from pathlib import Path
from b3.manifest import load_manifest
from b3.scanner import scan

MANIFEST = Path(__file__).parents[2] / "contracts" / "b3-style-manifest.v1.yaml"
M = load_manifest(MANIFEST)

def _ids(flags):
    return {f.rule_id for f in flags}

def test_word_rule_matches_with_boundary():
    flags = scan("Serveris krita. Turklāt dati pazuda.", M)
    assert "transition.turklat" in _ids(flags)

def test_literal_rule_matches_phrase():
    flags = scan("Mēs esam uzticams partneris.", M)
    assert "cliche.uzticams_partneris" in _ids(flags)

def test_url_is_excluded():
    flags = scan("Skati https://turklāt.example.com biežāk.", M)
    assert "transition.turklat" not in _ids(flags)   # inside a URL -> excluded

def test_caller_excluded_range_suppresses_match():
    text = "Citāts: «Turklāt viss mainās.»"
    start = text.index("«"); end = text.index("»") + 1
    flags = scan(text, M, excluded_ranges=[(start, end)])
    assert "transition.turklat" not in _ids(flags)

def test_regex_rule_gadus_atpakal_does_not_catch_correct_form():
    # round-5 correctness: must NOT flag the correct "pirms 5 gadiem"
    assert "rucalque.gadus_atpakal" not in _ids(scan("Tas notika pirms 5 gadiem.", M))
    assert "rucalque.gadus_atpakal" in _ids(scan("Tas notika 5 gadus atpakaļ.", M))

from b3.scanner import density_report

def test_tiek_density_reports_count_and_denominator():
    text = "Atbalsts tiek nodrošināts. Pakalpojums tiek piedāvāts."
    rep = density_report(text, M)["tiek.density"]
    assert rep["tiek_count"] == 2
    assert rep["denominator_word_tokens"] == 6
    assert round(rep["per_1000"], 1) == round(2 * 1000 / 6, 1)
    assert rep["severity"] == "diagnostic"

def test_tiek_excludes_ranges_from_both_num_and_denom():
    text = "«tiek tiek tiek» Mēs strādājam."
    q0, q1 = text.index("«"), text.index("»") + 1
    rep = density_report(text, M, excluded_ranges=[(q0, q1)])["tiek.density"]
    assert rep["tiek_count"] == 0
    assert rep["denominator_word_tokens"] == 2   # only "Mēs strādājam"
