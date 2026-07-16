"""Mehāniska 2b minimal-pairs kolekcijas pārbaude."""
from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

import yaml

DEFAULT = Path(__file__).resolve().parent.parent / "contracts" / "2b-minimal-pairs.v1.yaml"
FAMILIES = ("amod", "nsubj")
PHENOMENA = ("plain", "coordination", "indeclinable", "numeral", "syncretism", "ellipsis", "participle")
STATUSES = ("validated", "drafted", "todo")


def tokens(value: object) -> set[str]:
    return {token.casefold() for token in re.findall(r"\w+", str(value or ""), flags=re.UNICODE)}


def main(path: Path) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        print(f"KĻŪDA: nevar nolasīt YAML: {exc}")
        return 1
    pairs = data.get("pairs", []) if isinstance(data, dict) else []
    counts = {family: Counter() for family in FAMILIES}
    quota = Counter()
    errors: list[str] = []
    warnings: list[str] = []
    seen: set[str] = set()
    examples = 0
    fillins = 0
    for pair in pairs:
        pair_id = pair.get("id", "<bez id>")
        if pair_id in seen:
            errors.append(f"{pair_id}: dublēts id")
        seen.add(pair_id)
        family, status = pair.get("family"), pair.get("status")
        if family not in counts:
            errors.append(f"{pair_id}: neatpazīta ģimene {family!r}")
        elif not pair.get("example"):
            counts[family][status] += 1
        if pair.get("example"):
            examples += 1
            if status != "validated":
                errors.append(f"{pair_id}: paraugam jābūt validated")
        else:
            fillins += 1
        if status == "validated":
            for field in ("good", "feature", "phenomenon"):
                if not pair.get(field):
                    errors.append(f"{pair_id}: validated, bet trūkst {field}")
            good, bad, flag = pair.get("good"), pair.get("bad"), pair.get("flag_token")
            if bad is not None:
                if bad == good:
                    errors.append(f"{pair_id}: bad ir identisks good")
                if not flag or str(flag).casefold() not in tokens(bad):
                    errors.append(f"{pair_id}: flag_token nav tokens sliktajā teikumā")
            if not pair.get("example") and pair.get("phenomenon"):
                quota[pair["phenomenon"]] += 1
        if status not in STATUSES:
            errors.append(f"{pair_id}: nederīgs status {status!r}")
    meta = data.get("meta", {}) if isinstance(data, dict) else {}
    if meta.get("counts_only") != "validated":
        errors.append("meta.counts_only nav 'validated'")
    if examples != 10:
        warnings.append(f"Paraugu skaits ir {examples}, gaidīti 10")
    if fillins != 100:
        warnings.append(f"Aizpildāmo vietu skaits ir {fillins}, gaidītas 100")
    print("PROGRESS PĒC ĢIMENES")
    print("ģimene    validated  drafted  todo")
    for family in FAMILIES:
        print(f"{family:<10} {counts[family]['validated']:>9} {counts[family]['drafted']:>8} {counts[family]['todo']:>5}")
    print(f"\nPARAUGI: {examples} validēti")
    print("\nFENOMENU KVOTAS (tikai validated)")
    for phenomenon in PHENOMENA:
        target = 30 if phenomenon == "plain" else 4
        print(f"{phenomenon:<14} {quota[phenomenon]:>3}/{target}")
    freeze = all(counts[family]["validated"] >= 50 for family in FAMILIES)
    print(f"\nGATAVS FREEZE: {'jā' if freeze else 'nē'}")
    if warnings:
        print("\nBRĪDINĀJUMI:")
        for warning in warnings:
            print(f"- {warning}")
    if errors:
        print("\nKĻŪDAS:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("\nKĻŪDU NAV.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT))
