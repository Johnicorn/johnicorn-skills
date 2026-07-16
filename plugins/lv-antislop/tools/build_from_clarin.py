"""Build the local LV Antislop B2 index from pinned CLARIN assets."""
from __future__ import annotations

import argparse
import hashlib
import io
import os
from pathlib import Path
import sys
import time
import urllib.request
import zipfile


ISPELL_ZIP = "https://repository.clarin.lv/repository/xmlui/bitstream/handle/20.500.12574/160/tezaurs_2026_03.ispell.zip"
ISPELL_ZIP_SHA256 = "dfff0d8e29b9bf63827ae08e99b7b30406e97e04e0d2442f246bf5729996f25c"
WORDFORMS_ZIP = "https://repository.clarin.lv/repository/xmlui/bitstream/handle/20.500.12574/160/tezaurs_2026_3_wordforms_tei.xml.zip"
WORDFORMS_ZIP_SHA256 = "a0ac50c01adbb7db62ecd773de63a128bfcb3ed0cd0e532e0c1c3d8403278387"
FREQ_TSV = "https://repository.clarin.lv/repository/xmlui/bitstream/handle/20.500.12574/148/frequencies-lv-25K.tsv?sequence=1&isAllowed=y"
FREQ_TSV_SHA256 = "7cd81eb594b458d247b4a8701114f988ad3a60b7b605d8947579535145857002"

TEZAURS_ATTRIBUTION = (
    "Tēzaurs.lv 2026 (Summer Edition), Institute of Mathematics and Computer "
    "Science, University of Latvia (AILab). Licensed CC BY-SA 4.0."
)
FREQUENCY_ATTRIBUTION = (
    "Mikus Grasmanis, Baiba Valkovska, Kristīne Levāne-Petrova (2025-12-19): "
    "Latvian Word Frequency Dataset (25K lemmas). AiLab IMCS UL. "
    "http://hdl.handle.net/20.500.12574/148. Licensed CC BY-SA 4.0."
)

TOOLS_DIR = Path(__file__).resolve().parent
PLUGIN_ROOT = TOOLS_DIR.parent


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        while chunk := file.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def has_expected_sha256(path: Path, expected: str) -> bool:
    return path.is_file() and sha256(path) == expected


def download(url: str, destination: Path, expected_sha256: str) -> None:
    temporary = destination.with_name(destination.name + ".part")
    temporary.unlink(missing_ok=True)
    started = time.monotonic()
    print(f"Downloading {url}")
    try:
        with urllib.request.urlopen(url) as response, temporary.open("wb") as output:
            while chunk := response.read(1024 * 1024):
                output.write(chunk)
        observed_sha256 = sha256(temporary)
        if observed_sha256 != expected_sha256:
            raise RuntimeError(
                f"SHA-256 mismatch for {destination.name}: "
                f"expected {expected_sha256}, got {observed_sha256}")
        os.replace(temporary, destination)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
    print(f"Downloaded {destination.name} in {time.monotonic() - started:.1f}s")


