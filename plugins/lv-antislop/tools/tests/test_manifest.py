from pathlib import Path
import pytest
from b3.manifest import load_manifest

MANIFEST = Path(__file__).parents[2] / "contracts" / "b3-style-manifest.v1.yaml"

def test_manifest_loads_and_is_valid():
    m = load_manifest(MANIFEST)
    # version must be consistent (round-5 bug: comments said 1.0.0, meta said 1.1.0)
    assert m.version == "1.1.0"
    # every rule has id, kind, severity and exactly one pattern kind
    ids = set()
    for r in m.rules:
        assert r.id and r.kind and r.severity in ("issue", "diagnostic")
        assert r.id not in ids, f"duplicate rule id {r.id}"
        ids.add(r.id)
        kinds = [k for k in ("pattern_literal", "pattern_word", "pattern_regex") if getattr(r, k)]
        assert len(kinds) <= 1
        if r.kind == "density":
            assert r.density is not None
        else:
            assert len(kinds) == 1, f"{r.id} needs exactly one pattern"

def test_density_report_fields_match_schema():
    m = load_manifest(MANIFEST)
    # round-5 bug: tiek.reports used word_tokens; schema declared denominator_word_tokens
    assert "denominator_word_tokens" in m.schema["density_report_schema"]
    tiek = next(r for r in m.rules if r.id == "tiek.density")
    assert tiek.density["denominator"] == "word_tokens"
