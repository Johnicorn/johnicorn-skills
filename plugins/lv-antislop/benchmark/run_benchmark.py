"""lv-antislop instrukciju slāņa benchmarks — cross-model A/B pret B3 vārtiem.

Dizains:
  - 10 reālistiski LV copy uzdevumi (tipiskie slop magnēti).
  - Arms A (bāzes): cits modelis (OpenAI Codex CLI) raksta bez skila norādēm.
  - Arms B (skils): tas pats modelis + lv-antislop operatīvās prasības promptā
    (core move tabula, aktīvie likumi, red flags — SKILL.md izvilkums).
  - Metrika: deterministiskais B3 stila skeneris (iesaldētais manifests
    v1.1.0) — issue flagi / 1000 tokenu + kopējie flagi + tiek blīvums.

Ko šis mēra un ko NE (godīgi): mēra, vai instrukciju slānis samazina
DETERMINISTISKI atpazīstamOS AI-slop signālus arī citam modelim, ne šī
benchmarka autoram. Tas NAV galīgais teksta kvalitātes mērījums (to dod §7
efektivitātes pilots ar cilvēku edit-laiku) un metrika pēc uzbūves ir tā paša
skila definētais signālu saraksts — benchmarks pierāda pārnesi, ne gaumi.

Palaišana (prasa codex CLI; ģenerēšana ~10–20 min):
  python benchmark/run_benchmark.py            # ģenerē + vērtē
  python benchmark/run_benchmark.py --score    # tikai pārvērtē esošos failus
"""
from __future__ import annotations

import json
import re
import shutil
import statistics
import subprocess
import sys
import time
from pathlib import Path

# Windows: npm shims ir .cmd faili — kailais nosaukums CreateProcess nepazīst.
CODEX = shutil.which("codex") or "codex"

BENCH_DIR = Path(__file__).resolve().parent
ROOT = BENCH_DIR.parent
sys.path.insert(0, str(ROOT / "tools"))

from b3.manifest import load_manifest  # noqa: E402
from b3.scanner import WORD_TOKEN, scan  # noqa: E402

OUT_DIR = BENCH_DIR / "outputs-v2"
RESULTS = BENCH_DIR / "benchmark-results-v2.json"
MANIFEST = load_manifest(ROOT / "contracts" / "b3-style-manifest.v1.yaml")

# 1. kārtas (140–170 vārdu mārketinga teksti, mape outputs/) godīgais rezultāts:
# NULLE abos armos — īsos tekstos ģenerators manifestu nepārkāpj arī bez skila.
# 2. kārta tāpēc provocē kancelejas reģistru: garāki, formāli-institucionāli žanri.
PROMPTS = {
    "pasvaldiba": "pašvaldības paziņojumu iedzīvotājiem par plānotu ūdens padeves pārtraukumu",
    "es-fonds": "Eiropas Savienības fonda līdzfinansēta projekta publicitātes aprakstu uzņēmuma mājaslapai",
    "banka": "bankas paziņojumu klientiem par izmaiņām pakalpojumu cenrādī",
    "apdrosinasana": "apdrošināšanas produkta noteikumu skaidrojumu klientiem",
    "gada-parskats": "valsts iestādes gada publiskā pārskata ievadu",
    "prese": "IT uzņēmuma preses relīzi par jauna produkta laišanu tirgū",
    "augstskola": "augstskolas studiju programmas aprakstu uzņemšanas katalogam",
    "nvo-parskats": "nevalstiskās organizācijas gada darbības kopsavilkumu ziedotājiem",
    "kvalitate": "ražošanas uzņēmuma kvalitātes politikas lapu",
    "telekoms": "telekomunikāciju operatora paziņojumu par tīkla modernizāciju",
}

BASE_TASK = ("Uzraksti latviešu valodā {task}. Apjoms: aptuveni 320–420 vārdu. "
             "Atbildē tikai pats teksts — bez virsrakstiem, komentāriem un formatējuma.")

SKILL_EXCERPT = """Ievēro šīs rakstīšanas prasības (lv-antislop):

Latviešu valodas noklusējums LLM tekstiem ir kancelejas reģistrs — to aktīvi jāpagriež uz publicistiku: analītiska precizitāte, personīga balss, aktīvi verbi, teikuma garuma variācija, mērena emocionalitāte, ironija kā bāzes līnija.

Aizvietojumi:
- "tiek nodrošināts atbalsts" -> "mēs atbalstām" (aktīvā balss, konkrēts subjekts)
- "veikt analīzi" -> "analizēt" (verbs, ne lietvārda konstrukcija)
- "Ir svarīgi atzīmēt, ka ..." -> dzēs ievadu, saki faktu
- "Turklāt / tādējādi / līdz ar to" -> bez pārejas vārda, lai semantika nes
- vienādi vidēja garuma teikumi -> sajauc 5–30 vārdu teikumus; sekcijas beigās īsa verdikta rinda
- "piedāvājam visaptverošus risinājumus" -> konkrēti verbi + specifisks lietvārds

Aktīvie likumi: aktīvā balss visur, kur iespējams; aizvieto lietvārdu-verbu pārus ar verbiem; sajauc teikumu garumus; iepin partikulas (nu, jau, taču, gan, vien), kur tās ritmā iederas; galvenā informācija teikuma beigās; konkrēta detaļa (skaitlis, vieta, nosaukums) sit jebkuru superlatīvu; bez amerikāņu entuziasma un izsaukuma zīmēm.

Aizliegts: tiek + divdabis konstrukciju kaudzes; nodrošināt/veikt/īstenot bez konkrēta objekta; turklāt, tādējādi, līdz ar to; tukšie ievadi (ir svarīgi atzīmēt, jāuzsver, ka); trīs teikumi pēc kārtas, kas sākas ar Mēs; teksts, kas derētu jebkura uzņēmuma mājaslapai."""


