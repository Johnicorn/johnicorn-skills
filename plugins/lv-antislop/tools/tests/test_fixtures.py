from pathlib import Path
import yaml, pytest
from b3.manifest import load_manifest
from b3.scanner import scan, density_report

BASE = Path(__file__).parents[2] / "contracts"
M = load_manifest(BASE / "b3-style-manifest.v1.yaml")
FX = yaml.safe_load((BASE / "b3-fixtures.v1.yaml").read_text(encoding="utf-8"))["fixtures"]

ISSUE_IDS = {r.id for r in M.rules if r.severity == "issue"}

@pytest.mark.parametrize("rule_id", sorted(ISSUE_IDS))
def test_every_issue_rule_has_fixtures(rule_id):
    assert rule_id in FX, f"missing fixtures for issue rule {rule_id}"

@pytest.mark.parametrize("rule_id,case", [(rid, c) for rid, d in
    (yaml.safe_load((BASE / 'b3-fixtures.v1.yaml').read_text(encoding='utf-8'))['fixtures']).items()
    for c in d.get("positive", [])])
def test_positive_is_caught(rule_id, case):
    ids = {f.rule_id for f in scan(case, M)} | set(density_report(case, M).keys())
    assert rule_id in ids, f"positive for {rule_id} not caught: {case!r}"

@pytest.mark.parametrize("rule_id,case", [(rid, c) for rid, d in
    (yaml.safe_load((BASE / 'b3-fixtures.v1.yaml').read_text(encoding='utf-8'))['fixtures']).items()
    for c in d.get("negative", [])])
def test_negative_not_caught_as_issue(rule_id, case):
    issue_ids = {f.rule_id for f in scan(case, M) if f.severity == "issue"}
    assert rule_id not in issue_ids, f"negative for {rule_id} wrongly caught: {case!r}"
