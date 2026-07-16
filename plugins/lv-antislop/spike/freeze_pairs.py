"""2b minimal-pairs kolekcijas freeze + verify (§12 protokols).

Hash konvencija: SHA-256 pār faila BAITIEM kanoniskajā pirms-haša formā —
ar rindu `  frozen: true` un rindu `  frozen_sha256: null`. Freeze ieraksta
hash vērtību; verify to izņem, pārrēķina un salīdzina. Tātad hash sedz visu
saturu (headeri, pārus, malformed komplektu), izņemot pašu hash lauku.

  python spike/freeze_pairs.py freeze   # atsakās, ja < 50 validated/ģimenē
  python spike/freeze_pairs.py verify   # exit 0 = fails atbilst iesaldētajam
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

import yaml

PAIRS = Path(__file__).resolve().parent.parent / "contracts" / "2b-minimal-pairs.v1.yaml"
FROZEN_LINE = re.compile(rb"^(  frozen: )(\S+)$", re.M)
SHA_LINE = re.compile(rb"^(  frozen_sha256: )(\S+)$", re.M)


def canonical(raw: bytes) -> bytes:
    raw, n1 = FROZEN_LINE.subn(rb"\g<1>true", raw, count=1)
    raw, n2 = SHA_LINE.subn(rb"\g<1>null", raw, count=1)
    if n1 != 1 or n2 != 1:
        raise SystemExit("KĻŪDA: meta blokā nav tieši pa vienai frozen/frozen_sha256 rindai.")
    return raw


def main(command: str) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    raw = PAIRS.read_bytes()
    digest = hashlib.sha256(canonical(raw)).hexdigest()
    data = yaml.safe_load(raw.decode("utf-8"))

    if command == "freeze":
        counts = {"amod": 0, "nsubj": 0}
        for pair in data.get("pairs", []):
            if not pair.get("example") and pair.get("status") == "validated":
                counts[pair.get("family")] = counts.get(pair.get("family"), 0) + 1
        short = {f: c for f, c in counts.items() if c < 50}
        if short:
            print(f"ATTEIKTS: nepietiek validēto pāru: {short}")
            return 1
        if data.get("meta", {}).get("frozen") is True:
            print("Jau iesaldēts — nekas nemainīts. Pārbaudei: verify.")
            return 0
        frozen = SHA_LINE.sub(
            b"  frozen_sha256: \"" + digest.encode() + b"\"", canonical(raw), count=1)
        PAIRS.write_bytes(frozen)
        print(f"IESALDĒTS: amod {counts['amod']}, nsubj {counts['nsubj']} validated.")
        print(f"SHA-256: {digest}")
        return 0

    if command == "verify":
        meta = data.get("meta", {})
        stored = meta.get("frozen_sha256")
        if meta.get("frozen") is not True or not stored:
            print("NAV iesaldēts (frozen != true vai hash tukšs).")
            return 1
        if stored == digest:
            print(f"VERIFY OK: {digest}")
            return 0
        print(f"NESAKRĪT: fails ir mainīts pēc freeze!\n  glabātais:  {stored}\n  faktiskais: {digest}")
        return 1

    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else ""))