def codex_generate(prompt: str, out_path: Path) -> float:
    # Promptu padod caur stdin (pozicionālais "-"): npm .cmd šims argv saturu
    # laiž cauri cmd.exe, kur pēdiņas un > promptā salauž rindu (WinError klase,
    # noķerta 2026-07-16). Prompta failu saglabā blakus — caurspīdībai.
    prompt_path = out_path.with_name(out_path.stem + ".prompt.txt")
    prompt_path.write_text(prompt, encoding="utf-8")
    started = time.perf_counter()
    with prompt_path.open("rb") as handle:
        subprocess.run(
            [CODEX, "exec", "-s", "read-only",
             "-c", 'model_reasoning_effort="low"', "-o", str(out_path), "-"],
            stdin=handle, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            check=True, timeout=600)
    return time.perf_counter() - started


def score(text: str) -> dict:
    """Deterministiskā metrika: manifests + skila deklarēto likumu teksta statistika.

    Papildmetrikas ir PRE-deklarētas no SKILL.md aktīvajiem likumiem (teikumu
    garuma variācija, Mēs-sākumi, kancelejas verbi, tiek blīvums, izsaukuma
    zīmes) — mēra likumu ievērošanu, ne post-hoc izvēlētus rādītājus.
    """
    flags = scan(text, MANIFEST)
    tokens = len(WORD_TOKEN.findall(text))
    issues = [f for f in flags if f.severity == "issue"]
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    lengths = [len(WORD_TOKEN.findall(s)) for s in sentences] or [0]
    per_1k = (lambda n: round(1000 * n / tokens, 2) if tokens else 0.0)
    return {
        "tokens": tokens,
        "sentences": len(sentences),
        "b3_issues": len(issues),
        "b3_flags_total": len(flags),
        "issues_per_1k": per_1k(len(issues)),
        "diagnostics_per_1k": per_1k(len(flags) - len(issues)),
        "tiek_per_1k": per_1k(len(re.findall(r"\btiek\b", text, flags=re.IGNORECASE))),
        "kanc_verbs_per_1k": per_1k(len(re.findall(
            r"\b(?:nodrošin|īsteno|realizē)\w*|\bveic\w*\s+\w+(?:šanu|ciju)\b",
            text, flags=re.IGNORECASE))),
        "mes_sentence_starts": sum(s.casefold().startswith("mēs") for s in sentences),
        "exclamations": text.count("!"),
        "sentence_len_stdev": round(statistics.pstdev(lengths), 2),
        "issue_rules": sorted({f.rule_id for f in issues}),
    }


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    generate = "--score" not in sys.argv
    OUT_DIR.mkdir(exist_ok=True)
    rows = []
    for key, task in PROMPTS.items():
        row = {"prompt": key, "task": task}
        for arm, suffix in (("A", ""), ("B", "\n\n" + SKILL_EXCERPT)):
            out_path = OUT_DIR / f"{key}-{arm}.txt"
            if generate:
                seconds = codex_generate(BASE_TASK.format(task=task) + suffix, out_path)
                print(f"{key}/{arm}: ģenerēts {seconds:.0f} s")
            text = out_path.read_text(encoding="utf-8").strip()
            row[arm] = score(text)
        rows.append(row)
        print(f"{key}: A {row['A']['issues_per_1k']}/1k pret B {row['B']['issues_per_1k']}/1k")

    def med(arm: str, field: str) -> float:
        return round(statistics.median(r[arm][field] for r in rows), 2)

    def med_pair(field: str) -> dict:
        return {"A_base": med("A", field), "B_skill": med("B", field)}

    summary = {
        "prompts": len(rows),
        "generator": "OpenAI Codex CLI (konfigurācijas modelis; model_reasoning_effort=low)",
        "metric": "B3 manifests v1.1.0 + SKILL.md aktīvo likumu teksta statistika",
        "median_tokens": med_pair("tokens"),
        "median_issues_per_1k": med_pair("issues_per_1k"),
        "median_diagnostics_per_1k": med_pair("diagnostics_per_1k"),
        "median_tiek_per_1k": med_pair("tiek_per_1k"),
        "median_kanc_verbs_per_1k": med_pair("kanc_verbs_per_1k"),
        "median_sentence_len_stdev": med_pair("sentence_len_stdev"),
        "total_mes_sentence_starts": {"A_base": sum(r["A"]["mes_sentence_starts"] for r in rows),
                                      "B_skill": sum(r["B"]["mes_sentence_starts"] for r in rows)},
        "total_exclamations": {"A_base": sum(r["A"]["exclamations"] for r in rows),
                               "B_skill": sum(r["B"]["exclamations"] for r in rows)},
        "total_issues": {"A_base": sum(r["A"]["b3_issues"] for r in rows),
                         "B_skill": sum(r["B"]["b3_issues"] for r in rows)},
    }
    RESULTS.write_text(json.dumps({"summary": summary, "rows": rows}, ensure_ascii=False, indent=2) + "\n",
                       encoding="utf-8")
    print("\nKOPSAVILKUMS")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
