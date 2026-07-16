from b.analyze import analyze
from b.index import Lexicon, WordformIndex

LEX = Lexicon.from_words({"alus", "svaigs"})                  # B1 lexicon is SMALL (missing "alu")
WF = WordformIndex.from_mapping(
    {"alus": ["alus"], "alu": ["alus"], "svaigs": ["svaigs"]})  # B2 wordforms is the authority

def _ids(flags):
    return [(f.rule_id, f.observed) for f in flags]

def test_b2_validates_a_form_b1_lexicon_missed():
    # "alu" is unknown to B1 but valid per B2 -> NO flag (escalation clears it)
    flags = analyze("Svaigs alu.", LEX, WF)
    assert flags == []

def test_hallucinated_form_flags_no_known_analysis():
    flags = analyze("Svaigs blrgh.", LEX, WF)
    assert ("morphology.no_known_analysis", "blrgh") in _ids(flags)

def test_spelling_candidate_survives_when_b2_also_absent():
    flags = analyze("Svaigss alus.", LEX, WF)     # "svaigss" ~ edit1 of svaigs, absent in WF
    assert ("spelling.candidate", "Svaigss") in _ids(flags)
