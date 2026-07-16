from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import yaml

@dataclass
class Rule:
    id: str
    kind: str
    severity: str
    pattern_literal: list[str] | None = None
    pattern_word: list[str] | None = None
    pattern_regex: str | None = None
    density: dict | None = None
    replacement_hint: str | None = None

@dataclass
class Manifest:
    version: str
    schema: dict
    rules: list[Rule] = field(default_factory=list)

def load_manifest(path: str | Path) -> Manifest:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    meta, schema = data["meta"], data["schema"]
    rules: list[Rule] = []
    for raw in data["rules"]:
        density = None
        if raw.get("kind") == "density":
            density = {k: raw[k] for k in ("count_token", "denominator", "reports",
                                           "detect", "promotion_to_issue") if k in raw}
        rules.append(Rule(
            id=raw["id"], kind=raw["kind"], severity=raw["severity"],
            pattern_literal=raw.get("pattern_literal"),
            pattern_word=raw.get("pattern_word"),
            pattern_regex=raw.get("pattern_regex"),
            density=density, replacement_hint=raw.get("replacement_hint"),
        ))
    return Manifest(version=str(meta["version"]), schema=schema, rules=rules)
