"""§12 2b spike runner — mērījumi pret IESALDĒTO minimal-pairs kolekciju.

Protokols (design §12, rev 7):
  1. Kolekcijas hash verify (freeze_pairs) — mērījums tikai pret iesaldēto failu.
  2. Čekeris = tools/b/agreement.py (lvnlp fp32, analyzer=False, margin-based
     abstention pēc §12 rev 6). Katrs teikums parsēts VIENREIZ; sliekšņa
     kalibrācija notiek pēc tam pār savāktajiem marginiem (in-spike, §12).
  3. Metrikas (pre-reģistrētās definīcijas):
       TP        = sliktajā teikumā atzīmēts tieši flag_token (casefold).
       FP        = jebkurš flags labajā teikumā / negatīvajā kontrolē, UN
                   flags sliktajā teikumā uz cita tokena (pa tokenam).
       precision = TP / (TP + FP), Vilsona 95% apakšējā robeža >= 0.90.
       coverage  = TP / pārkāpuma pāri (bad != null)          >= 0.70.
       abstention= abstain malas / visas vērtētās ģimeņu malas <= 0.30
                   (pār visiem teikumiem, abām pusēm; margin < slieksnis).
       latence   = warm mediāna <= 500 ms un cold <= 1000 ms / teikumam (rev 7).
       RSS       <= 2048 MB; malformed komplekts: crash/timeout = 0
                   (tukša ievade = gate guards, skaitās ok — probe MF-05).
  4. Sliekšņa izvēle: starp sliekšņiem, kur precision/coverage/abstention
     vārti izpildās, maksimizē coverage, tad precision LB, tad min abstention.

Izeja: 0 = spike PASS, 1 = spike FAIL, 2 = protokola kļūda.
Rezultāti: spike/spike-results.json (+ konsoles kopsavilkums).
"""
from __future__ import annotations

import concurrent.futures
import json
import math
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import psutil
import yaml

SPIKE_DIR = Path(__file__).resolve().parent
ROOT = SPIKE_DIR.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(SPIKE_DIR))

import freeze_pairs  # noqa: E402
from b.agreement import LvnlpAdapter, check_tokens  # noqa: E402

RESULTS_PATH = SPIKE_DIR / "spike-results.json"
GATES = {
    "precision_wilson_lb": 0.90,
    "coverage": 0.70,
    "abstention": 0.30,
    "cold_ms": 1000.0,
    "warm_median_ms": 500.0,
    "peak_rss_mb": 2048.0,
}


def wilson_lb(successes: int, n: int, z: float = 1.96) -> float:
    if n == 0:
        return 0.0
    p = successes / n
    denominator = 1 + z * z / n
    centre = p + z * z / (2 * n)
    spread = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (centre - spread) / denominator


def evaluate(records: list[dict], threshold: float | None) -> dict:
    """Pārrēķina metrikas pie dotā margin sliekšņa (bez pārparsēšanas)."""
    tp = fp = 0
    abstained = examined = 0
    misses: list[str] = []
    fp_items: list[str] = []
    for record in records:
        for side in ("good", "bad"):
            decisions = record.get(f"{side}_decisions")
            if decisions is None:
                continue
            flagged: dict[int, str] = {}
            for decision in decisions:
                examined += 1
                margin = decision["margin"]
                if threshold is not None and margin is not None and margin < threshold:
                    abstained += 1
                    continue
                if decision["flags"]:
                    flagged[decision["token_index"]] = decision["token"]
            if side == "good":
                fp += len(flagged)
                fp_items.extend(f"{record['id']}/good:{tok}" for tok in flagged.values())
            else:
                target = (record["flag_token"] or "").casefold()
                hit = any(tok.casefold() == target for tok in flagged.values())
                if hit:
                    tp += 1
                else:
                    misses.append(record["id"])
                extra = [tok for tok in flagged.values() if tok.casefold() != target]
                fp += len(extra)
                fp_items.extend(f"{record['id']}/bad:{tok}" for tok in extra)
    violations = sum(1 for r in records if r.get("bad_decisions") is not None)
    flags_total = tp + fp
    precision = tp / flags_total if flags_total else 0.0
    return {
        "threshold": threshold,
        "tp": tp,
        "fp": fp,
        "precision": round(precision, 4),
        "precision_wilson_lb": round(wilson_lb(tp, flags_total), 4),
        "coverage": round(tp / violations, 4) if violations else 0.0,
        "abstention": round(abstained / examined, 4) if examined else 0.0,
        "examined_edges": examined,
        "abstained_edges": abstained,
        "misses": misses,
        "false_positives": fp_items,
    }


