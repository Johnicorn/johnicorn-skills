from __future__ import annotations
import re, unicodedata
from pathlib import Path
import yaml
from a.gate_adapter import b3_gate

LETTER = r"a-zāčēģīķļņōŗšūž"


def load_oracle(path: str | Path) -> dict:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def _norm(s: str) -> str:
    return unicodedata.normalize("NFC", s).lower()


def _has_word(text: str, words: list[str]) -> bool:
    t = _norm(text)
    return any(re.search(rf"(?<![{LETTER}]){re.escape(_norm(w))}(?![{LETTER}])", t) for w in words)


def check_output(text: str, oracle: dict) -> dict:
    gate = b3_gate(text)
    issue_hits = sum(1 for f in gate.flags if f.severity == "issue")
    proxy = oracle["tu_violation_proxy"]
    tu_violation = _has_word(text, proxy["jus_pronouns"] + proxy["jus_verb_forms"])
    persona = _has_word(text, oracle["persona_markers"])
    ok = issue_hits == 0 and not tu_violation and not persona
    return {"b3_issue_hits": issue_hits, "tu_violation": tu_violation,
            "persona_marker": persona, "pass": ok}
