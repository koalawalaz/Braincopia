"""Check which news feeds work: python -m bot.check_feeds

Run this on the server once after setup (and now and then) and fix or
remove the broken entries in bot/sources.py.
"""

import asyncio
import sys

import aiohttp

from .fetcher import TIMEOUT, USER_AGENT, parse_feed
from .sources import FEEDS, Feed


async def check(session: aiohttp.ClientSession, semaphore: asyncio.Semaphore, feed: Feed) -> tuple[Feed, str | None, int]:
    try:
        async with semaphore, session.get(feed.url, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT) as resp:
            if resp.status != 200:
                return feed, f"HTTP {resp.status}", 0
            articles = parse_feed(await resp.read(), feed.name, feed.lang, feed.country)
        return feed, None if articles else "no articles (not an RSS feed?)", len(articles)
    except Exception as exc:
        return feed, f"{type(exc).__name__}: {exc}", 0


async def main() -> int:
    semaphore = asyncio.Semaphore(10)
    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(*(check(session, semaphore, feed) for feed in FEEDS))
    broken = [r for r in results if r[1]]
    for feed, error, count in results:
        status = f"OK  {count:3d} articles" if not error else f"BROKEN  {error}"
        print(f"{feed.country:4} {feed.name[:40]:40} {status}")
    print(f"\n{len(results) - len(broken)} of {len(results)} feeds work.")
    if broken:
        print("\nBroken feed URLs (fix or remove them in bot/sources.py):")
        for feed, error, _ in broken:
            print(f"  {feed.name}: {feed.url}")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
