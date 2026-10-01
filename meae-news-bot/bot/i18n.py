"""Every message the bot sends, in English and Arabic.

Texts use Telegram HTML (<b>, <i>, <code>). Keep the same {placeholders}
in both languages; tests/test_i18n.py checks this.
"""

LANGUAGES = ("en", "ar")
LANGUAGE_NAMES = {"en": "🇬🇧 English", "ar": "🇸🇦 العربية"}

STRINGS: dict[str, dict[str, str]] = {
    "en": {
        "short_description": "MEAE NEWS — real-time monitoring of mentions in Middle East & Asia online media. Be the first to know!",
        "description": (
            "MEAE NEWS — real-time monitoring of mentions in online media across the Middle East and Asia.\n\n"
            "Follow a company, brand, organisation or person and get an alert within minutes "
            "whenever the news mentions it. In English and Arabic. Free."
        ),
        "welcome": (
            "<b>MEAE NEWS</b> — real-time monitoring of mentions in online media across the Middle East and Asia.\n\n"
            "<b>Main job:</b> tell you instantly when something you follow is mentioned in the news.\n"
            "<b>Typical things to follow:</b> a company, brand or trademark, an organisation, "
            "or a person's name.\n\n"
            "<b>MEAE NEWS:</b>\n"
            "🕐 Monitoring 24/7\n"
            "🌍 {sources}+ news sources: Gulf, Levant, Egypt, Iraq, Iran, Yemen, Turkey, "
            "Afghanistan, Bangladesh, Myanmar — plus Google News\n"
            "🔤 English and Arabic: one keyword can cover both spellings\n"
            "🚀 Instant alerts (within ~5 minutes) or a daily digest\n"
            "🆓 Free — up to {max} keywords\n\n"
            "Tap <b>➕ Add keyword</b> to start."
        ),
        "choose_lang": "Choose your language / اختر لغتك:",
        "lang_set": "✅ Language: English",
        "menu_add": "➕ Add keyword",
        "menu_list": "📋 My keywords",
        "menu_search": "🔍 Search",
        "menu_settings": "⚙️ Settings",
        "menu_help": "❓ Help",
        "help": (
            "<b>How MEAE NEWS works</b>\n\n"
            "1. Add a keyword — a company, brand or person.\n"
            "2. The bot checks {sources}+ news sites every few minutes, and Google News.\n"
            "3. When a new article mentions your keyword, you get an alert.\n\n"
            "<b>Writing a keyword</b>\n"
            "Separate other spellings with commas, and put a minus before words to exclude:\n"
            "<code>Aramco, أرامكو, Saudi Aramco, -stock</code>\n"
            "• <b>Aramco</b> — the main name\n"
            "• <b>أرامكو, Saudi Aramco</b> — other spellings (Arabic or English)\n"
            "• <b>-stock</b> — skip articles that mention this word\n\n"
            "Upper/lower case, Arabic diacritics and spellings like أ/ا or ة/ه don't matter.\n\n"
            "<b>Commands</b>\n"
            "/add — add a keyword\n"
            "/list — your keywords\n"
            "/search — search recent news\n"
            "/settings — language, alerts, digest time\n"
            "/cancel — cancel the current step"
        ),
        "add_prompt": (
            "Send the name to follow. You can add other spellings after commas, "
            "and words to exclude with a minus:\n\n"
            "<code>Aramco, أرامكو, Saudi Aramco, -stock</code>\n\n"
            "/cancel to stop."
        ),
        "add_ok": "✅ Now following <b>{name}</b>.\nYou'll get an alert when a new article mentions it.\n\n{details}",
        "limit_reached": "You already follow {max} keywords, the maximum. Delete one in 📋 My keywords to add another.",
        "err_too_short": "⚠️ Each word must be at least 2 letters. Please try again.",
        "err_too_long": "⚠️ That's too long — keep each spelling under 80 characters.",
        "err_no_name": "⚠️ Please send a name to follow (not only words to exclude).",
        "err_too_many": "⚠️ Up to 10 spellings and 10 excluded words per keyword.",
        "list_empty": "You don't follow any keywords yet. Tap <b>➕ Add keyword</b>.",
        "list_header": "<b>Your keywords</b> ({count}/{max}). Tap one to edit or delete it:",
        "kw_detail": "<b>{name}</b>\n\n{details}",
        "label_variants": "Other spellings",
        "label_excludes": "Excluded words",
        "none": "none",
        "btn_edit": "✏️ Edit",
        "btn_delete": "🗑 Delete",
        "btn_recent": "🔍 Recent mentions",
        "btn_back": "⬅️ Back",
        "btn_confirm_delete": "🗑 Yes, delete",
        "btn_cancel": "Cancel",
        "confirm_delete": "Stop following <b>{name}</b>?",
        "deleted": "🗑 Stopped following <b>{name}</b>.",
        "edit_prompt": "Send the new version. Current:\n\n<code>{current}</code>\n\n/cancel to keep it.",
        "edited": "✅ Updated <b>{name}</b>.\n\n{details}",
        "not_found": "That keyword no longer exists.",
        "search_prompt": "What should I search for? Same format as keywords, e.g. <code>Aramco, أرامكو</code>",
        "search_none": "No mentions of <b>{query}</b> in the last {days} days.",
        "search_header": "<b>{query}</b> — latest {count} mentions (last {days} days):",
        "settings_header": (
            "<b>Settings</b>\n\n"
            "Language: {language}\n"
            "Alerts: {mode}\n"
            "Daily digest time: {hour}:00 ({timezone})"
        ),
        "btn_set_lang": "🌐 Language",
        "btn_set_mode": "🔔 Alerts",
        "btn_set_hour": "🕗 Digest time",
        "btn_set_tz": "🗺 Time zone",
        "mode_instant": "Instant",
        "mode_digest": "Daily digest only",
        "mode_both": "Instant + daily digest",
        "choose_mode": "How do you want to receive mentions?",
        "choose_hour": "When should the daily digest arrive?",
        "choose_tz": "Choose your time zone:",
        "alert_read": "Read article",
        "digest_header": "📰 <b>Your daily digest</b> — {count} mentions in the last 24 hours",
        "digest_empty": "📰 <b>Your daily digest</b>\nNo new mentions of your keywords in the last 24 hours.",
        "digest_more": "…and {count} more.",
        "cancelled": "Cancelled.",
        "use_menu": "Use the menu below, or /help.",
    },
    "ar": {
        "short_description": "MEAE NEWS — رصد فوري للإشارات في وسائل الإعلام الإلكترونية في الشرق الأوسط وآسيا. كن أول من يعلم!",
        "description": (
            "MEAE NEWS — رصد فوري للإشارات في وسائل الإعلام الإلكترونية في الشرق الأوسط وآسيا.\n\n"
            "تابع شركة أو علامة تجارية أو منظمة أو شخصاً، واحصل على تنبيه خلال دقائق "
            "كلما ذُكر في الأخبار. بالعربية والإنجليزية. مجاناً."
        ),
        "welcome": (
            "<b>MEAE NEWS</b> — رصد فوري للإشارات في وسائل الإعلام الإلكترونية في الشرق الأوسط وآسيا.\n\n"
            "<b>المهمة الرئيسية:</b> إبلاغك فوراً عندما يُذكر ما تتابعه في الأخبار.\n"
            "<b>أمثلة لما يمكن متابعته:</b> اسم شركة أو علامة تجارية، منظمة، "
            "أو اسم شخص.\n\n"
            "<b>MEAE NEWS:</b>\n"
            "🕐 رصد على مدار الساعة طوال الأسبوع\n"
            "🌍 أكثر من {sources} مصدراً إخبارياً: الخليج، الشام، مصر، العراق، إيران، اليمن، تركيا، "
            "أفغانستان، بنغلاديش، ميانمار — بالإضافة إلى أخبار Google\n"
            "🔤 العربية والإنجليزية: كلمة واحدة تشمل الكتابتين\n"
            "🚀 تنبيهات فورية (خلال ٥ دقائق تقريباً) أو ملخص يومي\n"
            "🆓 مجاني — حتى {max} كلمات مفتاحية\n\n"
            "اضغط <b>➕ إضافة كلمة</b> للبدء."
        ),
        "choose_lang": "Choose your language / اختر لغتك:",
        "lang_set": "✅ اللغة: العربية",
        "menu_add": "➕ إضافة كلمة",
        "menu_list": "📋 كلماتي",
        "menu_search": "🔍 بحث",
        "menu_settings": "⚙️ الإعدادات",
        "menu_help": "❓ مساعدة",
        "help": (
            "<b>كيف يعمل MEAE NEWS</b>\n\n"
            "١. أضف كلمة مفتاحية — شركة أو علامة تجارية أو شخص.\n"
            "٢. يفحص البوت أكثر من {sources} موقعاً إخبارياً كل بضع دقائق، وأخبار Google.\n"
            "٣. عندما يذكر مقال جديد كلمتك، يصلك تنبيه.\n\n"
            "<b>كتابة الكلمة المفتاحية</b>\n"
            "افصل بين الكتابات المختلفة بفواصل، وضع علامة ناقص قبل الكلمات المستبعدة:\n"
            "<code>أرامكو, Aramco, أرامكو السعودية, -أسهم</code>\n"
            "• <b>أرامكو</b> — الاسم الرئيسي\n"
            "• <b>Aramco، أرامكو السعودية</b> — كتابات أخرى (عربية أو إنجليزية)\n"
            "• <b>-أسهم</b> — تجاهل المقالات التي تذكر هذه الكلمة\n\n"
            "لا يهم التشكيل ولا الفرق بين أ/ا أو ة/ه، ويشمل البحث الكلمات المسبوقة "
            "بـ و، ب، ل، ال (مثل: وأرامكو، لأرامكو).\n\n"
            "<b>الأوامر</b>\n"
            "/add — إضافة كلمة\n"
            "/list — كلماتك\n"
            "/search — البحث في الأخبار الأخيرة\n"
            "/settings — اللغة والتنبيهات ووقت الملخص\n"
            "/cancel — إلغاء الخطوة الحالية"
        ),
        "add_prompt": (
            "أرسل الاسم الذي تريد متابعته. يمكنك إضافة كتابات أخرى بعد فواصل، "
            "وكلمات مستبعدة بعلامة ناقص:\n\n"
            "<code>أرامكو, Aramco, أرامكو السعودية, -أسهم</code>\n\n"
            "/cancel للإلغاء."
        ),
        "add_ok": "✅ تتم الآن متابعة <b>{name}</b>.\nسيصلك تنبيه عندما يذكرها مقال جديد.\n\n{details}",
        "limit_reached": "أنت تتابع {max} كلمات، وهو الحد الأقصى. احذف كلمة من 📋 كلماتي لإضافة أخرى.",
        "err_too_short": "⚠️ يجب أن تتكون كل كلمة من حرفين على الأقل. حاول مرة أخرى.",
        "err_too_long": "⚠️ النص طويل جداً — اجعل كل كتابة أقل من ٨٠ حرفاً.",
        "err_no_name": "⚠️ أرسل اسماً للمتابعة (وليس كلمات مستبعدة فقط).",
        "err_too_many": "⚠️ الحد الأقصى ١٠ كتابات و١٠ كلمات مستبعدة لكل كلمة مفتاحية.",
        "list_empty": "لا تتابع أي كلمات بعد. اضغط <b>➕ إضافة كلمة</b>.",
        "list_header": "<b>كلماتك المفتاحية</b> ({count}/{max}). اضغط على كلمة لتعديلها أو حذفها:",
        "kw_detail": "<b>{name}</b>\n\n{details}",
        "label_variants": "كتابات أخرى",
        "label_excludes": "كلمات مستبعدة",
        "none": "لا يوجد",
        "btn_edit": "✏️ تعديل",
        "btn_delete": "🗑 حذف",
        "btn_recent": "🔍 آخر الإشارات",
        "btn_back": "⬅️ رجوع",
        "btn_confirm_delete": "🗑 نعم، احذف",
        "btn_cancel": "إلغاء",
        "confirm_delete": "إيقاف متابعة <b>{name}</b>؟",
        "deleted": "🗑 تم إيقاف متابعة <b>{name}</b>.",
        "edit_prompt": "أرسل النسخة الجديدة. الحالية:\n\n<code>{current}</code>\n\n/cancel للإبقاء عليها.",
        "edited": "✅ تم تحديث <b>{name}</b>.\n\n{details}",
        "not_found": "هذه الكلمة لم تعد موجودة.",
        "search_prompt": "عمّ تريد البحث؟ بنفس صيغة الكلمات المفتاحية، مثل: <code>أرامكو, Aramco</code>",
        "search_none": "لا توجد إشارات إلى <b>{query}</b> خلال آخر {days} يوماً.",
        "search_header": "<b>{query}</b> — آخر {count} إشارات (خلال {days} يوماً):",
        "settings_header": (
            "<b>الإعدادات</b>\n\n"
            "اللغة: {language}\n"
            "التنبيهات: {mode}\n"
            "وقت الملخص اليومي: {hour}:00 ({timezone})"
        ),
        "btn_set_lang": "🌐 اللغة",
        "btn_set_mode": "🔔 التنبيهات",
        "btn_set_hour": "🕗 وقت الملخص",
        "btn_set_tz": "🗺 المنطقة الزمنية",
        "mode_instant": "فورية",
        "mode_digest": "ملخص يومي فقط",
        "mode_both": "فورية + ملخص يومي",
        "choose_mode": "كيف تريد استلام الإشارات؟",
        "choose_hour": "متى يصلك الملخص اليومي؟",
        "choose_tz": "اختر منطقتك الزمنية:",
        "alert_read": "اقرأ المقال",
        "digest_header": "📰 <b>ملخصك اليومي</b> — {count} إشارة خلال آخر ٢٤ ساعة",
        "digest_empty": "📰 <b>ملخصك اليومي</b>\nلا توجد إشارات جديدة إلى كلماتك خلال آخر ٢٤ ساعة.",
        "digest_more": "…و{count} أخرى.",
        "cancelled": "تم الإلغاء.",
        "use_menu": "استخدم القائمة بالأسفل، أو /help.",
    },
}