def core_gates_pass(metrics: dict) -> bool:
    return (metrics["precision_wilson_lb"] >= GATES["precision_wilson_lb"]
            and metrics["coverage"] >= GATES["coverage"]
            and metrics["abstention"] <= GATES["abstention"])


def run_malformed(adapter: LvnlpAdapter, entries: list[dict]) -> list[dict]:
    results = []
    for entry in entries:
        text = entry["input"]
        if not text or not text.strip():
            results.append({"id": entry["id"], "status": "ok", "detail": "gate guards tukšu ievadi (MF-05)"})
            continue
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        future = executor.submit(adapter.parse_with_margins, text)
        try:
            future.result(timeout=30)
            executor.shutdown(wait=True)
            results.append({"id": entry["id"], "status": "ok", "detail": None})
        except concurrent.futures.TimeoutError:
            executor.shutdown(wait=False, cancel_futures=True)
            results.append({"id": entry["id"], "status": "timeout", "detail": "30 s"})
        except Exception as exc:  # noqa: BLE001 — spike reģistrē jebkuru avāriju
            executor.shutdown(wait=True)
            results.append({"id": entry["id"], "status": "exception",
                            "detail": f"{type(exc).__name__}: {str(exc)[:120]}"})
    return results


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    raw = freeze_pairs.PAIRS.read_bytes()
    digest = __import__("hashlib").sha256(freeze_pairs.canonical(raw)).hexdigest()
    data = yaml.safe_load(raw.decode("utf-8"))
    meta = data.get("meta", {})
    if meta.get("frozen") is not True or meta.get("frozen_sha256") != digest:
        print("PROTOKOLA KĻŪDA: kolekcija nav iesaldēta vai hash nesakrīt — spike aizliegts.")
        return 2
    pairs = [p for p in data["pairs"] if p.get("status") == "validated"]
    print(f"Kolekcija verificēta (sha256 {digest[:16]}…), {len(pairs)} validēti pāri.")

    process = psutil.Process()
    load_started = time.perf_counter()
    adapter = LvnlpAdapter()
    load_seconds = time.perf_counter() - load_started
    peak_rss = process.memory_info().rss

    records: list[dict] = []
    parse_ms: list[float] = []
    for pair in pairs:
        record = {"id": pair["id"], "family": pair["family"], "flag_token": pair.get("flag_token")}
        for side in ("good", "bad"):
            text = pair.get(side)
            if text is None:
                continue
            started = time.perf_counter()
            tokens, margins, _spans = adapter.parse_with_margins(text)
            parse_ms.append((time.perf_counter() - started) * 1000)
            peak_rss = max(peak_rss, process.memory_info().rss)
            record[f"{side}_decisions"] = [
                {"token_index": d.token_index, "token": tokens[d.token_index - 1]["text"],
                 "family": d.family, "margin": d.margin,
                 "flags": [f"{f.family}/{f.feature}" for f in d.flags]}
                for d in check_tokens(tokens, margins, margin_threshold=None)]
        records.append(record)

    cold_ms = parse_ms[0]
    warm = parse_ms[1:]
    warm_median = statistics.median(warm)
    warm_p95 = sorted(warm)[max(0, round(0.95 * (len(warm) - 1)))]
    peak_mb = round(peak_rss / (1024 * 1024), 1)

    malformed = run_malformed(adapter, data.get("malformed", []))
    malformed_ok = sum(1 for item in malformed if item["status"] == "ok")

    margins_seen = sorted({
        d["margin"] for r in records for side in ("good", "bad")
        for d in (r.get(f"{side}_decisions") or []) if d["margin"] is not None})
    sweep = [evaluate(records, None)] + [evaluate(records, threshold) for threshold in margins_seen]
    passing = [m for m in sweep if core_gates_pass(m)]
    chosen = (max(passing, key=lambda m: (m["coverage"], m["precision_wilson_lb"], -m["abstention"]))
              if passing else
              max(sweep, key=lambda m: (m["precision_wilson_lb"], m["coverage"])))

    verdict = {
        "precision_wilson_lb": chosen["precision_wilson_lb"] >= GATES["precision_wilson_lb"],
        "coverage": chosen["coverage"] >= GATES["coverage"],
        "abstention": chosen["abstention"] <= GATES["abstention"],
        "cold_le_1000ms": cold_ms <= GATES["cold_ms"],
        "warm_median_le_500ms": warm_median <= GATES["warm_median_ms"],
        "peak_rss_le_2048mb": peak_mb <= GATES["peak_rss_mb"],
        "malformed_no_crash": malformed_ok == len(malformed),
    }
    spike_pass = all(verdict.values())

    results = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "frozen_sha256": digest,
        "pairs_evaluated": len(pairs),
        "violation_pairs": sum(1 for r in records if r.get("bad_decisions") is not None),
        "model_id": adapter.model_id,
        "model_load_seconds": round(load_seconds, 2),
        "latency_ms": {"cold": round(cold_ms, 1), "warm_median": round(warm_median, 1),
                       "warm_p95": round(warm_p95, 1), "parses": len(parse_ms)},
        "peak_rss_mb": peak_mb,
        "malformed": malformed,
        "chosen": chosen,
        "sweep": [{k: m[k] for k in ("threshold", "tp", "fp", "precision_wilson_lb",
                                     "coverage", "abstention")} for m in sweep],
        "gates": GATES,
        "verdict": verdict,
        "spike_pass": spike_pass,
        "records": records,
    }
    RESULTS_PATH.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"\nModeļa ielāde: {load_seconds:.1f} s · parses: {len(parse_ms)}")
    print(f"Latence: cold {cold_ms:.0f} ms (≤1000) · warm mediāna {warm_median:.0f} ms (≤500) · p95 {warm_p95:.0f} ms")
    print(f"Peak RSS: {peak_mb} MB (≤2048) · malformed: {malformed_ok}/{len(malformed)} ok")
    threshold_display = "nav (bez abstention)" if chosen["threshold"] is None else f"{chosen['threshold']:.3f}"
    print(f"\nIzvēlētais margin slieksnis: {threshold_display}")
    print(f"TP {chosen['tp']} · FP {chosen['fp']} · precision {chosen['precision']}"
          f" (Wilson LB {chosen['precision_wilson_lb']}, ≥0.90)")
    print(f"coverage {chosen['coverage']} (≥0.70) · abstention {chosen['abstention']} (≤0.30)")
    if chosen["misses"]:
        print(f"Netrāpītie pāri ({len(chosen['misses'])}): {', '.join(chosen['misses'])}")
    if chosen["false_positives"]:
        print(f"FP ({len(chosen['false_positives'])}): {', '.join(chosen['false_positives'])}")
    print(f"\nSPIKE: {'PASS' if spike_pass else 'FAIL'}")
    for gate_name, ok in verdict.items():
        print(f"  {'✔' if ok else '✘'} {gate_name}")
    print(f"\nRezultāti: {RESULTS_PATH}")
    return 0 if spike_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
