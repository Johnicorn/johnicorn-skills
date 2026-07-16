from __future__ import annotations
from dataclasses import dataclass
import unicodedata

FORMAT_VERSION = "1"

def norm(s: str) -> str:
    """Canonical dictionary-key normalization: NFC + lowercase. The ONE place the
    fold is defined (spelling/morphology import it). Latvian needs no casefold (no
    ß / final-sigma). Distinct from b3.normalize, which preserves case for spans."""
    return unicodedata.normalize("NFC", s).lower()

def _merge(wordforms) -> dict[str, list[str]]:
    """norm(key) -> sorted, deduped union of lemma lists. Deterministic regardless
    of input key order: colliding keys merge instead of last-wins. Lemma STRINGS
    are not re-normalized (they join to freq keys as given)."""
    acc: dict[str, set[str]] = {}
    for k, lemmas in wordforms.items():
        acc.setdefault(norm(k), set()).update(lemmas)
    return {k: sorted(v) for k, v in acc.items()}

@dataclass(frozen=True)
class Lexicon:
    """B1: normalized-once set of known wordforms. Queried by membership only."""
    forms: frozenset[str]

    @classmethod
    def from_words(cls, words) -> "Lexicon":
        return cls(frozenset(norm(w) for w in words))

@dataclass                      # NOT frozen: wraps mutable dicts (frozen would be a shallow lie + break __hash__)
class WordformIndex:
    """B2: normalized-once form -> lemmas, plus lemma frequency. Queried by .get only."""
    forms: dict[str, list[str]]
    freq: dict[str, int]

    @classmethod
    def from_mapping(cls, wordforms, freq=None) -> "WordformIndex":
        return cls(_merge(wordforms), dict(freq or {}))

import hashlib, json
from pathlib import Path

_FILES = ("forms.txt", "wordforms.tsv", "freq.tsv")
_WS = ("\t", "\n", "\r", " ", "\x0b", "\x0c")   # v1: single-token forms/keys/lemmas only

def _reject_ws(s: str, kind: str) -> None:
    if not s:
        raise ValueError(f"{kind} is empty (v1 requires a non-empty token)")
    if any(c in s for c in _WS):
        raise ValueError(f"{kind} contains whitespace/tab/newline (v1 limitation): {s!r}")

def _sha256(path: Path) -> str:
    # Stream the file in fixed-size blocks: hashing must not materialize a
    # multi-GB wordforms.tsv in RAM (that would break the memory-bounded build
    # and inflate load_index's peak RSS). Same digest as sha256(read_bytes()).
    with path.open("rb") as fh:
        return hashlib.file_digest(fh, "sha256").hexdigest()

def _write_forms(path: Path, forms) -> int:
    """Normalize, validate, and write B1 forms in the v1 on-disk format."""
    nforms = sorted({norm(w) for w in forms})
    for w in nforms:
        _reject_ws(w, "form")
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        for w in nforms:
            fh.write(w + "\n")
    return len(nforms)

def _validate_wordform_item(key: str, lemmas) -> None:
    _reject_ws(key, "wordform key")
    if not lemmas:
        raise ValueError(f"wordform {key!r} has an empty lemma list")
    for lemma in lemmas:
        _reject_ws(lemma, "lemma")
        if "," in lemma:
            raise ValueError(f"lemma {lemma!r} contains the ',' separator (v1 limitation)")

def _write_wordforms_from_sorted_items(path: Path, items) -> int:
    """Write already key-sorted (key, sorted-lemmas) items in the v1 format."""
    count = 0
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        for key, lemmas in items:
            _validate_wordform_item(key, lemmas)
            fh.write(f"{key}\t{','.join(lemmas)}\n")
            count += 1
    return count

def _write_freq(path: Path, freq) -> int:
    """Validate and write lemma frequencies in the v1 on-disk format."""
    nfreq: dict[str, int] = {}
    for key, value in (freq or {}).items():
        key = str(key)
        _reject_ws(key, "freq key")
        nfreq[key] = int(value)
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        for key, value in sorted(nfreq.items()):
            fh.write(f"{key}\t{value}\n")
    return len(nfreq)

def _write_manifest(out: Path, *, forms: int, wordforms: int, freq: int) -> dict:
    manifest = {
        "format_version": FORMAT_VERSION,
        "counts": {"forms": forms, "wordforms": wordforms, "freq": freq},
        "sha256": {name: _sha256(out / name) for name in _FILES},
    }
    (out / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n")
    return manifest

def build_index(forms, wordforms, freq, out_dir) -> dict:
    """Write a deterministic, inspectable on-disk index + manifest. Same inputs ->
    byte-identical files -> identical SHA-256. Rejects separator chars and empty
    lemma lists (v1: single-token forms/keys/lemmas, every key >= 1 lemma)."""
    out = Path(out_dir)

    # Validate-before-write: materialize + check EVERY input before opening any
    # output file, so invalid input never truncates/partly-replaces an existing
    # index (failure atomicity — the writers still re-validate, idempotently).
    forms = sorted({norm(w) for w in forms})      # materialize (forms may be a generator)
    for w in forms:
        _reject_ws(w, "form")
    items = sorted(_merge(wordforms).items())     # norm keys, sorted/deduped lemma union
    for key, lemmas in items:
        _validate_wordform_item(key, lemmas)
    for key, value in (freq or {}).items():
        _reject_ws(str(key), "freq key")
        int(value)

    out.mkdir(parents=True, exist_ok=True)
    return _write_manifest(
        out,
        forms=_write_forms(out / "forms.txt", forms),
        wordforms=_write_wordforms_from_sorted_items(out / "wordforms.tsv", items),
        freq=_write_freq(out / "freq.tsv", freq),
    )

def load_index(in_dir) -> tuple[Lexicon, WordformIndex]:
    """Load + verify (format_version, manifest shape, per-file SHA-256) an on-disk index."""
    d = Path(in_dir)
    manifest = json.loads((d / "manifest.json").read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise ValueError("manifest is not a JSON object")
    if manifest.get("format_version") != FORMAT_VERSION:
        raise ValueError(
            f"index format_version {manifest.get('format_version')!r} != {FORMAT_VERSION!r}")
    sha = manifest.get("sha256")
    if not isinstance(sha, dict) or any(name not in sha for name in _FILES):
        raise ValueError("manifest missing or malformed sha256 section")
    for name in _FILES:
        if _sha256(d / name) != sha[name]:
            raise ValueError(f"sha256 mismatch for {name} (index tampered or corrupt)")

    # split on LITERAL "\n" only (build writes newline="\n"; fields reject \n/\r) so a
    # Unicode line/para separator inside a field cannot be mistaken for a record break.
    forms = frozenset(
        l for l in (d / "forms.txt").read_text(encoding="utf-8").split("\n") if l)
    wf: dict[str, list[str]] = {}
    for line in (d / "wordforms.tsv").read_text(encoding="utf-8").split("\n"):
        if not line:
            continue
        k, lemmas = line.split("\t", 1)
        wf[k] = lemmas.split(",") if lemmas else []
    fr: dict[str, int] = {}
    for line in (d / "freq.tsv").read_text(encoding="utf-8").split("\n"):
        if not line:
            continue
        k, c = line.split("\t", 1)
        fr[k] = int(c)
    return Lexicon(forms=forms), WordformIndex(forms=wf, freq=fr)
