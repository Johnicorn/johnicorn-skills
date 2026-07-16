from __future__ import annotations
import re
from .index import norm, Lexicon

_URL = re.compile(r"https?://\S+|www\.\S+")
_NUMISH = re.compile(r"^[\d.,%€$+\-/]+$")

def _skippable(token: str) -> bool:
    if _URL.match(token) or _NUMISH.match(token):
        return True
    if token.isupper() and len(token) <= 5:          # abbreviation heuristic
        return True
    return False

def _edit1_hit(word: str, forms) -> str | None:
    letters = "aābcčdeēģhiījkļlļmnņoprsštuūvzž"
    for i in range(len(word) + 1):
        for c in letters:                            # insertion
            if (cand := word[:i] + c + word[i:]) in forms:
                return cand
    for i in range(len(word)):
        if (cand := word[:i] + word[i+1:]) in forms:     # deletion
            return cand
        for c in letters:                            # substitution
            if (cand := word[:i] + c + word[i+1:]) in forms:
                return cand
    return None

def spell_check(token: str, lexicon: Lexicon, allow: frozenset[str] = frozenset()):
    if _skippable(token):
        return None
    n = norm(token)
    if n in allow:
        return None
    if n in lexicon.forms:
        return None
    sugg = _edit1_hit(n, lexicon.forms)
    if sugg:
        return ("SPELLING_CANDIDATE", sugg)
    return ("UNKNOWN_TO_LEXICON", None)
