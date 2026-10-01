"""The RSS poller against a local web server."""

import time

import aiohttp
from aiohttp import web

from bot.db import Database
from bot.fetcher import FeedFetcher
from bot.sources import Feed


def rss(*titles: str) -> str:
    now = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
    items = "".join(f"<item><title>{t}</title><link>https://e.com/{i}</link><pubDate>{now}</pubDate></item>"
                    for i, t in enumerate(titles))
    return f'<?xml version="1.0"?><rss version="2.0"><channel><title>x</title>{items}</channel></rss>'


async def test_first_read_is_history_then_new_items_alert(tmp_path):
    content = {"body": rss("Old story")}

    async def feed(request):
        return web.Response(text=content["body"], content_type="application/rss+xml")

    async def broken(request):
        return web.Response(status=500)

    app = web.Application()
    app.router.add_get("/feed", feed)
    app.router.add_get("/broken", broken)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    port = site._server.sockets[0].getsockname()[1]

    db = Database(str(tmp_path / "t.db"))
    await db.connect()
    feeds = [Feed("Good", f"http://127.0.0.1:{port}/feed", "en", "SA"),
             Feed("Bad", f"http://127.0.0.1:{port}/broken", "en", "SA")]
    try:
        async with aiohttp.ClientSession() as session:
            fetcher = FeedFetcher(db, session, feeds)
            assert await fetcher.poll() == []  # first read: stored, not alerted
            content["body"] = rss("Old story", "Breaking story")
            new = await fetcher.poll()
            assert [a.title for a in new] == ["Breaking story"]
            assert await fetcher.poll() == []
        [failing] = await db.failing_feeds()
        assert failing["fail_count"] == 3 and "500" in failing["last_error"]
    finally:
        await db.close()
        await runner.cleanup()
