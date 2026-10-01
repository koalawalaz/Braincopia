"""Everything the user can do in the chat: menus, keywords, search, settings,
and admin commands."""

import asyncio
import html
import time

from aiogram import F, Router
from aiogram.filters import Command, CommandObject, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, KeyboardButton, Message, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from .config import Config
from .db import Database, Keyword, User
from .engine import format_article_line, send
from .i18n import LANGUAGE_NAMES, LANGUAGES, TIMEZONES, language_for, menu_action, t
from .sources import FEEDS
from .textnorm import KeywordInputError, KeywordRule, format_keyword_input, parse_keyword_input

router = Router()

SEARCH_LIMIT = 10


class Form(StatesGroup):
    add_keyword = State()
    edit_keyword = State()
    search = State()


# ------------------------------------------------------------------ helpers

def main_menu(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(lang, "menu_add")), KeyboardButton(text=t(lang, "menu_list"))],
            [KeyboardButton(text=t(lang, "menu_search")), KeyboardButton(text=t(lang, "menu_settings"))],
            [KeyboardButton(text=t(lang, "menu_help"))],
        ],
        resize_keyboard=True,
    )


def language_keyboard():
    kb = InlineKeyboardBuilder()
    for code in LANGUAGES:
        kb.button(text=LANGUAGE_NAMES[code], callback_data=f"lang:{code}")
    return kb.as_markup()


def keyword_details(lang: str, keyword: Keyword) -> str:
    def joined(items: list[str]) -> str:
        return ", ".join(html.escape(i) for i in items) if items else t(lang, "none")

    return (f"{t(lang, 'label_variants')}: {joined(keyword.variants)}\n"
            f"{t(lang, 'label_excludes')}: {joined(keyword.excludes)}")


def counts(config: Config) -> dict:
    return {"sources": len(FEEDS), "max": config.max_keywords}


async def get_or_create_user(db: Database, tg_user) -> User:
    user = await db.get_user(tg_user.id)
    if user is None or user.blocked:
        user = await db.create_user(tg_user.id, user.lang if user else language_for(tg_user.language_code))
    return user


# -------------------------------------------------------------- start/help

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, db: Database, config: Config):
    await state.clear()
    is_new = await db.get_user(message.from_user.id) is None
    user = await get_or_create_user(db, message.from_user)
    await message.answer(t(user.lang, "welcome", **counts(config)), reply_markup=main_menu(user.lang))
    if is_new:
        await message.answer(t(user.lang, "choose_lang"), reply_markup=language_keyboard())


@router.message(Command("help"))
async def cmd_help(message: Message, db: Database, config: Config):
    user = await get_or_create_user(db, message.from_user)
    await message.answer(t(user.lang, "help", **counts(config)), reply_markup=main_menu(user.lang))


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext, db: Database):
    user = await get_or_create_user(db, message.from_user)
    await state.clear()
    await message.answer(t(user.lang, "cancelled"), reply_markup=main_menu(user.lang))


@router.callback_query(F.data.startswith("lang:"))
async def cb_language(callback: CallbackQuery, db: Database):
    lang = callback.data.split(":", 1)[1]
    if lang not in LANGUAGES:
        return await callback.answer()
    await get_or_create_user(db, callback.from_user)
    await db.update_user(callback.from_user.id, lang=lang)
    await callback.message.edit_text(t(lang, "lang_set"))
    await callback.message.answer(t(lang, "use_menu"), reply_markup=main_menu(lang))
    await callback.answer()


# ---------------------------------------------------------------- keywords

async def start_add(message: Message, state: FSMContext, db: Database, config: Config, user: User):
    if await db.count_keywords(user.user_id) >= config.max_keywords:
        await message.answer(t(user.lang, "limit_reached", max=config.max_keywords))
        return
    await state.set_state(Form.add_keyword)
    await message.answer(t(user.lang, "add_prompt"))


