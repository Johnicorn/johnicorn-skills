from __future__ import annotations
import json, unicodedata
from pathlib import Path
from .contract import LexResult, LexEntry, Synonym

def _norm(s: str) -> str:
    return unicodedata.normalize("NFC", s).strip().lower()

def load_index(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))

def lookup(query: str, query_kind: str, index: dict | None) -> LexResult:
    if index is None:
        return LexResult(status="unavailable", query=query, query_kind=query_kind)
    prov = index.get("meta", {})
    key = _norm(query)
    entry = index.get("entries", {}).get(key) if key else None
    if not entry:
        return LexResult(status="not_found", query=query, query_kind=query_kind, provenance=prov)
    lemmas = [LexEntry(lemma=l["lemma"], sense_id=l.get("sense_id"), gloss=l.get("gloss"))
              for l in entry.get("lemmas", [])]
    syns = [Synonym(surface=s["surface"], lemma=s["lemma"], source=s["source"],
                    sense_id=s.get("sense_id")) for s in entry.get("synonyms", [])]
    ambiguous = len(lemmas) > 1
    return LexResult(status="ok", query=query, query_kind=query_kind,
                     resolved_lemmas=lemmas, synonyms=syns, ambiguous=ambiguous, provenance=prov)
