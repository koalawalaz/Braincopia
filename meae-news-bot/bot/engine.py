"""The background work: polling sources, matching keywords, sending alerts
and daily digests, and cleaning up old data."""

import asyncio
import datetime as dt
import html
import logging
import time
from zoneinfo import ZoneInfo

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter
from aiogram.types import LinkPreviewOptions

from .config import Config
from .db import Article, Database, User
from .fetcher import FeedFetcher, GoogleNewsFetcher
from .i18n import t
from .sources import flag
from .textnorm import KeywordRule

log = logging.getLogger(__name__)

MAX_MESSAGE = 4000  # Telegram's limit is 4096 characters
DIGEST_MAX_ITEMS = 40


def snippet(article: Article, length: int = 280) -> str:
    text = article.summary
    if len(text) > length:
        text = text[:length].rsplit(" ", 1)[0] + "…"
    return text


def format_time(timestamp: int, timezone: str) -> str:
    try:
        zone = ZoneInfo(timezone)
    except Exception:
        zone = ZoneInfo("UTC")
    return dt.datetime.fromtimestamp(timestamp, zone).strftime("%d.%m.%Y %H:%M")


def format_alert(lang: str, keyword: str, article: Article, timezone: str) -> str:
    lines = [f"🔔 <b>{html.escape(keyword)}</b>", "", f"<b>{html.escape(article.title)}</b>"]
    if article.summary:
        lines.append(html.escape(snippet(article)))
    lines += [
        "",
        f"{flag(article.country)} {html.escape(article.source)} · {format_time(article.published_at, timezone)}",
        f'<a href="{html.escape(article.url, quote=True)}">{t(lang, "alert_read")} →</a>',
    ]
    return "\n".join(lines)


def format_article_line(article: Article, timezone: str) -> str:
    """One compact line for search results and digests."""
    title = html.escape(article.title)
    url = html.escape(article.url, quote=True)
    when = format_time(article.published_at, timezone)
    return f'• <a href="{url}">{title}</a>\n   <i>{html.escape(article.source)} · {when}</i>'


def split_messages(lines: list[str]) -> list[str]:
    """Join lines into as few messages as possible under Telegram's size limit."""
    messages, current = [], ""
    for line in lines:
        if current and len(current) + len(line) + 1 > MAX_MESSAGE:
            messages.append(current)
            current = ""
        current = f"{current}\n{line}" if current else line
    if current:
        messages.append(current)
    return messages


async def send(bot: Bot, db: Database, user_id: int, text: str, **kwargs) -> bool:
    """Send a message; marks the user as blocked if they blocked the bot."""
    kwargs.setdefault("link_preview_options", LinkPreviewOptions(is_disabled=True))
    for _ in range(3):
        try:
            await bot.send_message(user_id, text, **kwargs)
            await asyncio.sleep(0.04)  # stay well under Telegram's 30 messages/second
            return True
        except TelegramRetryAfter as exc:
            await asyncio.sleep(exc.retry_after + 1)
        except TelegramForbiddenError:
            await db.update_user(user_id, blocked=1)
            return False
        except Exception:
            log.exception("could not send to %s", user_id)
            return False
    return False


