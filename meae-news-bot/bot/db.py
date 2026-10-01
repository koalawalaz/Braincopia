"""SQLite storage: users, keywords, collected articles and sent matches."""

import json
import os
import time
from dataclasses import dataclass

import aiosqlite

from .textnorm import KeywordRule, normalize

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id        INTEGER PRIMARY KEY,
    lang           TEXT    NOT NULL DEFAULT 'en',
    mode           TEXT    NOT NULL DEFAULT 'instant',  -- instant | digest | both
    digest_hour    INTEGER NOT NULL DEFAULT 8,
    timezone       TEXT    NOT NULL,
    last_digest_at INTEGER,
    blocked        INTEGER NOT NULL DEFAULT 0,
    created_at     INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS keywords (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL REFERENCES users(user_id),
    name       TEXT    NOT NULL,
    variants   TEXT    NOT NULL DEFAULT '[]',
    excludes   TEXT    NOT NULL DEFAULT '[]',
    created_at INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS keywords_user ON keywords(user_id);
CREATE TABLE IF NOT EXISTS articles (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    url          TEXT    NOT NULL UNIQUE,
    title        TEXT    NOT NULL,
    summary      TEXT    NOT NULL DEFAULT '',
    source       TEXT    NOT NULL,
    lang         TEXT    NOT NULL,
    country      TEXT    NOT NULL,
    published_at INTEGER NOT NULL,
    fetched_at   INTEGER NOT NULL,
    norm         TEXT    NOT NULL,
    title_key    TEXT    NOT NULL
);
CREATE INDEX IF NOT EXISTS articles_published ON articles(published_at);
CREATE INDEX IF NOT EXISTS articles_title ON articles(title_key);
CREATE TABLE IF NOT EXISTS matches (
    user_id    INTEGER NOT NULL,
    article_id INTEGER NOT NULL,
    keyword_id INTEGER NOT NULL,
    matched_at INTEGER NOT NULL,
    PRIMARY KEY (user_id, article_id)
);
CREATE INDEX IF NOT EXISTS matches_user_time ON matches(user_id, matched_at);
CREATE TABLE IF NOT EXISTS feed_state (
    url           TEXT PRIMARY KEY,
    etag          TEXT,
    last_modified TEXT,
    last_ok_at    INTEGER,
    fail_count    INTEGER NOT NULL DEFAULT 0,
    last_error    TEXT
);
"""

USER_FIELDS = {"lang", "mode", "digest_hour", "timezone", "last_digest_at", "blocked"}


@dataclass
class Article:
    url: str
    title: str
    summary: str
    source: str
    lang: str
    country: str
    published_at: int
    id: int | None = None

    @property
    def norm(self) -> str:
        return normalize(f"{self.title}\n{self.summary}")

    @property
    def title_key(self) -> str:
        """Identifies the same story found via different links (site RSS vs Google News)."""
        return normalize(self.title)[:200]


@dataclass
class User:
    user_id: int
    lang: str
    mode: str
    digest_hour: int
    timezone: str
    last_digest_at: int | None
    blocked: bool


@dataclass
class Keyword:
    id: int
    user_id: int
    name: str
    variants: list[str]
    excludes: list[str]

    def rule(self) -> KeywordRule:
        return KeywordRule(self.id, self.user_id, self.name, self.variants, self.excludes)


def _keyword(row) -> Keyword:
    return Keyword(row["id"], row["user_id"], row["name"], json.loads(row["variants"]), json.loads(row["excludes"]))


def _article(row) -> Article:
    return Article(
        url=row["url"],
        title=row["title"],
        summary=row["summary"],
        source=row["source"],
        lang=row["lang"],
        country=row["country"],
        published_at=row["published_at"],
        id=row["id"],
    )


class Database:
    def __init__(self, path: str, default_timezone: str = "Asia/Riyadh"):
        self.path = path
        self.default_timezone = default_timezone
        self.conn: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        if self.path != ":memory:":
            os.makedirs(os.path.dirname(os.path.abspath(self.path)), exist_ok=True)
        self.conn = await aiosqlite.connect(self.path)
        self.conn.row_factory = aiosqlite.Row
        await self.conn.execute("PRAGMA journal_mode=WAL")
        await self.conn.executescript(SCHEMA)
        await self.conn.commit()

    async def close(self) -> None:
        if self.conn:
            await self.conn.close()

    # ------------------------------------------------------------- users

    async def get_user(self, user_id: int) -> User | None:
        async with self.conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cur:
            row = await cur.fetchone()
        if not row:
            return None
        return User(
            row["user_id"], row["lang"], row["mode"], row["digest_hour"],
            row["timezone"], row["last_digest_at"], bool(row["blocked"]),
        )

    async def create_user(self, user_id: int, lang: str) -> User:
        await self.conn.execute(
            "INSERT OR IGNORE INTO users (user_id, lang, timezone, created_at) VALUES (?, ?, ?, ?)",
            (user_id, lang, self.default_timezone, int(time.time())),
        )
        # A user who blocked the bot and came back is active again.
        await self.conn.execute("UPDATE users SET blocked = 0 WHERE user_id = ?", (user_id,))
        await self.conn.commit()
        return await self.get_user(user_id)

    async def update_user(self, user_id: int, **fields) -> None:
        unknown = set(fields) - USER_FIELDS
        if unknown:
            raise ValueError(f"unknown user fields: {unknown}")
        assignments = ", ".join(f"{name} = ?" for name in fields)
        await self.conn.execute(
            f"UPDATE users SET {assignments} WHERE user_id = ?", (*fields.values(), user_id)
        )
        await self.conn.commit()

    async def active_users(self) -> list[User]:
        async with self.conn.execute("SELECT user_id FROM users WHERE blocked = 0") as cur:
            ids = [row["user_id"] for row in await cur.fetchall()]
        return [await self.get_user(i) for i in ids]

    # ---------------------------------------------------------- keywords

    async def add_keyword(self, user_id: int, name: str, variants: list[str], excludes: list[str]) -> int:
        cur = await self.conn.execute(
            "INSERT INTO keywords (user_id, name, variants, excludes, created_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, name, json.dumps(variants, ensure_ascii=False),
             json.dumps(excludes, ensure_ascii=False), int(time.time())),
        )
        await self.conn.commit()
        return cur.lastrowid

    async def update_keyword(self, keyword_id: int, user_id: int, name: str,
                             variants: list[str], excludes: list[str]) -> None:
        await self.conn.execute(
            "UPDATE keywords SET name = ?, variants = ?, excludes = ? WHERE id = ? AND user_id = ?",
            (name, json.dumps(variants, ensure_ascii=False),
             json.dumps(excludes, ensure_ascii=False), keyword_id, user_id),
        )
        await self.conn.commit()

    async def delete_keyword(self, keyword_id: int, user_id: int) -> None:
        await self.conn.execute("DELETE FROM keywords WHERE id = ? AND user_id = ?", (keyword_id, user_id))
        await self.conn.commit()

    async def get_keyword(self, keyword_id: int, user_id: int) -> Keyword | None:
        async with self.conn.execute(
            "SELECT * FROM keywords WHERE id = ? AND user_id = ?", (keyword_id, user_id)
        ) as cur:
            row = await cur.fetchone()
        return _keyword(row) if row else None

    async def list_keywords(self, user_id: int) -> list[Keyword]:
        async with self.conn.execute(
            "SELECT * FROM keywords WHERE user_id = ? ORDER BY id", (user_id,)
        ) as cur:
            return [_keyword(row) for row in await cur.fetchall()]

    async def count_keywords(self, user_id: int) -> int:
        async with self.conn.execute("SELECT COUNT(*) FROM keywords WHERE user_id = ?", (user_id,)) as cur:
            return (await cur.fetchone())[0]

    async def active_keywords(self) -> list[Keyword]:
        """Keywords of every user who has not blocked the bot."""
        async with self.conn.execute(
            "SELECT k.* FROM keywords k JOIN users u ON u.user_id = k.user_id WHERE u.blocked = 0"
        ) as cur:
            return [_keyword(row) for row in await cur.fetchall()]

    # ---------------------------------------------------------- articles

    async def store_article(self, article: Article) -> tuple[int, bool]:
        """Save an article if its URL is new. Returns (article id, was_new)."""
        cur = await self.conn.execute(
            "INSERT OR IGNORE INTO articles "
            "(url, title, summary, source, lang, country, published_at, fetched_at, norm, title_key) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (article.url, article.title, article.summary, article.source, article.lang,
             article.country, article.published_at, int(time.time()), article.norm, article.title_key),
        )
        if cur.rowcount == 1:
            return cur.lastrowid, True
        async with self.conn.execute("SELECT id FROM articles WHERE url = ?", (article.url,)) as c:
            return (await c.fetchone())[0], False

    async def store_articles(self, articles: list[Article]) -> list[Article]:
        """Save articles; returns only the ones not seen before, with ids set."""
        new = []
        for article in articles:
            article.id, was_new = await self.store_article(article)
            if was_new:
                new.append(article)
        await self.conn.commit()
        return new

    async def search_articles(self, rule: KeywordRule, since: int, limit: int = 10) -> list[Article]:
        """Stored articles that match a keyword rule, newest first."""
        needles = set()
        for term in rule.terms:
            norm = normalize(term)
            # للجزيرة drops the alef of الجزيرة, so search for لجزيرة's core.
            needles.add(norm[2:] if norm.startswith("ال") and len(norm) > 3 else norm)
        # Cheap SQL pre-filter on the bare term, then the exact rule in Python.
        # Arabic prefixes (وأرامكو) still contain the term, so nothing is lost.
        where = " OR ".join("norm LIKE ?" for _ in needles)
        params = [f"%{n.replace('%', '').replace('_', '')}%" for n in needles]
        found: list[Article] = []
        async with self.conn.execute(
            f"SELECT * FROM articles WHERE published_at >= ? AND ({where}) ORDER BY published_at DESC",
            (since, *params),
        ) as cur:
            async for row in cur:
                if rule.matches(row["norm"]):
                    found.append(_article(row))
                    if len(found) >= limit:
                        break
        return found

    async def prune_articles(self, older_than: int) -> None:
        await self.conn.execute(
            "DELETE FROM matches WHERE article_id IN (SELECT id FROM articles WHERE published_at < ?)",
            (older_than,),
        )
        await self.conn.execute("DELETE FROM articles WHERE published_at < ?", (older_than,))
        await self.conn.commit()

    # ----------------------------------------------------------- matches

    async def record_match(self, user_id: int, article_id: int, keyword_id: int,
                           history: bool = False) -> bool:
        """True the first time an article is matched for a user (one alert per article).

        History matches (old news found when a keyword is first searched) are
        stored with matched_at = 0 so they never alert and stay out of digests.
        """
        cur = await self.conn.execute(
            "INSERT OR IGNORE INTO matches (user_id, article_id, keyword_id, matched_at) VALUES (?, ?, ?, ?)",
            (user_id, article_id, keyword_id, 0 if history else int(time.time())),
        )
        await self.conn.commit()
        return cur.rowcount == 1

    async def has_story(self, user_id: int, article: Article) -> bool:
        """Whether the user already has another article with the same headline."""
        async with self.conn.execute(
            "SELECT 1 FROM matches m JOIN articles a ON a.id = m.article_id "
            "WHERE m.user_id = ? AND a.title_key = ? AND a.id != ? LIMIT 1",
            (user_id, article.title_key, article.id),
        ) as cur:
            return await cur.fetchone() is not None

    async def matches_since(self, user_id: int, since: int) -> list[tuple[str, Article]]:
        """(keyword name, article) pairs matched for a user since a time."""
        async with self.conn.execute(
            "SELECT k.name AS keyword, a.* FROM matches m "
            "JOIN articles a ON a.id = m.article_id "
            "JOIN keywords k ON k.id = m.keyword_id "
            "WHERE m.user_id = ? AND m.matched_at >= ? ORDER BY k.name, a.published_at DESC",
            (user_id, since),
        ) as cur:
            return [(row["keyword"], _article(row)) for row in await cur.fetchall()]

    # -------------------------------------------------------- feed state

    async def get_feed_state(self, url: str) -> aiosqlite.Row | None:
        async with self.conn.execute("SELECT * FROM feed_state WHERE url = ?", (url,)) as cur:
            return await cur.fetchone()

    async def feed_ok(self, url: str, etag: str | None, last_modified: str | None) -> None:
        await self.conn.execute(
            "INSERT INTO feed_state (url, etag, last_modified, last_ok_at, fail_count, last_error) "
            "VALUES (?, ?, ?, ?, 0, NULL) ON CONFLICT(url) DO UPDATE SET "
            "etag = excluded.etag, last_modified = excluded.last_modified, "
            "last_ok_at = excluded.last_ok_at, fail_count = 0, last_error = NULL",
            (url, etag, last_modified, int(time.time())),
        )
        await self.conn.commit()

    async def feed_failed(self, url: str, error: str) -> None:
        await self.conn.execute(
            "INSERT INTO feed_state (url, fail_count, last_error) VALUES (?, 1, ?) "
            "ON CONFLICT(url) DO UPDATE SET fail_count = fail_count + 1, last_error = excluded.last_error",
            (url, error[:300]),
        )
        await self.conn.commit()

    async def failing_feeds(self) -> list[aiosqlite.Row]:
        async with self.conn.execute(
            "SELECT * FROM feed_state WHERE fail_count > 0 ORDER BY fail_count DESC"
        ) as cur:
            return await cur.fetchall()

    # ------------------------------------------------------------- stats

    async def stats(self) -> dict[str, int]:
        day_ago = int(time.time()) - 86400
        queries = {
            "users": ("SELECT COUNT(*) FROM users WHERE blocked = 0", ()),
            "blocked": ("SELECT COUNT(*) FROM users WHERE blocked = 1", ()),
            "keywords": ("SELECT COUNT(*) FROM keywords", ()),
            "articles": ("SELECT COUNT(*) FROM articles", ()),
            "articles_24h": ("SELECT COUNT(*) FROM articles WHERE fetched_at >= ?", (day_ago,)),
            "alerts_24h": ("SELECT COUNT(*) FROM matches WHERE matched_at >= ?", (day_ago,)),
        }
        result = {}
        for name, (sql, params) in queries.items():
            async with self.conn.execute(sql, params) as cur:
                result[name] = (await cur.fetchone())[0]
        return result
