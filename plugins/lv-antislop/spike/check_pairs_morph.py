"""Mehāniska drafted/validated pāru pārbaude pret Tēzaura formu indeksu (2b QA).

Katram pārim ar bad != null pārbauda:
  1. good/bad tokenu skaits vienāds un atšķiras TIEŠI viena pozīcija;
  2. flag_token == atšķirīgais bad tokens (precīza virsmas forma, ar lielo burtu);
  3. abas atšķirīgās formas eksistē Tēzaura vārdformu indeksā un dala >= 1 lemmu
     (t.i., sliktā forma ir tās pašas leksēmas cita locījuma forma, ne drukas kļūda);
  4. visi pārējie tokeni abos teikumos eksistē indeksā (drukas kļūdu tīkls).
Negatīvajām kontrolēm (bad = null) pārbauda tikai good tokenus (4. punkts).

Tas NAV saskaņas pārbaudītājs: pazīmju deltas (Case/Number/Gender/Person) indeksā
nav — tās paliek Jāņa validācijas atbildība. Skripts ķer tikai mehāniski
pārbaudāmo: formu eksistenci, viena-tokena īpašību un flag_token konsekvenci.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from b.index import norm                    # noqa: E402
from b.ondisk import SqliteWordforms        # noqa: E402

PAIRS = ROOT / "contracts" / "2b-minimal-pairs.v1.yaml"
# Noklusējums = dev izkārtojums; publiskā klonā padod savu ceļu kā 1. argumentu.
DB = (Path(sys.argv[1]) if len(sys.argv) > 1
      else ROOT / "vendor" / "tezaurs" / "index" / "b2" / "wordforms.sqlite")
TOKEN = re.compile(r"[\w']+", re.UNICODE)

# Īpašvārdi, kuru nav sugasvārdu indeksā — apzināti pieļauti.
PROPER = {"anna", "annu", "pēteris", "liepājā"}


def toks(text: str) -> list[str]:
    return TOKEN.findall(text or "")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    data = yaml.safe_load(PAIRS.read_text(encoding="utf-8"))
    wf = SqliteWordforms(DB)
    hard: list[str] = []
    soft: list[str] = []
    checked = negatives = 0

    def known(token: str) -> bool:
        return norm(token) in PROPER or wf.get(norm(token)) is not None

    for pair in data.get("pairs", []):
        pid, good, bad, flag = pair.get("id"), pair.get("good"), pair.get("bad"), pair.get("flag_token")
        if not good:
            continue
        for token in toks(good):
            if not known(token):
                soft.append(f"{pid}: good tokens nav indeksā: {token}")
        if bad is None:
            negatives += 1
            continue
        checked += 1
        g, b = toks(good), toks(bad)
        if len(g) != len(b):
            hard.append(f"{pid}: atšķiras tokenu skaits ({len(g)} pret {len(b)})")
            continue
        diff = [i for i, (x, y) in enumerate(zip(g, b)) if x != y]
        if len(diff) != 1:
            hard.append(f"{pid}: atšķirīgo pozīciju skaits ir {len(diff)}, jābūt tieši 1")
            continue
        i = diff[0]
        if b[i] != flag:
            hard.append(f"{pid}: flag_token {flag!r} != atšķirīgais tokens {b[i]!r}")
        good_lemmas = wf.get(norm(g[i]))
        bad_lemmas = wf.get(norm(b[i]))
        if good_lemmas is None:
            hard.append(f"{pid}: labā forma {g[i]!r} nav Tēzaura indeksā")
        if bad_lemmas is None:
            hard.append(f"{pid}: sliktā forma {b[i]!r} nav Tēzaura indeksā")
        if good_lemmas and bad_lemmas and not set(good_lemmas) & set(bad_lemmas):
            hard.append(
                f"{pid}: formas nedala lemmu (good {g[i]!r} -> {good_lemmas}; "
                f"bad {b[i]!r} -> {bad_lemmas})")
        for token in b:
            if not known(token):
                soft.append(f"{pid}: bad tokens nav indeksā: {token}")

    wf.close()
    print(f"Pārbaudīti {checked} pāri ar pārkāpumu + {negatives} negatīvās kontroles.")
    if soft:
        print("\nBRĪDINĀJUMI (nav indeksā — īpašvārds vai reta forma, apskati ar aci):")
        for line in dict.fromkeys(soft):
            print(f"- {line}")
    if hard:
        print("\nKĻŪDAS:")
        for line in hard:
            print(f"- {line}")
        return 1
    print("\nMEHĀNISKO KĻŪDU NAV.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
