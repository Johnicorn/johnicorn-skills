from b.gate import gate
from b3.scanner import Flag

def test_morphology_profile_requires_b2_and_b3():
    g = gate("morphology", {"B2": "completed", "B3": "completed"}, [])
    assert g.profile == "morphology" and g.outcome == "clear"
    assert set(k for k, v in g.checks.items() if v["requested"]) == {"B2", "B3"}

def test_full_profile_missing_b1_is_partial():
    g = gate("full", {"B2": "completed", "B3": "completed", "B1": "unavailable"}, [])
    assert g.assurance == "partial" and g.outcome == "not_cleared" and g.needs_human

def test_issue_flag_sets_issues():
    g = gate("full", {"B1": "completed", "B2": "completed", "B3": "completed"},
             [Flag(0, 5, "spelling.candidate", "issue", "x")])
    assert g.has_issues and g.outcome == "issues"

def test_diagnostic_only_is_clear():
    g = gate("morphology", {"B2": "completed", "B3": "completed"},
             [Flag(0, 5, "morphology.no_known_analysis", "diagnostic", "x")])
    assert not g.has_issues and g.outcome == "clear"
