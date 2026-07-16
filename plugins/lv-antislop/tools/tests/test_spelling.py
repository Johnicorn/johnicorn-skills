from b.spelling import spell_check
from b.index import Lexicon

LEX = Lexicon.from_words({"alus", "svaigs", "labs", "rīga"})

def test_known_word_no_flag():
    assert spell_check("alus", LEX) is None
    assert spell_check("Alus", LEX) is None          # case-insensitive

def test_unknown_word_flagged():
    assert spell_check("kļūdains", LEX) == ("UNKNOWN_TO_LEXICON", None)

def test_edit_distance_1_is_spelling_candidate():
    assert spell_check("aluss", LEX) == ("SPELLING_CANDIDATE", "alus")

def test_skips_numbers_urls_abbrev():
    assert spell_check("4.8%", LEX) is None
    assert spell_check("https://x.lv", LEX) is None
    assert spell_check("ABV", LEX) is None           # all-caps abbreviation
