from __future__ import annotations
import re, unicodedata
from .contract import Requirement

# morphology-free Tu/Jūs proxy (mirrors phase1a-acceptance.v1.yaml tu_violation_proxy)
JUS_PRONOUNS = ["jūs", "jums", "jūsu", "jūsos", "jūsim", "jūsuprāt"]
JUS_VERBS = ["esat", "esiet", "varat", "variet", "gribat", "gribiet",
             "sazinieties", "uzziniet", "izmantojiet", "atcerieties", "ņemiet"]
LETTER = r"a-zāčēģīķļņōŗšūž"


def _norm(s: str) -> str:
    return unicodedata.normalize("NFC", s).lower()


def _tu_violation(text: str) -> bool:
    t = _norm(text)
    for w in JUS_PRONOUNS + JUS_VERBS:
        if re.search(rf"(?<![{LETTER}]){re.escape(w)}(?![{LETTER}])", t):
            return True
    return False


def requirement_preservation(text: str, requirements: list[Requirement]) -> str:
    result = "pass"
    for req in requirements:
        if req.kind in ("fact", "quote", "term"):
            if _norm(req.value) not in _norm(text):
                return "fail"
        elif req.kind == "register":
            if req.value == "Tu" and _tu_violation(text):
                return "fail"
            # other register values: not machine-checkable in Phase 1
            if req.value != "Tu":
                result = "indeterminate"
        else:
            result = "indeterminate"
    return result
