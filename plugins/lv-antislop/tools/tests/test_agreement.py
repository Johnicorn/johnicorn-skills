"""2b saskaņas likumu dzinēja testi — tīrā daļa, bez lvnlp/torch."""
from b.agreement import agreement_flags, check_tokens, parse_feats


def tok(text, upos, feats, head, deprel):
    return {"text": text, "upos": upos, "feats": feats, "head": head, "deprel": deprel}


def flags_of(decisions):
    return [flag for decision in decisions for flag in decision.flags]


# ---- parse_feats ----

def test_parse_feats_basics():
    assert parse_feats("Case=Nom|Gender=Masc") == {"Case": "Nom", "Gender": "Masc"}
    assert parse_feats("_") == {}
    assert parse_feats(None) == {}


# ---- amod ----

def test_amod_gender_mismatch_flags_dependent():
    tokens = [
        tok("zaļa", "ADJ", "Case=Nom|Gender=Fem|Number=Sing", 2, "amod"),
        tok("koks", "NOUN", "Case=Nom|Gender=Masc|Number=Sing", 0, "root"),
    ]
    flags = flags_of(check_tokens(tokens))
    assert [(f.token, f.family, f.feature) for f in flags] == [("zaļa", "amod", "Gender")]


def test_amod_skips_feature_missing_on_one_side():
    tokens = [
        tok("rozā", "ADJ", "Degree=Pos", 2, "amod"),  # nelokāms: bez Case/Gender/Number
        tok("kleitu", "NOUN", "Case=Acc|Gender=Fem|Number=Sing", 0, "root"),
    ]
    assert flags_of(check_tokens(tokens)) == []


def test_amod_participle_dependent_checked():
    tokens = [
        tok("izlasītie", "VERB", "Case=Nom|Gender=Masc|Number=Plur|VerbForm=Part", 2, "amod"),
        tok("grāmatas", "NOUN", "Case=Nom|Gender=Fem|Number=Plur", 0, "root"),
    ]
    assert [f.feature for f in flags_of(check_tokens(tokens))] == ["Gender"]


# ---- nsubj ----

def test_nsubj_person_mismatch_flags_verb():
    tokens = [
        tok("Es", "PRON", "Case=Nom|Number=Sing|Person=1", 2, "nsubj"),
        tok("strādā", "VERB", "Mood=Ind|Person=3|VerbForm=Fin", 0, "root"),
    ]
    flags = flags_of(check_tokens(tokens))
    assert [(f.token, f.feature) for f in flags] == [("strādā", "Person")]


def test_nsubj_third_person_number_not_marked_stays_silent():
    tokens = [
        tok("Bērni", "NOUN", "Case=Nom|Gender=Masc|Number=Plur", 2, "nsubj"),
        tok("skrien", "VERB", "Mood=Ind|Person=3|VerbForm=Fin", 0, "root"),  # bez Number
    ]
    assert flags_of(check_tokens(tokens)) == []


def test_nsubj_nominal_subject_implies_third_person():
    tokens = [
        tok("Anna", "PROPN", "Case=Nom|Gender=Fem|Number=Sing", 2, "nsubj"),
        tok("spēlēju", "VERB", "Mood=Ind|Number=Sing|Person=1|VerbForm=Fin", 0, "root"),
    ]
    assert [f.feature for f in flags_of(check_tokens(tokens))] == ["Person"]


def test_nsubj_coordinated_subject_resolves_plural():
    base = [
        tok("Anna", "PROPN", "Case=Nom|Gender=Fem|Number=Sing", 4, "nsubj"),
        tok("un", "CCONJ", "_", 3, "cc"),
        tok("Pēteris", "PROPN", "Case=Nom|Gender=Masc|Number=Sing", 1, "conj"),
        tok("aizbraukuši", "VERB", "Gender=Masc|Number=Plur|VerbForm=Part", 0, "root"),
    ]
    assert flags_of(check_tokens(base)) == []          # Plur saskan
    singular = [dict(t) for t in base]
    singular[3]["feats"] = "Gender=Masc|Number=Sing|VerbForm=Part"
    singular[3]["text"] = "aizbraucis"
    assert [f.feature for f in flags_of(check_tokens(singular))] == ["Number"]


def test_nsubj_finite_aux_child_checked():
    tokens = [
        tok("Tu", "PRON", "Case=Nom|Number=Sing|Person=2", 3, "nsubj"),
        tok("esat", "AUX", "Mood=Ind|Number=Plur|Person=2|VerbForm=Fin", 3, "aux"),
        tok("nopelnījis", "VERB", "Gender=Masc|Number=Sing|VerbForm=Part", 0, "root"),
    ]
    flags = flags_of(check_tokens(tokens))
    assert [(f.token, f.feature) for f in flags] == [("esat", "Number")]


def test_nsubj_infinitive_with_overt_person_subject_flags():
    tokens = [
        tok("Mēs", "PRON", "Case=Nom|Number=Plur|Person=1", 2, "nsubj"),
        tok("iet", "VERB", "Polarity=Pos|VerbForm=Inf", 0, "root"),
    ]
    flags = flags_of(check_tokens(tokens))
    assert [(f.token, f.feature) for f in flags] == [("iet", "Person")]


# ---- abstention ----

def test_margin_below_threshold_abstains():
    tokens = [
        tok("zaļa", "ADJ", "Case=Nom|Gender=Fem|Number=Sing", 2, "amod"),
        tok("koks", "NOUN", "Case=Nom|Gender=Masc|Number=Sing", 0, "root"),
    ]
    decisions = check_tokens(tokens, margins=[1.0, None], margin_threshold=2.0)
    amod = [d for d in decisions if d.family == "amod"]
    assert amod[0].abstained and not amod[0].flags


def test_margin_none_never_abstains():
    tokens = [
        tok("zaļa", "ADJ", "Case=Nom|Gender=Fem|Number=Sing", 2, "amod"),
        tok("koks", "NOUN", "Case=Nom|Gender=Masc|Number=Sing", 0, "root"),
    ]
    decisions = check_tokens(tokens, margins=[None, None], margin_threshold=99.0)
    amod = [d for d in decisions if d.family == "amod"]
    assert not amod[0].abstained and amod[0].flags


# ---- gate API guards ----

def test_agreement_flags_empty_input_guard():
    assert agreement_flags("", adapter=None) == []
    assert agreement_flags("   \n", adapter=None) == []