def ensure_asset(
        url: str, destination: Path, expected_sha256: str, skip_download: bool) -> Path:
    if has_expected_sha256(destination, expected_sha256):
        print(f"Verified existing {destination.name}")
        return destination
    if skip_download:
        if destination.exists():
            observed_sha256 = sha256(destination)
            raise RuntimeError(
                f"--skip-download requires a matching {destination.name}: "
                f"expected {expected_sha256}, got {observed_sha256}")
        raise RuntimeError(
            f"--skip-download requires {destination} with SHA-256 {expected_sha256}")
    if destination.exists():
        print(f"Existing {destination.name} does not match its pinned SHA-256; replacing it")
    download(url, destination, expected_sha256)
    if not has_expected_sha256(destination, expected_sha256):
        raise RuntimeError(f"SHA-256 verification failed for {destination}")
    return destination


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build LV Antislop's local B2 index from pinned CLARIN assets.")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=PLUGIN_ROOT / "vendor",
        help="local data directory (default: plugin_root/vendor)",
    )
    parser.add_argument(
        "--skip-download",
        action="store_true",
        help="require all pinned source files to exist locally with matching SHA-256 values",
    )
    parser.add_argument(
        "--run-size",
        type=int,
        default=2_000_000,
        help="maximum normalized records per external-sort run (default: 2000000)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.run_size <= 0:
        raise ValueError("--run-size must be positive")

    overall_started = time.monotonic()
    data_dir = args.data_dir.resolve()
    tezaurs_raw = data_dir / "tezaurs" / "raw"
    korpuss_raw = data_dir / "korpuss" / "raw"
    tezaurs_raw.mkdir(parents=True, exist_ok=True)
    korpuss_raw.mkdir(parents=True, exist_ok=True)

    print("WARNING: full B2 build takes about 25 minutes, measured peak build RSS is about 271 MB, and it needs about 1.5 GB free disk.")
    ispell_zip = ensure_asset(
        ISPELL_ZIP, tezaurs_raw / "tezaurs_2026_03.ispell.zip",
        ISPELL_ZIP_SHA256, args.skip_download)
    wordforms_zip = ensure_asset(
        WORDFORMS_ZIP, tezaurs_raw / "tezaurs_2026_3_wordforms_tei.xml.zip",
        WORDFORMS_ZIP_SHA256, args.skip_download)
    freq_tsv = ensure_asset(
        FREQ_TSV, korpuss_raw / "frequencies-lv-25K.tsv",
        FREQ_TSV_SHA256, args.skip_download)

    started = time.monotonic()
    print(f"Extracting {ispell_zip.name}")
    with zipfile.ZipFile(ispell_zip) as archive:
        archive.extractall(tezaurs_raw)
    ispell_path = tezaurs_raw / "tezaurs_2026_03.ispell"
    if not ispell_path.is_file():
        raise FileNotFoundError(f"Expected {ispell_path} after extracting {ispell_zip}")
    print(f"Extracted ispell in {time.monotonic() - started:.1f}s")

    # scale = occurrences per 1e9 tokens; RARE_THRESHOLD=100 in b.morphology means rare == absent from the top-25K list
    freq = {}
    for line in io.open(freq_tsv, encoding="utf-8").read().split("\n")[1:]:
        if not line:
            continue
        lemma, _pos, permille = line.split("\t")
        freq[lemma] = freq.get(lemma, 0.0) + float(permille)
    freq_int = {k: int(round(v * 1_000_000)) for k, v in freq.items()}
    assert min(freq_int.values()) >= 100
    print(f"Loaded frequency data for {len(freq_int):,} lemmas")

    sys.path.insert(0, str(TOOLS_DIR))
    from b.tezaurs import build_b2_index_extmerge

    out_dir = data_dir / "tezaurs" / "index" / "b2"
    started = time.monotonic()
    print(f"Building B2 index in {out_dir}")
    build_b2_index_extmerge(
        wordforms_zip,
        out_dir=out_dir,
        ispell_path=ispell_path,
        freq=freq_int,
        run_size=args.run_size,
    )
    print(f"Built B2 index in {time.monotonic() - started:.1f}s")

    from b.ondisk import build_sqlite_wordforms

    started = time.monotonic()
    build_sqlite_wordforms(out_dir / "wordforms.tsv", out_dir / "wordforms.sqlite")
    print(f"Built SQLite wordforms index in {time.monotonic() - started:.1f}s")

    from b.ondisk import load_index_ondisk
    from b.allowlist import load_allowlist
    from b.analyze import analyze

    lexicon, index = load_index_ondisk(out_dir)
    allow = load_allowlist(
        TOOLS_DIR / "data" / "lv-it-supplement.txt",
        TOOLS_DIR / "data" / "tezaurs-gaps.txt",
    )
    # NB: exact-form allowlists (v1) — avoid inflected dictionary words here, or the
    # diagnostic-severity morphology flag would break the single-flag assertion.
    flags = analyze("Šī sistēmma strādā labi.", lexicon, index, allow)
    assert len(flags) == 1
    assert flags[0].rule_id == "spelling.candidate"
    assert flags[0].observed == "sistēmma"
    print("PASS: smoke test flagged only sistēmma as spelling.candidate")

    print("\nUsage:")
    print(
        "python tools/pilot.py --text path/to/input.txt "
        f"--index {out_dir} "
        "--allow tools/data/lv-it-supplement.txt "
        "--allow tools/data/tezaurs-gaps.txt --out report.json"
    )
    print("\nCC BY-SA 4.0 attribution:")
    print(TEZAURS_ATTRIBUTION)
    print(FREQUENCY_ATTRIBUTION)
    print(f"Completed in {time.monotonic() - overall_started:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
