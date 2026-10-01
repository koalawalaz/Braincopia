"""Downloading and parsing RSS feeds and Google News searches."""

import asyncio
import calendar
import html
import logging
import re
import time
from urllib.parse import parse_qsl, quote_plus, urlencode, urlsplit, urlunsplit

import aiohttp
import feedparser

from .db import Article, Database
from .sources import FEEDS, Feed
from .textnorm import KeywordRule, is_arabic

log = logging.getLogger(__name__)

USER_AGENT = "Mozilla/5.0 (compatible; MEAENewsBot/1.0; +https://t.me/)"
TIMEOUT = aiohttp.ClientTimeout(total=25)
MAX_SUMMARY = 1000

_TAGS = re.compile(r"<[^>]+>")
_TRACKING_PARAMS = ("utm_", "fbclid", "gclid", "ocid", "cmpid", "at_medium", "at_campaign")


def clean_html(text: str) -> str:
    text = html.unescape(_TAGS.sub(" ", text or ""))
    return re.sub(r"\s+", " ", text).strip()


def canonical_url(url: str) -> str:
    """Drop tracking parameters and #fragments so one article has one URL."""
    parts = urlsplit(url.strip())
    query = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
             if not k.lower().startswith(_TRACKING_PARAMS)]
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path, urlencode(query), ""))


def _entry_time(entry, now: int) -> int:
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if not parsed:
        return now
    return min(calendar.timegm(parsed), now)


def parse_feed(content: bytes, source: str, lang: str, country: str) -> list[Article]:
    parsed = feedparser.parse(content)
    now = int(time.time())
    articles = []
    for entry in parsed.entries:
        link = entry.get("link")
        title = clean_html(entry.get("title", ""))
        if not link or not title:
            continue
        summary = clean_html(entry.get("summary") or entry.get("description") or "")
        if summary == title:
            summary = ""
        articles.append(Article(
            url=canonical_url(link),
            title=title,
            summary=summary[:MAX_SUMMARY],
            source=source,
            lang=lang,
            country=country,
            published_at=_entry_time(entry, now),
        ))
    return articles


# ---------------------------------------------------------------- RSS feeds

class FeedFetcher:
    """Polls every feed in sources.FEEDS and stores what is new."""

    def __init__(self, db: Database, session: aiohttp.ClientSession, feeds: list[Feed] = FEEDS,
                 concurrency: int = 10):
        self.db = db
        self.session = session
        self.feeds = feeds
        self.semaphore = asyncio.Semaphore(concurrency)
        self.cycle = 0

    async def poll(self) -> list[Article]:
        """One pass over all feeds. Returns new articles that may be alerted."""
        self.cycle += 1
        results = await asyncio.gather(*(self._poll_feed(feed) for feed in self.feeds))
        return [article for batch in results for article in batch]

    async def _poll_feed(self, feed: Feed) -> list[Article]:
        state = await self.db.get_feed_state(feed.url)
        # A feed that keeps failing is only retried every 10th cycle (~30 min).
        if state and state["fail_count"] >= 5 and self.cycle % 10:
            return []
        headers = {"User-Agent": USER_AGENT}
        if state and state["etag"]:
            headers["If-None-Match"] = state["etag"]
        if state and state["last_modified"]:
            headers["If-Modified-Since"] = state["last_modified"]
        try:
            async with self.semaphore, self.session.get(feed.url, headers=headers, timeout=TIMEOUT) as resp:
                if resp.status == 304:
                    await self.db.feed_ok(feed.url, state["etag"], state["last_modified"])
                    return []
                if resp.status != 200:
                    raise RuntimeError(f"HTTP {resp.status}")
                content = await resp.read()
                etag, last_modified = resp.headers.get("ETag"), resp.headers.get("Last-Modified")
            articles = parse_feed(content, feed.name, feed.lang, feed.country)
            if not articles:
                raise RuntimeError("no articles in feed")
        except Exception as exc:  # network errors, bad XML, timeouts...
            await self.db.feed_failed(feed.url, f"{type(exc).__name__}: {exc}")
            log.debug("feed %s failed: %s", feed.name, exc)
            return []
        await self.db.feed_ok(feed.url, etag, last_modified)
        new = await self.db.store_articles(articles)
        if state is None or state["last_ok_at"] is None:
            # First successful read of this feed: everything in it is old news.
            # Keep it for search, but don't alert.
            return []
        return new


