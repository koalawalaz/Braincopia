"""Start the bot: python -m bot"""

import asyncio
import logging

import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, LinkPreviewOptions

from .config import load_config
from .db import Database
from .engine import Engine
from .fetcher import FeedFetcher, GoogleNewsFetcher
from .handlers import router
from .i18n import LANGUAGES, t

log = logging.getLogger("meae_news")

COMMANDS = {
    "en": [("start", "Start"), ("add", "Add a keyword"), ("list", "My keywords"),
           ("search", "Search recent news"), ("settings", "Settings"), ("help", "Help")],
    "ar": [("start", "البداية"), ("add", "إضافة كلمة"), ("list", "كلماتي"),
           ("search", "البحث في الأخبار"), ("settings", "الإعدادات"), ("help", "مساعدة")],
}


async def set_profile(bot: Bot) -> None:
    """The texts users see on the bot's profile and before pressing Start."""
    for lang in LANGUAGES:
        code = None if lang == "en" else lang  # English is the default for everyone else
        try:
            await bot.set_my_description(t(lang, "description"), language_code=code)
            await bot.set_my_short_description(t(lang, "short_description"), language_code=code)
            await bot.set_my_commands([BotCommand(command=c, description=d) for c, d in COMMANDS[lang]],
                                      language_code=code)
        except Exception as exc:  # rate limits here must not stop the bot
            log.warning("could not set the %s profile texts: %s", lang, exc)


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    config = load_config()
    db = Database(config.db_path, config.default_timezone)
    await db.connect()

    bot = Bot(config.bot_token, default=DefaultBotProperties(
        parse_mode="HTML", link_preview_options=LinkPreviewOptions(is_disabled=True)))
    dp = Dispatcher(storage=MemoryStorage(), db=db, config=config)
    dp.include_router(router)

    async with aiohttp.ClientSession() as session:
        google = GoogleNewsFetcher(db, session) if config.google_news_enabled else None
        engine = Engine(bot, db, config, FeedFetcher(db, session), google)
        await set_profile(bot)
        tasks = [asyncio.create_task(loop()) for loop in
                 (engine.rss_loop, engine.google_loop, engine.digest_loop, engine.maintenance_loop)]
        try:
            await dp.start_polling(bot)
        finally:
            for task in tasks:
                task.cancel()
            await db.close()
            await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
