import string

from bot.handlers import main_menu
from bot.i18n import STRINGS, language_for, menu_action, t


def placeholders(text: str) -> set[str]:
    return {name for _, name, _, _ in string.Formatter().parse(text) if name}


def test_both_languages_have_the_same_keys_and_placeholders():
    en, ar = STRINGS["en"], STRINGS["ar"]
    assert en.keys() == ar.keys()
    for key in en:
        assert placeholders(en[key]) == placeholders(ar[key]), key


def test_telegram_profile_limits():
    for lang in STRINGS:
        assert len(t(lang, "short_description")) <= 120
        assert len(t(lang, "description")) <= 512


def test_language_for():
    assert language_for("ar") == "ar"
    assert language_for("ar-SA") == "ar"
    assert language_for("tr") == "en"
    assert language_for(None) == "en"


def test_menu_buttons_are_recognised_in_both_languages():
    for lang in STRINGS:
        for row in main_menu(lang).keyboard:
            for button in row:
                assert menu_action(button.text)
    assert menu_action("Aramco") is None
