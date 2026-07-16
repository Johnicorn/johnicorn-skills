from b.index import norm, Lexicon, WordformIndex, FORMAT_VERSION

def test_norm_is_nfc_lower():
    assert norm("Alus") == "alus"
    assert norm("RĪGA") == "rīga"

def test_lexicon_normalizes_and_dedups_once():
    lex = Lexicon.from_words(["Alus", "alus", "Svaigs"])
    assert lex.forms == frozenset({"alus", "svaigs"})

def test_wordform_index_normalizes_keys_and_keeps_freq():
    idx = WordformIndex.from_mapping({"Alu": ["alus"]}, {"alus": 5000})
    assert idx.forms == {"alu": ["alus"]}
    assert idx.freq == {"alus": 5000}

def test_wordform_index_freq_defaults_empty():
    idx = WordformIndex.from_mapping({"alu": ["alus"]})
    assert idx.freq == {}

def test_colliding_keys_merge_lemmas_sorted_deduped():
    # "Alu" and "alu" both normalize to "alu" -> union of lemmas, NOT last-wins
    idx = WordformIndex.from_mapping({"Alu": ["alus", "ala"], "alu": ["ala", "aluss"]})
    assert idx.forms == {"alu": ["ala", "alus", "aluss"]}   # sorted, deduped union

def test_format_version_is_a_string():
    assert isinstance(FORMAT_VERSION, str) and FORMAT_VERSION

from b.spelling import spell_check
from b.morphology import form_check

class _MembershipOnly:
    """Exposes ONLY __contains__. Any iteration (Python-level) raises."""
    def __init__(self, items): self._s = set(items)
    def __contains__(self, x): return x in self._s
    def __iter__(self): raise AssertionError("B1 query iterated the whole lexicon (per-call rescan)")

class _GetOnly:
    """Exposes ONLY .get. Any iteration raises."""
    def __init__(self, mapping): self._d = dict(mapping)
    def get(self, k, default=None): return self._d.get(k, default)
    def __iter__(self): raise AssertionError("B2 query iterated the whole index")
    def keys(self):     raise AssertionError("B2 query iterated the whole index")
    def values(self):   raise AssertionError("B2 query iterated the whole index")
    def items(self):    raise AssertionError("B2 query iterated the whole index")

def test_b1_query_does_not_scan_lexicon():
    lex = Lexicon(forms=_MembershipOnly({"alus"}))
    assert spell_check("alus", lex) is None                            # hit
    assert spell_check("zzzz", lex) == ("UNKNOWN_TO_LEXICON", None)    # miss + no edit-1 hit

def test_b2_query_does_not_scan_index():
    idx = WordformIndex(forms=_GetOnly({"alu": ["alus"]}), freq={})
    assert form_check("alu", idx).status == "validated"
    assert form_check("zzzz", idx).status == "no_known_analysis"

import json, pytest
from b.index import build_index, load_index

FORMS = ["Alus", "svaigs", "alus"]                       # dup + case -> normalized/deduped on build
WORDFORMS = {"Alu": ["alus"], "svaigu": ["svaigs"]}
FREQ = {"alus": 5000, "svaigs": 40}

def test_build_then_load_round_trips(tmp_path):
    build_index(FORMS, WORDFORMS, FREQ, tmp_path)
    lex, idx = load_index(tmp_path)
    assert "alus" in lex.forms and "svaigs" in lex.forms
    assert idx.forms == {"alu": ["alus"], "svaigu": ["svaigs"]}
    assert idx.freq == {"alus": 5000, "svaigs": 40}
    from b.spelling import spell_check
    from b.morphology import form_check
    assert spell_check("alu", lex) == ("SPELLING_CANDIDATE", "alus")   # not in B1 lexicon
    assert form_check("alu", idx).status == "validated"                # but valid per B2

def test_manifest_has_version_counts_and_sha256(tmp_path):
    build_index(FORMS, WORDFORMS, FREQ, tmp_path)
    m = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    assert m["format_version"] == FORMAT_VERSION
    assert m["counts"] == {"forms": 2, "wordforms": 2, "freq": 2}
    assert set(m["sha256"]) == {"forms.txt", "wordforms.tsv", "freq.tsv"}
    assert all(len(h) == 64 for h in m["sha256"].values())

def test_build_is_reproducible_byte_for_byte(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    build_index(FORMS, WORDFORMS, FREQ, a)
    build_index(FORMS, WORDFORMS, FREQ, b)
    for name in ("forms.txt", "wordforms.tsv", "freq.tsv", "manifest.json"):
        ba, bb = (a / name).read_bytes(), (b / name).read_bytes()
        assert ba == bb                                  # deterministic bytes
        assert b"\r" not in ba                           # no CRLF
        assert not ba.startswith(b"\xef\xbb\xbf")        # no UTF-8 BOM

def test_load_detects_tampering(tmp_path):
    build_index(FORMS, WORDFORMS, FREQ, tmp_path)
    (tmp_path / "forms.txt").write_text("tampered\n", encoding="utf-8")
    with pytest.raises(ValueError, match="sha256"):
        load_index(tmp_path)

def test_load_rejects_wrong_format_version(tmp_path):
    build_index(FORMS, WORDFORMS, FREQ, tmp_path)
    m = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    m["format_version"] = "999"
    (tmp_path / "manifest.json").write_text(json.dumps(m), encoding="utf-8")
    with pytest.raises(ValueError, match="format_version"):
        load_index(tmp_path)

def test_load_rejects_malformed_manifest(tmp_path):
    build_index(FORMS, WORDFORMS, FREQ, tmp_path)
    (tmp_path / "manifest.json").write_text(
        json.dumps({"format_version": FORMAT_VERSION}), encoding="utf-8")  # no sha256
    with pytest.raises(ValueError, match="manifest"):
        load_index(tmp_path)

def test_build_rejects_separator_chars(tmp_path):
    with pytest.raises(ValueError, match="whitespace|separator"):
        build_index(["a b"], {}, {}, tmp_path)           # space in a form
    with pytest.raises(ValueError, match="separator|comma"):
        build_index([], {"x": ["a,b"]}, {}, tmp_path)    # comma in a lemma

def test_build_rejects_empty_lemma_list(tmp_path):
    with pytest.raises(ValueError, match="lemma"):
        build_index([], {"x": []}, {}, tmp_path)         # a present key must have >=1 lemma

def test_build_rejects_empty_form(tmp_path):
    with pytest.raises(ValueError, match="empty"):
        build_index([""], {}, {}, tmp_path)              # empty form would vanish on load

def test_build_rejects_empty_lemma_string(tmp_path):
    with pytest.raises(ValueError, match="empty"):
        build_index([], {"x": [""]}, {}, tmp_path)       # [""] serializes like [] -> reject

def test_build_rejects_separator_in_freq_key(tmp_path):
    with pytest.raises(ValueError, match="whitespace|freq"):
        build_index([], {}, {"a\tb": 5}, tmp_path)       # tab in freq key would corrupt freq.tsv

def test_build_leaves_existing_index_untouched_on_invalid_input(tmp_path):
    # Failure atomicity: an invalid input into a populated index dir must NOT
    # truncate/partly-replace the existing files before raising (validate-before-write).
    build_index(["alus"], {"alu": ["alus"]}, {"alus": 5000}, tmp_path)
    before = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    with pytest.raises(ValueError, match="separator|comma"):
        build_index(["alus"], {"a": ["ok"], "z": ["bad,lemma"]}, {}, tmp_path)
    after = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    assert after == before          # nothing written on the failed rebuild