class Engine:
    def __init__(self, bot: Bot, db: Database, config: Config,
                 feeds: FeedFetcher, google: GoogleNewsFetcher | None):
        self.bot = bot
        self.db = db
        self.config = config
        self.feeds = feeds
        self.google = google

    # ------------------------------------------------------------ matching

    async def _rules_by_user(self) -> tuple[list[KeywordRule], dict[int, User]]:
        rules = [k.rule() for k in await self.db.active_keywords()]
        users = {u.user_id: u for u in await self.db.active_users()}
        return [r for r in rules if r.user_id in users], users

    async def process(self, articles: list[Article],
                      found_by: dict[int, set[int]] | None = None,
                      history: set[int] | None = None) -> int:
        """Match articles against every keyword and alert users. Returns alerts sent.

        found_by maps an article id to keyword ids whose Google search returned
        it: Google matched the full article text, so only excluded words are
        checked. Articles in `history` are remembered but never alerted.
        """
        found_by = found_by or {}
        history = history or set()
        rules, users = await self._rules_by_user()
        oldest = int(time.time()) - self.config.max_article_age_hours * 3600
        sent = 0
        for article in articles:
            norm = article.norm
            is_history = article.id in history or article.published_at < oldest
            google_ids = found_by.get(article.id, set())
            for user_id, rule in self._first_match_per_user(rules, norm, google_ids):
                # The same story already sent via another link counts as history.
                duplicate = await self.db.has_story(user_id, article)
                if not await self.db.record_match(user_id, article.id, rule.id,
                                                  history=is_history or duplicate):
                    continue  # this user already has this article
                user = users[user_id]
                if is_history or duplicate or user.mode == "digest":
                    continue
                text = format_alert(user.lang, rule.name, article, user.timezone)
                preview = LinkPreviewOptions(url=article.url, prefer_small_media=True)
                if await send(self.bot, self.db, user_id, text, link_preview_options=preview):
                    sent += 1
        return sent

    @staticmethod
    def _first_match_per_user(rules: list[KeywordRule], norm: str, google_ids: set[int]):
        done: set[int] = set()
        for rule in rules:
            if rule.user_id in done:
                continue
            if rule.matches(norm) or (rule.id in google_ids and not rule.is_excluded(norm)):
                done.add(rule.user_id)
                yield rule.user_id, rule

    # --------------------------------------------------------------- loops

    async def rss_loop(self) -> None:
        while True:
            started = time.monotonic()
            try:
                new = await self.feeds.poll()
                sent = await self.process(new)
                log.info("RSS: %d new articles, %d alerts (%.0fs)", len(new), sent, time.monotonic() - started)
            except Exception:
                log.exception("RSS cycle failed")
            await asyncio.sleep(max(10, self.config.poll_interval - (time.monotonic() - started)))

    async def google_loop(self) -> None:
        if not self.google:
            return
        await asyncio.sleep(30)  # let the first RSS pass go first
        while True:
            started = time.monotonic()
            try:
                rules, _ = await self._rules_by_user()
                results = await self.google.poll(rules)
                articles: dict[int, Article] = {}
                found_by: dict[int, set[int]] = {}
                history: set[int] = set()
                for article, keyword_ids, is_history in results:
                    articles[article.id] = article
                    found_by.setdefault(article.id, set()).update(keyword_ids)
                    if is_history:
                        history.add(article.id)
                sent = await self.process(list(articles.values()), found_by, history)
                log.info("Google News: %d results, %d alerts", len(results), sent)
            except Exception:
                log.exception("Google News cycle failed")
            await asyncio.sleep(max(60, self.config.google_news_interval - (time.monotonic() - started)))

    async def digest_loop(self) -> None:
        while True:
            try:
                for user in await self.db.active_users():
                    if user.mode in ("digest", "both") and self._digest_due(user):
                        await self.send_digest(user)
            except Exception:
                log.exception("digest cycle failed")
            await asyncio.sleep(60)

    @staticmethod
    def _digest_due(user: User, now: float | None = None) -> bool:
        now = time.time() if now is None else now
        try:
            zone = ZoneInfo(user.timezone)
        except Exception:
            zone = ZoneInfo("UTC")
        local = dt.datetime.fromtimestamp(now, zone)
        if local.hour != user.digest_hour:
            return False
        if user.last_digest_at is None:
            return True
        return dt.datetime.fromtimestamp(user.last_digest_at, zone).date() != local.date()

    async def send_digest(self, user: User) -> None:
        now = int(time.time())
        since = max(user.last_digest_at or 0, now - 86400)
        await self.db.update_user(user.user_id, last_digest_at=now)
        items = await self.db.matches_since(user.user_id, since)
        if not items:
            await send(self.bot, self.db, user.user_id, t(user.lang, "digest_empty"))
            return
        lines = [t(user.lang, "digest_header", count=len(items))]
        current_keyword = None
        for keyword, article in items[:DIGEST_MAX_ITEMS]:
            if keyword != current_keyword:
                lines.append(f"\n🔔 <b>{html.escape(keyword)}</b>")
                current_keyword = keyword
            lines.append(format_article_line(article, user.timezone))
        if len(items) > DIGEST_MAX_ITEMS:
            lines.append("\n" + t(user.lang, "digest_more", count=len(items) - DIGEST_MAX_ITEMS))
        for message in split_messages(lines):
            if not await send(self.bot, self.db, user.user_id, message):
                return

    async def maintenance_loop(self) -> None:
        while True:
            try:
                await self.db.prune_articles(int(time.time()) - self.config.retention_days * 86400)
            except Exception:
                log.exception("maintenance failed")
            await asyncio.sleep(6 * 3600)
