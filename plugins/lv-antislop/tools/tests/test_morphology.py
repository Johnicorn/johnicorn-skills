from b.morphology import form_check
from b.index import WordformIndex

WF = WordformIndex.from_mapping(
    {"alus": ["alus"], "alu": ["alus"], "svaigs": ["svaigs"], "svaigu": ["svaigs"]},
    {"alus": 5000, "svaigs": 40},   # lemma frequency; low = rare
)

def test_known_form_validated_with_lemma():
    r = form_check("alu", WF)
    assert r.status == "validated" and r.lemmas == ["alus"] and r.rare is False

def test_rare_lemma_flagged_rare_but_valid():
    r = form_check("svaigu", WF)
    assert r.status == "validated" and r.rare is True   # freq below threshold

def test_absent_form_is_no_known_analysis():
    r = form_check("blrgh", WF)
    assert r.status == "no_known_analysis" and r.lemmas == []