async def save_new_keyword(message: Message, text: str, state: FSMContext,
                           db: Database, config: Config, user: User):
    if await db.count_keywords(user.user_id) >= config.max_keywords:
        await state.clear()
        await message.answer(t(user.lang, "limit_reached", max=config.max_keywords))
        return
    try:
        parsed = parse_keyword_input(text)
    except KeywordInputError as err:
        await message.answer(t(user.lang, err.code))
        return  # stay in the same step so the user can retry
    keyword_id = await db.add_keyword(user.user_id, parsed.name, parsed.variants, parsed.excludes)
    await state.clear()
    keyword = await db.get_keyword(keyword_id, user.user_id)
    await message.answer(
        t(user.lang, "add_ok", name=html.escape(keyword.name), details=keyword_details(user.lang, keyword)),
        reply_markup=main_menu(user.lang),
    )


@router.message(Command("add"))
async def cmd_add(message: Message, command: CommandObject, state: FSMContext, db: Database, config: Config):
    user = await get_or_create_user(db, message.from_user)
    if command.args:
        await save_new_keyword(message, command.args, state, db, config, user)
    else:
        await start_add(message, state, db, config, user)


@router.message(Form.add_keyword, F.text, ~F.text.startswith("/"), F.func(lambda m: not menu_action(m.text)))
async def on_add_keyword(message: Message, state: FSMContext, db: Database, config: Config):
    user = await get_or_create_user(db, message.from_user)
    await save_new_keyword(message, message.text, state, db, config, user)


async def show_list(target: Message, db: Database, config: Config, user: User, edit: bool = False):
    keywords = await db.list_keywords(user.user_id)
    if not keywords:
        text, markup = t(user.lang, "list_empty"), None
    else:
        text = t(user.lang, "list_header", count=len(keywords), max=config.max_keywords)
        kb = InlineKeyboardBuilder()
        for keyword in keywords:
            kb.button(text=keyword.name, callback_data=f"kw:{keyword.id}")
        kb.adjust(1)
        markup = kb.as_markup()
    if edit:
        await target.edit_text(text, reply_markup=markup)
    else:
        await target.answer(text, reply_markup=markup)


@router.message(Command("list"))
async def cmd_list(message: Message, state: FSMContext, db: Database, config: Config):
    await state.clear()
    user = await get_or_create_user(db, message.from_user)
    await show_list(message, db, config, user)


def keyword_keyboard(lang: str, keyword_id: int):
    kb = InlineKeyboardBuilder()
    kb.button(text=t(lang, "btn_recent"), callback_data=f"kwrecent:{keyword_id}")
    kb.button(text=t(lang, "btn_edit"), callback_data=f"kwedit:{keyword_id}")
    kb.button(text=t(lang, "btn_delete"), callback_data=f"kwdel:{keyword_id}")
    kb.button(text=t(lang, "btn_back"), callback_data="kwlist")
    kb.adjust(1, 2, 1)
    return kb.as_markup()


async def callback_keyword(callback: CallbackQuery, db: Database) -> tuple[User, Keyword | None]:
    user = await get_or_create_user(db, callback.from_user)
    keyword_id = int(callback.data.split(":", 1)[1])
    keyword = await db.get_keyword(keyword_id, user.user_id)
    if keyword is None:
        await callback.answer(t(user.lang, "not_found"), show_alert=True)
    return user, keyword


@router.callback_query(F.data == "kwlist")
async def cb_list(callback: CallbackQuery, db: Database, config: Config):
    user = await get_or_create_user(db, callback.from_user)
    await show_list(callback.message, db, config, user, edit=True)
    await callback.answer()


