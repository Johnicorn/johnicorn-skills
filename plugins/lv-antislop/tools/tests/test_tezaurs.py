import io, zipfile
import b.tezaurs as tezaurs
from b.tezaurs import (iter_ispell_forms, build_b1_index,
                       _iter_tei_pairs, iter_wordform_lemma_pairs, build_b2_index,
                       build_b2_index_extmerge)
from b.index import build_index, load_index
from b.morphology import form_check

_TEI_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
 <teiHeader/>
 <standOff>
  <entry type="supplemental"><form>
    <orth type="lemma">diena</orth>
    <form type="inflection"><orth>diena</orth></form>
    <form type="inflection"><orth>dienas</orth></form>
    <form type="inflection"><orth>dienā</orth></form>
    <form type="inflection"><orth>2diena</orth></form>
  </form></entry>
  <entry type="supplemental"><form>
    <orth type="lemma">māja</orth>
    <form type="inflection"><orth>Māja</orth></form>
    <form type="inflection"><orth>mājas</orth></form>
  </form></entry>
  <entry type="supplemental"><form>
    <orth type="lemma">flora</orth>
    <form type="inflection"><orth>Zieds</orth></form>
    <form type="inflection"><orth>floras</orth></form>
  </form></entry>
  <entry type="supplemental"><form>
    <orth type="lemma">augs</orth>
    <form type="inflection"><orth>zieds</orth></form>
    <form type="inflection"><orth>augi</orth></form>
  </form></entry>
  <entry type="supplemental"><form>
    <orth type="lemma">saule</orth>
    <form type="inflection"><orth>saule</orth></form>
  </form></entry>
  <entry type="supplemental"><form>
    <orth type="lemma">meness</orth>
    <form type="inflection"><orth>meness</orth></form>
  </form></entry>
 </standOff>
</TEI>'''

def test_tei_extracts_form_lemma_and_filters_nonletter():
    pairs = list(_iter_tei_pairs(io.BytesIO(_TEI_XML.encode("utf-8"))))
    assert ("diena", "diena") in pairs
    assert ("dienas", "diena") in pairs
    assert ("dienā", "diena") in pairs
    assert ("mājas", "māja") in pairs
    assert all(not any(c.isdigit() for c in f) for f, _ in pairs)   # "2diena" dropped

def test_tei_limit_stops_after_n_entries():
    lemmas = {l for _, l in _iter_tei_pairs(io.BytesIO(_TEI_XML.encode("utf-8")), limit=1)}
    assert lemmas == {"diena"}                                       # only the first entry

def test_build_b2_index_from_tei_zip(tmp_path):
    z = tmp_path / "wf.zip"
    with zipfile.ZipFile(z, "w") as zf:
        zf.writestr("wordforms.xml", _TEI_XML)
    out = tmp_path / "idx"
    build_b2_index(z, out)
    lex, idx = load_index(out)
    assert idx.forms["dienas"] == ["diena"]
    assert idx.forms["māja"] == ["māja"]          # "Māja" normalized (NFC+lower) on build
    r = form_check("dienā", idx)
    assert r.status == "validated" and r.lemmas == ["diena"]

def test_iter_keeps_pure_letter_drops_the_rest(tmp_path):
    p = tmp_path / "x.ispell"
    p.write_text("alus\nA/g\n60-tais\nsvaigs\nipso facto\nrīga\n", encoding="utf-8")
    assert list(iter_ispell_forms(p)) == ["alus", "svaigs", "rīga"]

def test_build_b1_index_from_ispell(tmp_path):
    src = tmp_path / "x.ispell"
    src.write_text("Alus\nalus\nSvaigs\n", encoding="utf-8")
    out = tmp_path / "idx"
    build_b1_index(src, out)
    lex, idx = load_index(out)
    assert lex.forms == frozenset({"alus", "svaigs"})
    assert idx.forms == {}

def _write_tei_zip(path):
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("wordforms.xml", _TEI_XML)

def _wordforms_from_tei_zip(path):
    wordforms = {}
    for form, lemma in iter_wordform_lemma_pairs(path):
        wordforms.setdefault(form, []).append(lemma)
    return wordforms

def test_b2_extmerge_is_byte_identical_to_in_memory_and_canonical_writer(tmp_path):
    z = tmp_path / "wf.zip"
    _write_tei_zip(z)
    ispell = tmp_path / "forms.ispell"
    ispell.write_text("Alus\nalus\n", encoding="utf-8")
    in_memory = tmp_path / "in-memory"
    extmerge = tmp_path / "extmerge"
    canonical = tmp_path / "canonical"

    build_b2_index(z, in_memory, ispell_path=ispell)
    build_b2_index_extmerge(z, extmerge, ispell_path=ispell, freq={}, run_size=2)
    build_index([], _wordforms_from_tei_zip(z), {}, canonical)

    _, idx = load_index(extmerge)
    assert idx.forms["zieds"] == ["augs", "flora"]
    for name in ("forms.txt", "wordforms.tsv", "freq.tsv", "manifest.json"):
        assert (in_memory / name).read_bytes() == (extmerge / name).read_bytes()
    assert (in_memory / "wordforms.tsv").read_bytes() == (
        canonical / "wordforms.tsv").read_bytes()
    assert (extmerge / "wordforms.tsv").read_bytes() == (
        canonical / "wordforms.tsv").read_bytes()

def test_b2_extmerge_forces_multiple_runs_and_merges_them(tmp_path, monkeypatch):
    z = tmp_path / "wf.zip"
    _write_tei_zip(z)
    pair_count = len(list(iter_wordform_lemma_pairs(z)))
    run_paths = []
    original_write_run = tezaurs._write_run

    def record_run(lines, run_dir):
        path = original_write_run(lines, run_dir)
        run_paths.append(path)
        return path

    monkeypatch.setattr(tezaurs, "_write_run", record_run)
    out = tmp_path / "extmerge"
    canonical = tmp_path / "canonical"
    build_b2_index_extmerge(z, out, run_size=2)
    build_index([], _wordforms_from_tei_zip(z), {}, canonical)

    assert 2 < pair_count
    assert len(run_paths) > 1
    assert (out / "wordforms.tsv").read_bytes() == (
        canonical / "wordforms.tsv").read_bytes()

def test_b2_extmerge_is_deterministic(tmp_path):
    z = tmp_path / "wf.zip"
    _write_tei_zip(z)
    a = tmp_path / "a"
    b = tmp_path / "b"

    build_b2_index_extmerge(z, a, run_size=2)
    build_b2_index_extmerge(z, b, run_size=2)

    for name in ("forms.txt", "wordforms.tsv", "freq.tsv", "manifest.json"):
        assert (a / name).read_bytes() == (b / name).read_bytes()