# Time zones offered in settings: (IANA name, label).
TIMEZONES = [
    ("Africa/Cairo", "Cairo · القاهرة"),
    ("Asia/Riyadh", "Riyadh, Baghdad, Kuwait, Doha, Aden · الرياض"),
    ("Europe/Istanbul", "Istanbul · إسطنبول"),
    ("Asia/Amman", "Amman, Damascus · عمّان"),
    ("Asia/Beirut", "Beirut · بيروت"),
    ("Asia/Tehran", "Tehran · طهران"),
    ("Asia/Dubai", "Dubai, Muscat · دبي"),
    ("Asia/Kabul", "Kabul · كابل"),
    ("Asia/Dhaka", "Dhaka · دكا"),
    ("Asia/Yangon", "Yangon · يانغون"),
    ("Europe/London", "London · لندن"),
    ("UTC", "UTC"),
]


def t(lang: str, key: str, **kwargs) -> str:
    table = STRINGS.get(lang, STRINGS["en"])
    text = table.get(key) or STRINGS["en"][key]
    return text.format(**kwargs) if kwargs else text


def language_for(telegram_code: str | None) -> str:
    """Pick the bot language from the user's Telegram app language."""
    return "ar" if (telegram_code or "").lower().startswith("ar") else "en"


def menu_action(text: str) -> str | None:
    """Which main-menu button was pressed, in either language."""
    for table in STRINGS.values():
        for key in ("menu_add", "menu_list", "menu_search", "menu_settings", "menu_help"):
            if text == table[key]:
                return key
    return None
