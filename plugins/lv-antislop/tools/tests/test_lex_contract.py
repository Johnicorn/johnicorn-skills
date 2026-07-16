from pathlib import Path
from lex.lookup import load_index, lookup

FIX = Path(__file__).parents[2] / "contracts" / "lex-index.fixture.json"

def test_fixture_loads_and_looks_up():
    idx = load_index(FIX)
    r = lookup("ātrs", "surface", idx)
    assert r.status == "ok"
    assert {s.surface for s in r.synonyms} == {"straujš", "žigls"}
    assert all(s.source in ("tezaurs", "wordnet") for s in r.synonyms)
    assert r.provenance["release"] == "fixture-v1"
