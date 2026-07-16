from __future__ import annotations
from dataclasses import dataclass
import re
from .manifest import Manifest, Rule
from .normalize import normalize

LETTER = r"A-Za-zĀāČčĒēĢģĪīĶķĻļŅņŌōŖŗŠšŪūŽž"
WORD_TOKEN = re.compile(rf"[{LETTER}]+")
URL_RE = re.compile(r"https?://\S+|www\.\S+")
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")

@dataclass(frozen=True)
class Flag:
    start: int
    end: int
    rule_id: str
    severity: str
    observed: str

def _auto_exclusions(text: str) -> list[tuple[int, int]]:
    ex = [(m.start(), m.end()) for m in URL_RE.finditer(text)]
    ex += [(m.start(), m.end()) for m in EMAIL_RE.finditer(text)]
    return ex

def _excluded(s: int, e: int, ranges: list[tuple[int, int]]) -> bool:
    return any(s < re_ and e > rs for rs, re_ in ranges)

def _compile_rule(rule: Rule) -> re.Pattern | None:
    if rule.pattern_literal:
        alt = "|".join(re.escape(p) for p in rule.pattern_literal)
        return re.compile(alt, re.IGNORECASE | re.UNICODE)
    if rule.pattern_word:
        alt = "|".join(re.escape(w) for w in rule.pattern_word)
        return re.compile(rf"(?<![{LETTER}])(?:{alt})(?![{LETTER}])", re.IGNORECASE | re.UNICODE)
    if rule.pattern_regex:
        return re.compile(rule.pattern_regex, re.IGNORECASE | re.UNICODE)
    return None

def scan(text: str, manifest: Manifest, excluded_ranges=None) -> list[Flag]:
    norm, _omap = normalize(text)
    exclusions = list(excluded_ranges or []) + _auto_exclusions(norm)
    raw: list[Flag] = []
    for rule in manifest.rules:
        if rule.kind == "density":
            continue  # Task 7
        pat = _compile_rule(rule)
        if not pat:
            continue
        for m in pat.finditer(norm):
            if _excluded(m.start(), m.end(), exclusions):
                continue
            raw.append(Flag(m.start(), m.end(), rule.id, rule.severity, m.group(0)))
    return _resolve_overlaps(raw)

def _resolve_overlaps(flags: list[Flag]) -> list[Flag]:
    # longest match wins; tie -> lowest rule_id
    flags = sorted(flags, key=lambda f: (f.start, -(f.end - f.start), f.rule_id))
    kept: list[Flag] = []
    for f in flags:
        if any(f.start < k.end and f.end > k.start for k in kept):
            continue
        kept.append(f)
    return kept

def _tokens_outside(text: str, exclusions: list[tuple[int, int]]) -> list[str]:
    return [m.group(0) for m in WORD_TOKEN.finditer(text)
            if not _excluded(m.start(), m.end(), exclusions)]

def density_report(text: str, manifest: Manifest, excluded_ranges=None) -> dict:
    norm, _ = normalize(text)
    exclusions = list(excluded_ranges or []) + _auto_exclusions(norm)
    words = _tokens_outside(norm, exclusions)
    denom = len(words)
    out: dict = {}
    for rule in manifest.rules:
        if rule.kind != "density":
            continue
        tok = (rule.density or {}).get("count_token", "")
        if tok == "!":
            cnt = sum(1 for i, ch in enumerate(norm)
                      if ch == "!" and not _excluded(i, i + 1, exclusions))
        else:
            pat = re.compile(rf"(?<![{LETTER}]){re.escape(tok)}(?![{LETTER}])",
                             re.IGNORECASE | re.UNICODE)
            cnt = sum(1 for m in pat.finditer(norm)
                      if not _excluded(m.start(), m.end(), exclusions))
        out[rule.id] = {
            "tiek_count" if rule.id == "tiek.density" else "count": cnt,
            "denominator_word_tokens": denom,
            "per_1000": (cnt * 1000 / denom) if denom else 0.0,
            "severity": rule.severity,
        }
    return out