@router.callback_query(F.data.startswith("kw:"))
async def cb_keyword(callback: CallbackQuery, db: Database):
    user, keyword = await callback_keyword(callback, db)
    if keyword is None:
        return
    await callback.message.edit_text(
        t(user.lang, "kw_detail", name=html.escape(keyword.name), details=keyword_details(user.lang, keyword)),
        reply_markup=keyword_keyboard(user.lang, keyword.id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("kwdel:"))
async def cb_delete(callback: CallbackQuery, db: Database):
    user, keyword = await callback_keyword(callback, db)
    if keyword is None:
        return
    kb = InlineKeyboardBuilder()
    kb.button(text=t(user.lang, "btn_confirm_delete"), callback_data=f"kwdelok:{keyword.id}")
    kb.button(text=t(user.lang, "btn_cancel"), callback_data=f"kw:{keyword.id}")
    await callback.message.edit_text(t(user.lang, "confirm_delete", name=html.escape(keyword.name)),
                                     reply_markup=kb.as_markup())
    await callback.answer()


@router.callback_query(F.data.startswith("kwdelok:"))
async def cb_delete_confirmed(callback: CallbackQuery, db: Database):
    user, keyword = await callback_keyword(callback, db)
    if keyword is None:
        return
    await db.delete_keyword(keyword.id, user.user_id)
    kb = InlineKeyboardBuilder()
    kb.button(text=t(user.lang, "btn_back"), callback_data="kwlist")
    await callback.message.edit_text(t(user.lang, "deleted", name=html.escape(keyword.name)),
                                     reply_markup=kb.as_markup())
    await callback.answer()


@router.callback_query(F.data.startswith("kwedit:"))
async def cb_edit(callback: CallbackQuery, state: FSMContext, db: Database):
    user, keyword = await callback_keyword(callback, db)
    if keyword is None:
        return
    await state.set_state(Form.edit_keyword)
    await state.update_data(keyword_id=keyword.id)
    current = format_keyword_input(keyword.name, keyword.variants, keyword.excludes)
    await callback.message.answer(t(user.lang, "edit_prompt", current=html.escape(current)))
    await callback.answer()


@router.message(Form.edit_keyword, F.text, ~F.text.startswith("/"), F.func(lambda m: not menu_action(m.text)))
async def on_edit_keyword(message: Message, state: FSMContext, db: Database):
    user = await get_or_create_user(db, message.from_user)
    keyword_id = (await state.get_data()).get("keyword_id")
    keyword = await db.get_keyword(keyword_id, user.user_id) if keyword_id else None
    if keyword is None:
        await state.clear()
        await message.answer(t(user.lang, "not_found"), reply_markup=main_menu(user.lang))
        return
    try:
        parsed = parse_keyword_input(message.text)
    except KeywordInputError as err:
        await message.answer(t(user.lang, err.code))
        return
    await db.update_keyword(keyword.id, user.user_id, parsed.name, parsed.variants, parsed.excludes)
    await state.clear()
    keyword = await db.get_keyword(keyword.id, user.user_id)
    await message.answer(
        t(user.lang, "edited", name=html.escape(keyword.name), details=keyword_details(user.lang, keyword)),
        reply_markup=main_menu(user.lang),
    )


# ------------------------------------------------------------------ search

async def run_search(message: Message, rule: KeywordRule, query: str, db: Database, config: Config, user: User):
    since = int(time.time()) - config.retention_days * 86400
    articles = await db.search_articles(rule, since, SEARCH_LIMIT)
    query = html.escape(query)
    if not articles:
        await message.answer(t(user.lang, "search_none", query=query, days=config.retention_days))
        return
    lines = [t(user.lang, "search_header", query=query, count=len(articles), days=config.retention_days), ""]
    lines += [format_article_line(a, user.timezone) for a in articles]
    await send(message.bot, db, user.user_id, "\n".join(lines))


async def search_text(message: Message, text: str, state: FSMContext, db: Database, config: Config, user: User):
    try:
        parsed = parse_keyword_input(text)
    except KeywordInputError as err:
        await message.answer(t(user.lang, err.code))
        return
    await state.clear()
    rule = KeywordRule(0, user.user_id, parsed.name, parsed.variants, parsed.excludes)
    await run_search(message, rule, parsed.name, db, config, user)


@router.message(Command("search"))
async def cmd_search(message: Message, command: CommandObject, state: FSMContext, db: Database, config: Config):
    user = await get_or_create_user(db, message.from_user)
    if command.args:
        await search_text(message, command.args, state, db, config, user)
    else:
        await state.set_state(Form.search)
        await message.answer(t(user.lang, "search_prompt"))


@router.message(Form.search, F.text, ~F.text.startswith("/"), F.func(lambda m: not menu_action(m.text)))
async def on_search(message: Message, state: FSMContext, db: Database, config: Config):
    user = await get_or_create_user(db, message.from_user)
    await search_text(message, message.text, state, db, config, user)


@router.callback_query(F.data.startswith("kwrecent:"))
async def cb_recent(callback: CallbackQuery, db: Database, config: Config):
    user, keyword = await callback_keyword(callback, db)
    if keyword is None:
        return
    await callback.answer()
    await run_search(callback.message, keyword.rule(), keyword.name, db, config, user)


# ---------------------------------------------------------------- settings

async def show_settings(target: Message, user: User, edit: bool = False):
    tz_label = next((label for name, label in TIMEZONES if name == user.timezone), user.timezone)
    text = t(user.lang, "settings_header", language=LANGUAGE_NAMES[user.lang],
             mode=t(user.lang, f"mode_{user.mode}"), hour=f"{user.digest_hour:02d}",
             timezone=html.escape(tz_label))
    kb = InlineKeyboardBuilder()
    for key, data in (("btn_set_lang", "set:lang"), ("btn_set_mode", "set:mode"),
                      ("btn_set_hour", "set:hour"), ("btn_set_tz", "set:tz")):
        kb.button(text=t(user.lang, key), callback_data=data)
    kb.adjust(2)
    if edit:
        await target.edit_text(text, reply_markup=kb.as_markup())
    else:
        await target.answer(text, reply_markup=kb.as_markup())


@router.message(Command("settings"))
async def cmd_settings(message: Message, state: FSMContext, db: Database):
    await state.clear()
    user = await get_or_create_user(db, message.from_user)
    await show_settings(message, user)


@router.callback_query(F.data.startswith("set:"))
async def cb_settings(callback: CallbackQuery, db: Database):
    user = await get_or_create_user(db, callback.from_user)
    what = callback.data.split(":", 1)[1]
    kb = InlineKeyboardBuilder()
    if what == "lang":
        await callback.message.edit_text(t(user.lang, "choose_lang"), reply_markup=language_keyboard())
        return await callback.answer()
    if what == "mode":
        for mode in ("instant", "digest", "both"):
            mark = "✅ " if mode == user.mode else ""
            kb.button(text=mark + t(user.lang, f"mode_{mode}"), callback_data=f"mode:{mode}")
        kb.adjust(1)
        text = t(user.lang, "choose_mode")
    elif what == "hour":
        for hour in range(5, 24):
            mark = "✅" if hour == user.digest_hour else ""
            kb.button(text=f"{mark}{hour:02d}:00", callback_data=f"hour:{hour}")
        kb.adjust(4)
        text = t(user.lang, "choose_hour")
    elif what == "tz":
        for index, (name, label) in enumerate(TIMEZONES):
            mark = "✅ " if name == user.timezone else ""
            kb.button(text=mark + label, callback_data=f"tz:{index}")
        kb.adjust(1)
        text = t(user.lang, "choose_tz")
    else:
        return await callback.answer()
    kb.row()
    kb.button(text=t(user.lang, "btn_back"), callback_data="settings")
    await callback.message.edit_text(text, reply_markup=kb.as_markup())
    await callback.answer()


@router.callback_query(F.data == "settings")
async def cb_settings_back(callback: CallbackQuery, db: Database):
    user = await get_or_create_user(db, callback.from_user)
    await show_settings(callback.message, user, edit=True)
    await callback.answer()


@router.callback_query(F.data.regexp(r"^(mode|hour|tz):"))
async def cb_setting_value(callback: CallbackQuery, db: Database):
    user = await get_or_create_user(db, callback.from_user)
    kind, value = callback.data.split(":", 1)
    if kind == "mode" and value in ("instant", "digest", "both"):
        await db.update_user(user.user_id, mode=value)
    elif kind == "hour" and value.isdigit() and 0 <= int(value) <= 23:
        # Changing the time re-arms today's digest.
        await db.update_user(user.user_id, digest_hour=int(value), last_digest_at=None)
    elif kind == "tz" and value.isdigit() and int(value) < len(TIMEZONES):
        await db.update_user(user.user_id, timezone=TIMEZONES[int(value)][0], last_digest_at=None)
    await show_settings(callback.message, await db.get_user(user.user_id), edit=True)
    await callback.answer("✅")


# ------------------------------------------------------------------- admin

def is_admin(message: Message, config: Config) -> bool:
    return message.from_user.id in config.admin_ids


@router.message(Command("stats"))
async def cmd_stats(message: Message, db: Database, config: Config):
    if not is_admin(message, config):
        return
    s = await db.stats()
    failing = await db.failing_feeds()
    await message.answer(
        "<b>MEAE NEWS — stats</b>\n\n"
        f"Users: {s['users']} (blocked the bot: {s['blocked']})\n"
        f"Keywords: {s['keywords']}\n"
        f"Articles stored: {s['articles']} (last 24h: {s['articles_24h']})\n"
        f"Matches last 24h: {s['alerts_24h']}\n"
        f"Sources: {len(FEEDS)} (failing: {len(failing)} — /feeds)"
    )


@router.message(Command("feeds"))
async def cmd_feeds(message: Message, db: Database, config: Config):
    if not is_admin(message, config):
        return
    failing = await db.failing_feeds()
    if not failing:
        await message.answer("All feeds are working ✅")
        return
    names = {feed.url: feed.name for feed in FEEDS}
    lines = [f"<b>Failing feeds ({len(failing)})</b>", ""]
    for row in failing[:40]:
        name = html.escape(names.get(row["url"], row["url"]))
        lines.append(f"• {name} — {row['fail_count']}× — <i>{html.escape(row['last_error'] or '')}</i>")
    await message.answer("\n".join(lines)[:4000])


@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message, command: CommandObject, db: Database, config: Config):
    if not is_admin(message, config):
        return
    if not command.args:
        await message.answer("Usage: /broadcast your message (HTML allowed)")
        return
    users = await db.active_users()
    await message.answer(f"Sending to {len(users)} users…")
    delivered = 0
    for user in users:
        if await send(message.bot, db, user.user_id, command.args):
            delivered += 1
        await asyncio.sleep(0.05)
    await message.answer(f"Delivered to {delivered} of {len(users)} users.")


# ------------------------------------------------------- menu and fallback

@router.message(F.text)
async def on_text(message: Message, state: FSMContext, db: Database, config: Config):
    user = await get_or_create_user(db, message.from_user)
    action = menu_action(message.text)
    if action:
        await state.clear()
    if action == "menu_add":
        await start_add(message, state, db, config, user)
    elif action == "menu_list":
        await show_list(message, db, config, user)
    elif action == "menu_search":
        await state.set_state(Form.search)
        await message.answer(t(user.lang, "search_prompt"))
    elif action == "menu_settings":
        await show_settings(message, user)
    elif action == "menu_help":
        await message.answer(t(user.lang, "help", **counts(config)), reply_markup=main_menu(user.lang))
    else:
        await message.answer(t(user.lang, "use_menu"), reply_markup=main_menu(user.lang))
