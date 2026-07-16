from a.contract import Requirement
from a.preserve import requirement_preservation as rp


def test_fact_present_passes():
    reqs = [Requirement("fact", "4.8% ABV")]
    assert rp("Alus ar 4.8% ABV.", reqs) == "pass"


def test_fact_missing_fails():
    reqs = [Requirement("fact", "4.8% ABV")]
    assert rp("Garšīgs alus.", reqs) == "fail"


def test_register_tu_ok_when_no_jus_marker():
    reqs = [Requirement("register", "Tu")]
    assert rp("Pasūti sev alu.", reqs) == "pass"


def test_register_tu_fails_on_jus_pronoun():
    reqs = [Requirement("register", "Tu")]
    assert rp("Pasūtiet Jums alu.", reqs) == "fail"


def test_unknown_kind_is_indeterminate():
    reqs = [Requirement("vibe", "cosy")]
    assert rp("whatever", reqs) == "indeterminate"
