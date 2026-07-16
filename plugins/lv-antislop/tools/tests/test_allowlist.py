from pathlib import Path

import pytest

from b.allowlist import load_allowlist
from b.analyze import analyze
from b.index import Lexicon, WordformIndex, norm
from b.spelling import spell_check


def test_load_allowlist_skips_comments_blanks_normalizes_and_unions(tmp_path):
    first = tmp_path / "first.txt"
    second = tmp_path / "second.txt"
    first.write_text("# pilot terms\n\nSĀKumlapa\nke\u0301\n", encoding="utf-8")
    second.write_text("# more terms\nKešatmiņa\n", encoding="utf-8")

    assert load_allowlist(first, second) == frozenset({"sākumlapa", "ké", "kešatmiņa"})


def test_load_allowlist_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_allowlist(tmp_path / "missing.txt")


def test_spell_check_allowlist_suppresses_spelling_candidate():
    lexicon = Lexicon.from_words({"alus"})

    assert spell_check("aluss", lexicon) == ("SPELLING_CANDIDATE", "alus")
    assert spell_check("aluss", lexicon, frozenset({"aluss"})) is None


def test_analyze_allowlist_suppresses_unknown_without_affecting_b2_flow():
    lexicon = Lexicon.from_words({"alus"})
    index = WordformIndex.from_mapping({"alus": ["alus"]})

    assert analyze("zinātvārds", lexicon, index, frozenset({"zinātvārds"})) == []
    flags = analyze("zinātvārds", lexicon, index)
    assert [(flag.rule_id, flag.observed) for flag in flags] == [
        ("morphology.no_known_analysis", "zinātvārds")]


def test_shipped_allowlist_does_not_suppress_an_edit_one_typo():
    data = Path(__file__).parents[1] / "data"
    allow = load_allowlist(data / "lv-it-supplement.txt", data / "tezaurs-gaps.txt")
    lexicon = Lexicon.from_words({"alus"})
    index = WordformIndex.from_mapping({"alus": ["alus"]})

    flags = analyze("aluss", lexicon, index, allow)
    assert [(flag.rule_id, flag.observed) for flag in flags] == [("spelling.candidate", "aluss")]


def test_shipped_allowlist_is_normalized_and_nonempty():
    data = Path(__file__).parents[1] / "data"
    allow = load_allowlist(data / "lv-it-supplement.txt", data / "tezaurs-gaps.txt")

    assert allow
    assert all(entry == norm(entry) for entry in allow)
