from lex.lookup import lookup

INDEX = {
    "meta": {"release": "fixture", "file": "lex-index.fixture.json", "sha256": "fixture"},
    "entries": {
        "labs": {
            "lemmas": [{"lemma": "labs", "sense_id": "labs.1", "gloss": "kvalitatīvs"}],
            "synonyms": [{"surface": "kvalitatīvs", "lemma": "kvalitatīvs", "source": "tezaurs"},
                         {"surface": "izcils", "lemma": "izcils", "source": "wordnet"}],
        }
    },
}

def test_hit_returns_ok_with_synonyms():
    r = lookup("labs", "surface", INDEX)
    assert r.status == "ok"
    assert r.resolved_lemmas[0].lemma == "labs"
    assert {s.surface for s in r.synonyms} == {"kvalitatīvs", "izcils"}
    assert r.provenance["release"] == "fixture"

def test_miss_returns_not_found():
    r = lookup("nezināmsvārds", "surface", INDEX)
    assert r.status == "not_found" and r.synonyms == []

def test_none_index_returns_unavailable():
    r = lookup("labs", "surface", None)
    assert r.status == "unavailable"

def test_case_and_nfc_insensitive():
    r = lookup("LABS", "surface", INDEX)
    assert r.status == "ok"
