from lex.lookup import lookup
from lex.contract import LexResult

AMBIG = {
    "meta": {"release": "fixture"},
    "entries": {
        "sods": {  # two lemmas / senses -> ambiguous, return BOTH (never pick)
            "lemmas": [{"lemma": "sods", "sense_id": "sods.1", "gloss": "penalty"},
                       {"lemma": "sods", "sense_id": "sods.2", "gloss": "dessert (colloq.)"}],
            "synonyms": [{"surface": "soda nauda", "lemma": "sods", "source": "tezaurs"}],
        }
    },
}

def test_ambiguous_returns_all_candidates_not_a_pick():
    r = lookup("sods", "surface", AMBIG)
    assert r.ambiguous is True
    assert len(r.resolved_lemmas) == 2          # both senses returned; caller/human chooses

def test_result_is_inert_data_no_substitution_api():
    # advisory: LexResult must not expose any mutate/substitute/apply method
    r = lookup("sods", "surface", AMBIG)
    for banned in ("apply", "substitute", "rewrite", "inject", "to_gate_feedback"):
        assert not hasattr(r, banned)

def test_empty_query_is_not_found():
    r = lookup("   ", "surface", AMBIG)
    assert r.status == "not_found"
