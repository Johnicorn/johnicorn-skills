from pathlib import Path
import yaml

ORACLE = Path(__file__).parents[2] / "contracts" / "phase1a-acceptance.v1.yaml"


def test_oracle_is_valid_yaml_and_complete():
    data = yaml.safe_load(ORACLE.read_text(encoding="utf-8"))   # round-5: persona_markers was invalid YAML
    assert isinstance(data["persona_markers"], list)            # must be a clean list, no inline mapping key
    assert data["model"]["K_runs"] == 5
    for fx in data["fixtures"]:
        # A-input mapping present (round-5 B2: brief/input/address must map to the A contract)
        assert {"id", "intent", "profile"} <= set(fx)
        assert fx["profile"] in ("style_only", "lexical", "morphology", "full")
        assert any(r["kind"] == "register" for r in fx.get("requirements", []))