# -------------------------------------------------------------- Google News

GOOGLE_EDITIONS = {
    "en": {"hl": "en-US", "gl": "US", "ceid": "US:en"},
    "ar": {"hl": "ar", "gl": "EG", "ceid": "EG:ar"},
}


def google_queries(rule: KeywordRule) -> dict[str, str]:
    """One Google News search per language: {"en": '"Aramco"', "ar": '"أرامكو"'}."""
    by_lang: dict[str, list[str]] = {"en": [], "ar": []}
    for term in rule.terms:
        by_lang["ar" if is_arabic(term) else "en"].append(f'"{term}"')
    return {lang: " OR ".join(terms) for lang, terms in by_lang.items() if terms}


def google_news_url(query: str, lang: str) -> str:
    edition = GOOGLE_EDITIONS[lang]
    return (f"https://news.google.com/rss/search?q={quote_plus(query + ' when:1d')}"
            f"&hl={edition['hl']}&gl={edition['gl']}&ceid={edition['ceid']}")


def parse_google_news(content: bytes, lang: str) -> list[Article]:
    """Google titles look like "Headline - Source"; the summary is just links."""
    parsed = feedparser.parse(content)
    now = int(time.time())
    articles = []
    for entry in parsed.entries:
        link, title = entry.get("link"), clean_html(entry.get("title", ""))
        if not link or not title:
            continue
        source = clean_html((entry.get("source") or {}).get("title", "")) or "Google News"
        suffix = f" - {source}"
        if title.endswith(suffix):
            title = title[: -len(suffix)]
        articles.append(Article(
            url=link, title=title, summary="", source=source, lang=lang,
            country="INT", published_at=_entry_time(entry, now),
        ))
    return articles


class GoogleNewsFetcher:
    """Searches Google News for every keyword, which finds mentions in the
    body of articles and in outlets that are not in the RSS list."""

    def __init__(self, db: Database, session: aiohttp.ClientSession, concurrency: int = 3):
        self.db = db
        self.session = session
        self.semaphore = asyncio.Semaphore(concurrency)
        self.seen_queries: set[tuple[str, str]] = set()

    async def poll(self, rules: list[KeywordRule]) -> list[tuple[Article, set[int], bool]]:
        """Returns (article, ids of the keywords whose search found it, is_history).

        The first search for a keyword (or after a restart) returns the past
        day's news. Those results are marked as history: remembered so they
        are never alerted later, but not sent now.
        """
        searches: dict[tuple[str, str], set[int]] = {}
        for rule in rules:
            for lang, query in google_queries(rule).items():
                searches.setdefault((lang, query), set()).add(rule.id)
        results = await asyncio.gather(*(self._search(lang, query) for lang, query in searches))
        found: list[tuple[Article, set[int], bool]] = []
        for (key, keyword_ids), articles in zip(searches.items(), results):
            if articles is None:
                continue
            history = key not in self.seen_queries
            self.seen_queries.add(key)
            for article in articles:
                article.id, _ = await self.db.store_article(article)
                found.append((article, keyword_ids, history))
        await self.db.conn.commit()
        return found

    async def _search(self, lang: str, query: str) -> list[Article] | None:
        try:
            async with self.semaphore:
                async with self.session.get(google_news_url(query, lang),
                                            headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT) as resp:
                    if resp.status != 200:
                        raise RuntimeError(f"HTTP {resp.status}")
                    content = await resp.read()
                await asyncio.sleep(1)  # be gentle with Google
            return parse_google_news(content, lang)
        except Exception as exc:
            log.warning("Google News search %r failed: %s", query, exc)
            return None
