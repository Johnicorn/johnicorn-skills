from __future__ import annotations
from b3.scanner import Flag, WORD_TOKEN
from .spelling import spell_check
from .morphology import form_check
from .index import Lexicon, WordformIndex

def analyze(
        text: str, lexicon: Lexicon, index: WordformIndex,
        allow: frozenset[str] = frozenset()) -> list[Flag]:
    flags: list[Flag] = []
    for m in WORD_TOKEN.finditer(text):
        tok = m.group(0)
        b1 = spell_check(tok, lexicon, allow)
        if b1 is None:
            continue                                  # known to B1 -> fine
        # B2 (wordform index) is the authority: validation overrides BOTH B1 outcomes
        # (a token that looks like a typo of a known word may be a valid inflection, e.g.
        #  "alu" is edit-1 of "alus" but is itself a valid form).
        b2 = form_check(tok, index)
        if b2.status == "validated":
            continue
        kind, _sugg = b1
        if kind == "SPELLING_CANDIDATE":
            flags.append(Flag(m.start(), m.end(), "spelling.candidate", "issue", tok))
        else:  # UNKNOWN_TO_LEXICON
            flags.append(Flag(m.start(), m.end(), "morphology.no_known_analysis", "diagnostic", tok))
    return flags
