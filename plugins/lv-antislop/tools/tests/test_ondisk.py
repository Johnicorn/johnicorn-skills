import sqlite3

import pytest

from b.index import WordformIndex, build_index, load_index
from b.morphology import form_check
from b.ondisk import SqliteWordforms, build_sqlite_wordforms, load_index_ondisk


FORMS = ["Kafija", "Rīga", "Silts"]
WORDFORMS = {
    "kafiju": ["kafija"],
    "Rīgā": ["Rīga"],
    "RI\u0304GA\u0304": ["Rīgas"],  # NFC + case collision with Rīgā
    "siltu": ["silts", "siltums"],
}
FREQ = {"kafija": 1000, "Rīga": 1000, "Rīgas": 500, "silts": 1000, "siltums": 1000}


def _build_ondisk_index(tmp_path):
    build_index(FORMS, WORDFORMS, FREQ, tmp_path)
    database = tmp_path / "wordforms.sqlite"
    build_sqlite_wordforms(tmp_path / "wordforms.tsv", database)
    return database


def test_sqlite_wordforms_match_in_memory_index_for_every_key(tmp_path):
    database = _build_ondisk_index(tmp_path)
    _, in_memory = load_index(tmp_path)

    with SqliteWordforms(database) as sqlite_forms:
        for key in in_memory.forms:
            assert sqlite_forms.get(key) == in_memory.forms.get(key)
        for key in ("", "neesošs", "riga"):
            assert sqlite_forms.get(key) is None


def test_sqlite_wordforms_returns_default_for_non_string_keys(tmp_path):
    build_index([], {"1": ["viens"]}, {}, tmp_path)
    database = tmp_path / "wordforms.sqlite"
    build_sqlite_wordforms(tmp_path / "wordforms.tsv", database)

    with SqliteWordforms(database) as sqlite_forms:
        assert sqlite_forms.get(1) is None
        assert sqlite_forms.get(True) is None
        assert sqlite_forms.get("1") == ["viens"]


def test_form_check_accepts_sqlite_wordforms_as_a_drop_in(tmp_path):
    database = _build_ondisk_index(tmp_path)
    _, in_memory = load_index(tmp_path)
    sqlite_index = WordformIndex(forms=SqliteWordforms(database), freq=in_memory.freq)

    try:
        for token in ("KAFIJU", "RĪGĀ", "neesošs"):
            sqlite_result = form_check(token, sqlite_index)
            in_memory_result = form_check(token, in_memory)
            assert sqlite_result.status == in_memory_result.status
            assert sqlite_result.lemmas == in_memory_result.lemmas
    finally:
        sqlite_index.forms.close()


def test_load_index_ondisk_round_trips_for_form_check(tmp_path):
    _build_ondisk_index(tmp_path)
    _, index = load_index_ondisk(tmp_path)

    try:
        assert form_check("Rīgā", index).status == "validated"
        assert form_check("neesošs", index).status == "no_known_analysis"
    finally:
        index.forms.close()


def test_load_index_ondisk_detects_tampered_forms(tmp_path):
    _build_ondisk_index(tmp_path)
    (tmp_path / "forms.txt").write_text("tampered\n", encoding="utf-8")

    with pytest.raises(ValueError, match="sha256"):
        load_index_ondisk(tmp_path)


def test_load_index_ondisk_rejects_stale_sqlite_wordforms(tmp_path):
    database = _build_ondisk_index(tmp_path)
    build_index(
        ["Cits"], {"citu": ["cits"]}, {"cits": 1}, tmp_path)

    with pytest.raises(ValueError, match="stale"):
        load_index_ondisk(tmp_path, database)


def test_build_sqlite_wordforms_replaces_an_existing_database_atomically(tmp_path):
    first = tmp_path / "first"
    second = tmp_path / "second"
    database = tmp_path / "wordforms.sqlite"
    build_index([], {"pirmais": ["pirmais"]}, {}, first)
    build_index([], {"otrais": ["otrais"]}, {}, second)

    build_sqlite_wordforms(first / "wordforms.tsv", database)
    build_sqlite_wordforms(second / "wordforms.tsv", database)

    with SqliteWordforms(database) as sqlite_forms:
        assert sqlite_forms.get("pirmais") is None
        assert sqlite_forms.get("otrais") == ["otrais"]


def test_sqlite_wordforms_context_manager_closes_connection(tmp_path):
    database = _build_ondisk_index(tmp_path)

    with SqliteWordforms(database) as forms:
        assert forms.get("siltu") == ["silts", "siltums"]
    with pytest.raises(sqlite3.ProgrammingError):
        forms.get("siltu")
