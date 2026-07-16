from b3.gate import gate_style_only, GateResult
from b3.scanner import Flag

def test_clean_style_only_is_pass():
    g = gate_style_only(flags=[], b3_status="completed")
    assert g.profile == "style_only"
    assert g.assurance == "complete" and not g.has_issues
    assert g.outcome == "clear" and g.needs_human is False

def test_issue_flag_sets_issues_outcome():
    g = gate_style_only(flags=[Flag(0, 5, "cliche.uzticams_partneris", "issue", "x")],
                        b3_status="completed")
    assert g.has_issues and g.outcome == "issues" and g.needs_human

def test_diagnostic_only_is_clear():
    g = gate_style_only(flags=[Flag(0, 4, "overused.verbs", "diagnostic", "x")],
                        b3_status="completed")
    assert not g.has_issues and g.outcome == "clear"

def test_incomplete_with_issues_is_representable():
    # round-5 B5: a check that found an issue THEN crashed stays has_issues + partial
    # (incomplete progress is DISTINCT from engine-absent)
    g = gate_style_only(flags=[Flag(0, 5, "cliche.uzticams_partneris", "issue", "x")],
                        b3_status="incomplete")
    assert g.has_issues is True
    assert g.assurance == "partial"
    assert g.outcome == "issues" and g.needs_human

def test_incomplete_no_issues_is_not_cleared_not_pass():
    g = gate_style_only(flags=[], b3_status="incomplete")
    assert g.assurance == "partial" and not g.has_issues
    assert g.outcome == "not_cleared" and g.needs_human

def test_unavailable_engine_is_distinct_from_incomplete():
    # engine absent -> assurance=unavailable (distinct from incomplete progress)
    g = gate_style_only(flags=[], b3_status="unavailable")
    assert g.assurance == "unavailable" and not g.has_issues
    assert g.outcome == "not_cleared" and g.needs_human
