import pytest

from bot.textnorm import (KeywordInputError, KeywordRule, format_keyword_input, normalize,
                          parse_keyword_input)


def matches(rule: KeywordRule, text: str) -> bool:
    return rule.matches(normalize(text))


def test_normalize_arabic_spelling_variants():
    assert normalize("أَرامْكو") == normalize("ارامكو")
    assert normalize("إيران") == normalize("ايران")
    assert normalize("مكتبة") == normalize("مكتبه")
    assert normalize("مصطفى") == normalize("مصطفي")
    assert normalize("الـجـزيرة") == normalize("الجزيرة")
    assert normalize("٢٠٢٦") == "2026"


def test_normalize_latin():
    assert normalize("Erdoğan") == "erdogan"
    assert normalize("İSTANBUL") == "istanbul"
    assert normalize("Istanbul") == normalize("İstanbul")


def test_english_whole_words():
    rule = KeywordRule(1, 1, "Aramco")
    assert matches(rule, "Saudi Aramco reports profit")
    assert matches(rule, "ARAMCO's new plant")
    assert not matches(rule, "Aramcorp is a different company")


def test_arabic_attached_prefixes():
    rule = KeywordRule(1, 1, "أرامكو")
    for text in ("أعلنت أرامكو اليوم", "وأرامكو تعلن", "بارامكو", "لأرامكو", "فأرامكو", "والأرامكو"):
        assert matches(rule, text), text
    assert not matches(rule, "أرامكوية جديدة")


def test_arabic_term_with_al():
    rule = KeywordRule(1, 1, "الجزيرة")
    assert matches(rule, "قالت قناة الجزيرة")
    assert matches(rule, "في تصريح للجزيرة")
    assert matches(rule, "وبالجزيرة")


def test_variants_match_both_languages():
    rule = KeywordRule(1, 1, "Aramco", variants=["أرامكو"])
    assert matches(rule, "Aramco news")
    assert matches(rule, "أخبار أرامكو")


def test_multiword_and_hyphens():
    rule = KeywordRule(1, 1, "Al Jazeera")
    assert matches(rule, "Al-Jazeera reported")
    assert matches(rule, "al  jazeera reported")
    assert not matches(rule, "Jazeera only")


def test_excludes():
    rule = KeywordRule(1, 1, "Apple", excludes=["fruit", "تفاح"])
    assert matches(rule, "Apple launches a phone")
    assert not matches(rule, "Apple is a healthy fruit")
    assert not matches(rule, "Apple و تفاح")


def test_parse_keyword_input():
    parsed = parse_keyword_input("Aramco، أرامكو, Saudi Aramco, -stock, -أسهم")
    assert parsed.name == "Aramco"
    assert parsed.variants == ["أرامكو", "Saudi Aramco"]
    assert parsed.excludes == ["stock", "أسهم"]
    assert format_keyword_input(parsed.name, parsed.variants, parsed.excludes) == \
        "Aramco, أرامكو, Saudi Aramco, -stock, -أسهم"


def test_parse_keeps_inner_hyphens_and_dedupes():
    parsed = parse_keyword_input("Al-Jazeera, al-jazeera, \"Al Jazeera\"")
    assert parsed.name == "Al-Jazeera"
    assert parsed.variants == ["Al Jazeera"]


@pytest.mark.parametrize("text,code", [
    ("-only exclude", "err_no_name"),
    ("a", "err_too_short"),
    ("x" * 81, "err_too_long"),
    (", ".join(f"name{i}" for i in range(11)), "err_too_many"),
])
def test_parse_errors(text, code):
    with pytest.raises(KeywordInputError) as err:
        parse_keyword_input(text)
    assert err.value.code == code
