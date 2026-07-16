"""Tēzaurs CLARIN dump -> lv-antislop index inputs.
B1 extractor: the .ispell wordform list (one UTF-8 form per line). Keeps only
pure-letter forms (what the letter-only WORD_TOKEN can ever query); abbreviations,
multi-word, digit and punctuation entries are dropped. NFC+lower + dedup happen in
build_index.
B2 extractor: the wordforms TEI (form->lemma), streamed — 13+ GB uncompressed, never
DOM-parsed; processed <entry> subtrees are dropped from <standOff> to bound memory."""
from __future__ import annotations
import heapq, re, tempfile, zipfile
from pathlib import Path
from xml.etree.ElementTree import iterparse
from b.index import (
    _validate_wordform_item,
    _write_forms,
    _write_freq,
    _write_manifest,
    _write_wordforms_from_sorted_items,
    build_index,
    norm,
)

_LETTER = "A-Za-zĀāČčĒēĢģĪīĶķĻļŅņŌōŖŗŠšŪūŽž"
_PURE = re.compile(f"^[{_LETTER}]+$")

def iter_ispell_forms(path):
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            w = line.rstrip("\n")
            if _PURE.match(w):
                yield w

def build_b1_index(ispell_path, out_dir) -> dict:
    """B1-only index: forms populated from the ispell; wordforms/freq empty."""
    return build_index(iter_ispell_forms(ispell_path), {}, {}, out_dir)

_TEI = "{http://www.tei-c.org/ns/1.0}"

def _iter_tei_pairs(fh, limit=None):
    """Stream (form, lemma) pairs from a wordforms-TEI byte stream. Per <entry>:
    lemma = <form>/<orth type="lemma">; each <form type="inflection">/<orth> is a
    form. Pure-letter forms only. Memory-bounded: each processed <entry> is removed
    from <standOff> so the tree never accumulates."""
    context = iterparse(fh, events=("start", "end"))
    standoff = None
    n = 0
    for event, elem in context:
        if event == "start":
            if standoff is None and elem.tag == _TEI + "standOff":
                standoff = elem
            continue
        if elem.tag != _TEI + "entry":
            continue
        lemma_el = elem.find(f"{_TEI}form/{_TEI}orth[@type='lemma']")
        lemma = lemma_el.text if lemma_el is not None else None
        if lemma:
            for orth in elem.findall(
                    f"{_TEI}form/{_TEI}form[@type='inflection']/{_TEI}orth"):
                form = orth.text
                if form and _PURE.match(form):
                    yield form, lemma
        elem.clear()
        if standoff is not None:
            standoff.remove(elem)
        n += 1
        if limit and n >= limit:
            break

def iter_wordform_lemma_pairs(wordforms_zip, limit=None):
    """Stream (form, lemma) pairs from a Tēzaurs wordforms-TEI .zip (reads the single
    member without extracting the 13+ GB XML to disk)."""
    with zipfile.ZipFile(wordforms_zip) as zf:
        with zf.open(zf.namelist()[0]) as fh:
            yield from _iter_tei_pairs(fh, limit)

def build_b2_index(wordforms_zip, out_dir, ispell_path=None, limit=None) -> dict:
    """Build an index with B2 wordforms from the TEI (+ optional B1 forms from the
    ispell). Accumulates form->lemmas in RAM (bounded by unique pure-letter forms);
    build_index does the NFC+lower merge/dedup/sort and writes the on-disk index.

    MEMORY: the full Tēzaurs wordforms dump is ~30M unique forms (~224 forms/entry)
    and the in-RAM accumulator OOMs on a 16 GB host. Use `limit` for a bounded slice;
    the full index needs a memory-bounded external-merge builder (§12 B2-PKG TODO)."""
    wf: dict[str, list[str]] = {}
    for form, lemma in iter_wordform_lemma_pairs(wordforms_zip, limit=limit):
        wf.setdefault(form, []).append(lemma)
    forms = iter_ispell_forms(ispell_path) if ispell_path else []
    return build_index(forms, wf, {}, out_dir)

def _write_run(lines: list[str], run_dir: Path) -> Path:
    """Sort one bounded chunk of normalized key/lemma records into a temp run."""
    lines.sort()
    with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n", suffix=".tsv",
            dir=run_dir, delete=False) as fh:
        fh.writelines(lines)
        return Path(fh.name)

def _collapse_sorted_run_lines(lines):
    """Yield sorted (key, sorted unique lemmas) from key-sorted run records."""
    current_key = None
    lemmas: set[str] = set()
    for line in lines:
        key, lemma = line[:-1].split("\t", 1)
        if key != current_key:
            if current_key is not None:
                yield current_key, sorted(lemmas)
            current_key = key
            lemmas = set()
        lemmas.add(lemma)
    if current_key is not None:
        yield current_key, sorted(lemmas)

def build_b2_index_extmerge(
        wordforms_zip, out_dir, ispell_path=None, freq=None, limit=None,
        run_size=2_000_000, tmp_dir=None) -> dict:
    """Build B2 with bounded run buffers and a streaming external merge.

    The TEI pair stream is normalized and validated before it reaches temporary
    storage. Only one run-size chunk and the lemmas for one normalized key are
    held in memory during the final merge.

    run_size trades run count for chunk RAM: the final merge opens every run at
    once, so keep run_size large enough that pair_count/run_size stays within the
    OS file-handle budget (the 2M default -> ~tens of runs even at full scale).
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    forms = iter_ispell_forms(ispell_path) if ispell_path else []
    run_paths: list[Path] = []
    handles = []
    try:
        with tempfile.TemporaryDirectory(dir=tmp_dir) as run_dir_name:
            run_dir = Path(run_dir_name)
            chunk: list[str] = []
            for form, lemma in iter_wordform_lemma_pairs(wordforms_zip, limit=limit):
                key = norm(form)
                _validate_wordform_item(key, [lemma])
                chunk.append(f"{key}\t{lemma}\n")
                if len(chunk) >= run_size:
                    run_paths.append(_write_run(chunk, run_dir))
                    chunk = []
            if chunk:
                run_paths.append(_write_run(chunk, run_dir))

            try:
                if run_paths:
                    for path in run_paths:
                        handles.append(path.open(encoding="utf-8", newline="\n"))
                    merged = heapq.merge(
                        *handles, key=lambda line: line.partition("\t")[0])
                    wordform_count = _write_wordforms_from_sorted_items(
                        out / "wordforms.tsv", _collapse_sorted_run_lines(merged))
                else:
                    wordform_count = _write_wordforms_from_sorted_items(
                        out / "wordforms.tsv", ())
            finally:
                for fh in handles:
                    fh.close()
                handles = []

            return _write_manifest(
                out,
                forms=_write_forms(out / "forms.txt", forms),
                wordforms=wordform_count,
                freq=_write_freq(out / "freq.tsv", freq),
            )
    finally:
        for fh in handles:
            fh.close()
        for path in run_paths:
            try:
                path.unlink()
            except FileNotFoundError:
                pass
