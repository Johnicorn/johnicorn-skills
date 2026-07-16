from pathlib import Path
from a.acceptance import load_oracle, check_output

ORACLE = Path(__file__).parents[2] / "contracts" / "phase1a-acceptance.v1.yaml"
O = load_oracle(ORACLE)


def test_clean_tu_output_passes_invariants():
    res = check_output("Pasūti sev svaigu alu.", O)
    assert res["b3_issue_hits"] == 0
    assert res["tu_violation"] is False
    assert res["persona_marker"] is False
    assert res["pass"] is True


def test_b3_issue_fails():
    res = check_output("Mēs esam uzticams partneris.", O)
    assert res["b3_issue_hits"] >= 1 and res["pass"] is False


def test_jus_register_fails():
    res = check_output("Sazinieties ar mums.", O)
    assert res["tu_violation"] is True and res["pass"] is False


def test_persona_marker_fails_neutral_core():
    res = check_output("Vispirms brālis, tad ležaks.", O)
    assert res["persona_marker"] is True and res["pass"] is False
