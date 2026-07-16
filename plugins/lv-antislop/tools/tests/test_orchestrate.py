from a.contract import AInput, Requirement, Policy
from a.gate_adapter import b3_gate
from a.orchestrate import generate


def _gen_from(seq):
    """stub generator: returns seq[attempt], ignores the payload."""
    calls = {"n": -1}
    def gen(_payload):
        calls["n"] += 1
        return seq[min(calls["n"], len(seq) - 1)]
    return gen


def test_clean_first_attempt_stops_early():
    ai = AInput(intent="write", profile="style_only")
    r = generate(ai, _gen_from(["Mēs būvējam sistēmas medicīnas tirgotājiem."]), b3_gate)
    assert r.status == "generated" and r.revision == 0
    assert r.gate.outcome == "clear" and r.needs_human is False


def test_repair_improves_until_clean():
    ai = AInput(intent="write", profile="style_only")
    seq = ["Mēs esam uzticams partneris.",      # attempt 0: issue
           "Mēs piegādājam 48 stundās."]         # repair 1: clean
    r = generate(ai, _gen_from(seq), b3_gate)
    assert r.revision == 1 and r.gate.outcome == "clear" and r.needs_human is False


def test_picks_fewest_issue_flags_when_none_clean():
    ai = AInput(intent="write", profile="style_only")
    seq = ["Uzticams partneris, individuāla pieeja.",  # 2 issues
           "Uzticams partneris.",                       # 1 issue
           "Uzticams partneris."]                       # 1 issue
    r = generate(ai, _gen_from(seq), b3_gate)
    assert r.gate.has_issues and len([f for f in r.gate.flags if f.severity == "issue"]) == 1
    assert r.needs_human is True


def test_preservation_failure_forces_needs_human():
    ai = AInput(intent="write", profile="style_only",
                requirements=[Requirement("fact", "4.8% ABV")])
    # both candidates are B3-clean but DROP the required fact
    r = generate(ai, _gen_from(["Garšīgs alus.", "Svaigs alus."]), b3_gate)
    assert r.status == "generated" and r.needs_human is True   # no survivor preserves the fact


def test_cloud_forbidden_returns_denied():
    ai = AInput(intent="write", policy=Policy(cloud_allowed=False))
    r = generate(ai, _gen_from(["x"]), b3_gate)
    assert r.status == "denied" and r.reason == "cloud_forbidden" and r.needs_human is True
