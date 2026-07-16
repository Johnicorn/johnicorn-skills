from __future__ import annotations
from dataclasses import dataclass, field

@dataclass(frozen=True)
class Synonym:
    surface: str
    lemma: str
    source: str            # tezaurs | wordnet
    sense_id: str | None = None

@dataclass(frozen=True)
class LexEntry:
    lemma: str
    sense_id: str | None = None
    gloss: str | None = None

@dataclass
class LexResult:
    status: str                        # ok | not_found | unavailable
    query: str
    query_kind: str                    # surface | lemma
    resolved_lemmas: list[LexEntry] = field(default_factory=list)
    synonyms: list[Synonym] = field(default_factory=list)
    ambiguous: bool = False
    provenance: dict = field(default_factory=dict)   # {release, file, sha256}
