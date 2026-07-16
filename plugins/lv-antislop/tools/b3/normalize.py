from __future__ import annotations
import unicodedata

def normalize(text: str) -> tuple[str, list[int]]:
    """Return (NFC text, offset_map) where offset_map[i] = original code-point
    index that normalized char i starts at. Reversible for span translation."""
    norm_chars: list[str] = []
    omap: list[int] = []
    for orig_idx, ch in enumerate(text):
        composed = unicodedata.normalize("NFC", ch)
        for c in composed:
            norm_chars.append(c)
            omap.append(orig_idx)
    # collapse combining sequences that compose across chars
    joined = unicodedata.normalize("NFC", "".join(norm_chars))
    if joined == "".join(norm_chars):
        return "".join(norm_chars), omap
    # rebuild map for the fully-composed form, aligning by original index scan
    out_chars, out_map, oi = [], [], 0
    nfc = unicodedata.normalize("NFC", text)
    # map each NFC char back to the earliest original index whose prefix composes to it
    acc = ""
    for orig_idx, ch in enumerate(text):
        acc += ch
        comp = unicodedata.normalize("NFC", acc)
        while len(comp) > len(out_chars):
            out_chars.append(comp[len(out_chars)])
            out_map.append(orig_idx)
    return nfc, out_map
