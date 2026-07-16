from __future__ import annotations
from dataclasses import dataclass, field
from .index import norm, WordformIndex

RARE_THRESHOLD = 100          # lemma frequency below this = rare (down-weight, not a flag)

@dataclass
class B2Result:
    status: str               # validated | no_known_analysis
    lemmas: list[str] = field(default_factory=list)
    rare: bool = False

def form_check(token: str, index: WordformIndex) -> B2Result:
    lemmas = index.forms.get(norm(token))
    if lemmas is None:
        return B2Result(status="no_known_analysis")
    rare = bool(index.freq) and all(index.freq.get(l, 0) < RARE_THRESHOLD for l in lemmas)
    return B2Result(status="validated", lemmas=list(lemmas), rare=rare)
