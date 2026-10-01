"""Drive the real handlers through aiogram with a fake Telegram connection."""

import datetime as dt
import itertools

import pytest
from aiogram import Bot, Dispatcher
from aiogram.client.session.base import BaseSession
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.methods import AnswerCallbackQuery, EditMessageText, SendMessage, TelegramMethod
from aiogram.types import CallbackQuery, Chat, Message, Update, User

from bot.config import Config
from bot.db import Database
from bot.handlers import router

USER_ID = 42
ids = itertools.count(1)


class FakeSession(BaseSession):
    def __init__(self):
        super().__init__()
        self.calls: list[TelegramMethod] = []

    async def make_request(self, bot, method, timeout=None):
        self.calls.append(method)
        if isinstance(method, (SendMessage, EditMessageText)):
            return Message(message_id=next(ids), date=dt.datetime.now(), text=method.text,
                           chat=Chat(id=USER_ID, type="private"))
        return True

    async def stream_content(self, *args, **kwargs):
        yield b""

    async def close(self):
        pass

    def texts(self) -> list[str]:
        return [c.text for c in self.calls if isinstance(c, (SendMessage, EditMessageText))]


@pytest.fixture
async def env(tmp_path):
    db = Database(str(tmp_path / "t.db"))
    await db.connect()
    session = FakeSession()
    bot = Bot("42:TEST", session=session)
    dp = Dispatcher(storage=MemoryStorage(), db=db, config=Config(bot_token="x", admin_ids=frozenset({USER_ID})))
    dp.include_router(router)
    yield dp, bot, session, db
    router._parent_router = None  # the module-level router is reused by the next test
    await db.close()


def tg_user(lang="en"):
    return User(id=USER_ID, is_bot=False, first_name="Test", language_code=lang)


async def say(env, text, lang="en"):
    dp, bot, session, _ = env
    session.calls.clear()
    message = Message(message_id=next(ids), date=dt.datetime.now(), text=text,
                      chat=Chat(id=USER_ID, type="private"), from_user=tg_user(lang))
    await dp.feed_update(bot, Update(update_id=next(ids), message=message))
    return session.texts()


async def press(env, data, lang="en"):
    dp, bot, session, _ = env
    session.calls.clear()
    message = Message(message_id=1, date=dt.datetime.now(), text="x", chat=Chat(id=USER_ID, type="private"))
    callback = CallbackQuery(id=str(next(ids)), from_user=tg_user(lang), chat_instance="c",
                             data=data, message=message)
    await dp.feed_update(bot, Update(update_id=next(ids), callback_query=callback))
    assert any(isinstance(c, AnswerCallbackQuery) for c in session.calls), "callback not answered"
    return session.texts()


async def test_arabic_user_full_flow(env):
    _, _, _, db = env
    texts = await say(env, "/start", lang="ar")
    assert "رصد فوري" in texts[0] and "اختر لغتك" in texts[1]

    texts = await say(env, "➕ إضافة كلمة", lang="ar")
    assert "أرسل الاسم" in texts[0]
    texts = await say(env, "أرامكو, Aramco, -أسهم", lang="ar")
    assert "تتم الآن متابعة" in texts[0] and "Aramco" in texts[0]

    [keyword] = await db.list_keywords(USER_ID)
    assert keyword.variants == ["Aramco"] and keyword.excludes == ["أسهم"]

    texts = await say(env, "📋 كلماتي", lang="ar")
    assert "(1/10)" in texts[0]
    texts = await press(env, f"kw:{keyword.id}", lang="ar")
    assert "كلمات مستبعدة: أسهم" in texts[0]

    await press(env, f"kwedit:{keyword.id}", lang="ar")
    texts = await say(env, "أرامكو, Saudi Aramco", lang="ar")
    assert "تم تحديث" in texts[0]
    assert (await db.list_keywords(USER_ID))[0].variants == ["Saudi Aramco"]

    texts = await press(env, f"kwrecent:{keyword.id}", lang="ar")
    assert "لا توجد إشارات" in texts[0]

    await press(env, f"kwdelok:{keyword.id}", lang="ar")
    assert await db.list_keywords(USER_ID) == []


async def test_language_and_settings(env):
    _, _, _, db = env
    await say(env, "/start")
    await press(env, "lang:ar")
    assert (await db.get_user(USER_ID)).lang == "ar"
    await press(env, "lang:en")

    texts = await press(env, "set:mode")
    assert "How do you want" in texts[0]
    await press(env, "mode:both")
    await press(env, "hour:21")
    await press(env, "tz:9")  # Yangon
    user = await db.get_user(USER_ID)
    assert (user.mode, user.digest_hour, user.timezone) == ("both", 21, "Asia/Yangon")
    texts = await say(env, "⚙️ Settings")
    assert "21:00" in texts[0] and "Yangon" in texts[0]


async def test_add_command_errors_and_limit(env):
    _, _, _, db = env
    await say(env, "/start")
    texts = await say(env, "/add -only")
    assert "send a name" in texts[0]
    for i in range(10):
        await say(env, f"/add Company{i}")
    texts = await say(env, "/add One more")
    assert "maximum" in texts[0]
    assert await db.count_keywords(USER_ID) == 10


async def test_menu_button_leaves_a_pending_step(env):
    await say(env, "/start")
    await say(env, "➕ Add keyword")
    texts = await say(env, "⚙️ Settings")
    assert "Settings" in texts[0]
    texts = await say(env, "Aramco")  # no longer waiting for a keyword
    assert "Use the menu" in texts[0]


async def test_admin_stats(env):
    await say(env, "/start")
    texts = await say(env, "/stats")
    assert "Users: 1" in texts[0]
    texts = await say(env, "/feeds")
    assert "All feeds are working" in texts[0]
