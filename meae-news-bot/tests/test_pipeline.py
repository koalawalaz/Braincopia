"""Storage, feed parsing and the alert pipeline, with a fake Telegram bot."""

import time

import pytest

from bot.config import Config
from bot.db import Article, Database
from bot.engine import Engine, format_alert, split_messages
from bot.fetcher import canonical_url, google_queries, parse_feed, parse_google_news
from bot.textnorm import KeywordRule

RSS = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel><title>Test</title>
<item><title>أرامكو تعلن نتائجها</title><link>https://example.com/a?utm_source=x&amp;id=1#top</link>
<description>&lt;p&gt;أعلنت شركة &lt;b&gt;أرامكو&lt;/b&gt; اليوم&lt;/p&gt;</description>
<pubDate>{time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime())}</pubDate></item>
<item><title>Weather today</title><link>https://example.com/b</link></item>
</channel></rss>""".encode()

GOOGLE = b"""<?xml version="1.0"?><rss version="2.0"><channel>
<item><title>Aramco signs deal - Reuters</title><link>https://news.google.com/rss/articles/xyz</link>
<source url="https://reuters.com">Reuters</source><description>&lt;a href="x"&gt;Aramco signs deal&lt;/a&gt;</description></item>
</channel></rss>"""


class FakeBot:
    def __init__(self):
        self.sent = []

    async def send_message(self, chat_id, text, **kwargs):
        self.sent.append((chat_id, text))


@pytest.fixture
async def db(tmp_path):
    database = Database(str(tmp_path / "test.db"))
    await database.connect()
    yield database
    await database.close()


def config(**overrides) -> Config:
    return Config(bot_token="x", admin_ids=frozenset(), **overrides)


def article(url="https://e.com/1", title="Aramco news", summary="", published_at=None) -> Article:
    return Article(url, title, summary, "Src", "en", "SA", published_at or int(time.time()))


def test_parse_feed_cleans_html_and_urls():
    items = parse_feed(RSS, "Test", "ar", "SA")
    assert len(items) == 2
    assert items[0].url == "https://example.com/a?id=1"
    assert items[0].summary == "أعلنت شركة أرامكو اليوم"
    assert items[1].summary == ""


def test_parse_google_news_strips_source_from_title():
    [item] = parse_google_news(GOOGLE, "en")
    assert item.title == "Aramco signs deal"
    assert item.source == "Reuters"


def test_google_queries_split_by_language():
    rule = KeywordRule(1, 1, "Aramco", variants=["أرامكو", "Saudi Aramco"])
    assert google_queries(rule) == {"en": '"Aramco" OR "Saudi Aramco"', "ar": '"أرامكو"'}


def test_canonical_url():
    assert canonical_url("HTTPS://Site.com/x?fbclid=1&a=2#f") == "https://site.com/x?a=2"


def test_split_messages():
    lines = ["x" * 1500] * 5
    messages = split_messages(lines)
    assert len(messages) == 3 and all(len(m) <= 4000 for m in messages)


def test_alert_escapes_html():
    text = format_alert("en", "A&B", article(title="<script> news"), "Asia/Riyadh")
    assert "&lt;script&gt;" in text and "A&amp;B" in text and "🇸🇦" in text


async def test_store_articles_dedupes(db):
    new = await db.store_articles([article(), article(), article(url="https://e.com/2")])
    assert [a.url for a in new] == ["https://e.com/1", "https://e.com/2"]
    assert await db.store_articles([article()]) == []


async def test_alert_flow(db):
    bot = FakeBot()
    await db.create_user(100, "ar")
    await db.create_user(200, "en")
    await db.add_keyword(100, "أرامكو", ["Aramco"], [])
    await db.add_keyword(200, "Aramco", [], ["stock"])
    engine = Engine(bot, db, config(), feeds=None, google=None)

    fresh = await db.store_articles([
        article("https://e.com/1", "Aramco opens plant"),
        article("https://e.com/2", "Aramco stock falls"),
        article("https://e.com/3", "Old Aramco story", published_at=int(time.time()) - 2 * 86400),
    ])
    assert await engine.process(fresh) == 3  # user 100: 1 and 2, user 200: only 1
    assert sorted(chat for chat, _ in bot.sent) == [100, 100, 200]
    assert "اقرأ المقال" in bot.sent[0][1]

    # Same article again: no second alert.
    assert await engine.process(fresh) == 0

    # The same story through Google News (different link) is not sent twice.
    google_copy = article("https://news.google.com/x", "Aramco opens plant")
    google_copy.id, _ = await db.store_article(google_copy)
    assert await engine.process([google_copy]) == 0

    # Google found it in the body text; RSS text alone would not match.
    body_only = article("https://news.google.com/y", "Energy giant expands")
    body_only.id, _ = await db.store_article(body_only)
    keyword_id = (await db.list_keywords(200))[0].id
    assert await engine.process([body_only], found_by={body_only.id: {keyword_id}}) == 1

    # History results are remembered but never sent.
    hist = article("https://news.google.com/z", "Earlier deal")
    hist.id, _ = await db.store_article(hist)
    assert await engine.process([hist], found_by={hist.id: {keyword_id}}, history={hist.id}) == 0
    assert await engine.process([hist], found_by={hist.id: {keyword_id}}) == 0


async def test_digest_mode_and_digest(db):
    bot = FakeBot()
    await db.create_user(100, "en")
    await db.update_user(100, mode="digest")
    await db.add_keyword(100, "Aramco", [], [])
    engine = Engine(bot, db, config(), feeds=None, google=None)
    fresh = await db.store_articles([article("https://e.com/1", "Aramco A"), article("https://e.com/2", "Aramco B")])
    assert await engine.process(fresh) == 0
    await engine.send_digest(await db.get_user(100))
    [(_, text)] = bot.sent
    assert "2 mentions" in text and "Aramco A" in text and "Aramco B" in text


def test_digest_due():
    from bot.db import User
    noon_utc = 1790000000 - (1790000000 % 86400) + 12 * 3600  # 12:00 UTC = 15:00 Riyadh
    user = User(1, "en", "digest", 15, "Asia/Riyadh", None, False)
    assert Engine._digest_due(user, noon_utc)
    user.last_digest_at = noon_utc - 60
    assert not Engine._digest_due(user, noon_utc)
    user.last_digest_at = noon_utc - 86400
    assert Engine._digest_due(user, noon_utc)
    user.digest_hour = 8
    assert not Engine._digest_due(user, noon_utc)


async def test_search(db):
    await db.store_articles([
        article("https://e.com/1", "تقرير", summary="قالت قناة للجزيرة"),
        article("https://e.com/2", "Nothing here"),
    ])
    found = await db.search_articles(KeywordRule(0, 0, "الجزيرة"), since=0)
    assert [a.url for a in found] == ["https://e.com/1"]
