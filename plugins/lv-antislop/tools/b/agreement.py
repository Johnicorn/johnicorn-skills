"""B2 agreement (2b): amod/nsubj saskaņas pārbaude ar margin-based abstention.

Divslāņu dizains:
  - tīrais likumu dzinējs (`check_tokens`) strādā ar jau noparsētiem tokenu
    dictiem (text/upos/feats/head/deprel) + per-token arc-marginiem — testējams
    bez lvnlp/torch;
  - `LvnlpAdapter` (lazy import; instalēts tikai 2b videi) dod tokenus, arc
    marginus un rakstzīmju spanus no AiLab lvnlp parsera. Vienmēr
    `analyzer=False` — pilnībā offline (analyzer=True klusi POST-o uz
    nlp.ailab.lv). Windows: procesam vajag PYTHONUTF8=1 (lvnlp 0.1.0 config
    lasīšana bez encoding).

Ģimenes (design §5, §12 rev 6/7):
  amod : head = NOUN/PROPN, dependents = ADJ (vai divdabis, upos VERB) —
         Case/Number/Gender, kur pazīme ir ABĀS pusēs.
  nsubj: subjekts–predikāts — Person/Number tikai tur, kur verba forma tos
         atklāti marķē (LVTB konvencija: 3. personas formām Number nav feats)
         + tā paša predikāta finītie AUX bērni (saliktie laiki) + nsubj uz
         nefinītas formas ar atklātu 1./2. personas subjektu.
         Koordinēts subjekts (conj bērni) -> skaitlis Plur; Gender nsubj
         ģimenē NAV pārbaudīts (design §5: Person/Number only).

Abstention: mala, kuras arc-margins (top1-top2 arc score, §12 rev 6) ir zem
sliekšņa, netiek vērtēta un skaitās abstain. margin=None (viens vienīgais
galīgais kandidāts) nozīmē pilnu noteiktību -> nekad neabstainē.

Tukša/whitespace ievade tiek noraidīta pirms parsera (lvnlp 0.1.0 uz tukšu
ievadi met AssertionError — probe atradums MF-05).
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from b3.scanner import Flag

AMOD_FEATURES = ("Case", "Number", "Gender")
NOMINAL = {"NOUN", "PROPN"}
RULE_ID = "agreement.violation"


def parse_feats(feats: str | None) -> dict[str, str]:
    if not feats or feats == "_":
        return {}
    return dict(part.split("=", 1) for part in feats.split("|") if "=" in part)


def _base(deprel: str | None) -> str:
    return (deprel or "").split(":", 1)[0]


@dataclass(frozen=True)
class AgreementFlag:
    token_index: int          # 1-based pozīcija teikumā
    token: str
    family: str               # amod | nsubj
    feature: str              # Case | Number | Gender | Person
    dependent_value: str | None
    expected_value: str | None
    detail: str


@dataclass(frozen=True)
class EdgeDecision:
    """Viena pārbaudītā mala: flagi + margins, pēc kura kalibrē abstention."""
    token_index: int          # tokens, kura piesaistes marginu vērtē
    family: str
    margin: float | None
    abstained: bool
    flags: tuple[AgreementFlag, ...]


def check_tokens(
        tokens: list[dict[str, Any]],
        margins: list[float | None] | None = None,
        margin_threshold: float | None = None) -> list[EdgeDecision]:
    feats = [parse_feats(t.get("feats")) for t in tokens]
    children: dict[int, list[int]] = defaultdict(list)
    for i, t in enumerate(tokens, 1):
        head = t.get("head") or 0
        if head:
            children[head].append(i)

    def margin_of(i: int) -> float | None:
        return None if margins is None else margins[i - 1]

    def abstains(i: int) -> bool:
        m = margin_of(i)
        return margin_threshold is not None and m is not None and m < margin_threshold

    decisions: list[EdgeDecision] = []
    for i, t in enumerate(tokens, 1):
        dep, head_ix = _base(t.get("deprel")), t.get("head") or 0
        if not head_ix or head_ix > len(tokens):
            continue
        hf, tf = feats[head_ix - 1], feats[i - 1]
        head = tokens[head_ix - 1]

        if dep == "amod" and head.get("upos") in NOMINAL and t.get("upos") in {"ADJ", "VERB"}:
            if abstains(i):
                decisions.append(EdgeDecision(i, "amod", margin_of(i), True, ()))
                continue
            flags = tuple(
                AgreementFlag(i, t["text"], "amod", feature, tf[feature], hf[feature],
                              f"{feature}={tf[feature]} pret {head['text']} ({feature}={hf[feature]})")
                for feature in AMOD_FEATURES
                if feature in tf and feature in hf and tf[feature] != hf[feature])
            decisions.append(EdgeDecision(i, "amod", margin_of(i), False, flags))

        elif dep == "nsubj":
            subj_person = tf.get("Person") or ("3" if t.get("upos") in NOMINAL else None)
            subj_number = tf.get("Number")
            if any(_base(tokens[j - 1].get("deprel")) == "conj" for j in children.get(i, [])):
                subj_number = "Plur"          # koordinēts subjekts -> daudzskaitlis
            targets = [head_ix] + [
                j for j in children.get(head_ix, [])
                if _base(tokens[j - 1].get("deprel")) == "aux"
                and parse_feats(tokens[j - 1].get("feats")).get("VerbForm") == "Fin"]
            for j in targets:
                gate_ix = i if j == head_ix else j   # nsubj malu sargā subjekta margins, aux — savs
                if abstains(gate_ix):
                    decisions.append(EdgeDecision(j, "nsubj", margin_of(gate_ix), True, ()))
                    continue
                jf, tok_j = feats[j - 1], tokens[j - 1]
                flags: list[AgreementFlag] = []
                if "Person" in jf and subj_person and jf["Person"] != subj_person:
                    flags.append(AgreementFlag(
                        j, tok_j["text"], "nsubj", "Person", jf["Person"], subj_person,
                        f"Person={jf['Person']} pret subjektu {t['text']} (Person={subj_person})"))
                if "Number" in jf and subj_number and jf["Number"] != subj_number:
                    flags.append(AgreementFlag(
                        j, tok_j["text"], "nsubj", "Number", jf["Number"], subj_number,
                        f"Number={jf['Number']} pret subjektu {t['text']} (Number={subj_number})"))
                if jf.get("VerbForm") == "Inf" and subj_person in {"1", "2"}:
                    flags.append(AgreementFlag(
                        j, tok_j["text"], "nsubj", "Person", None, subj_person,
                        f"nsubj uz nefinītu formu ar {subj_person}. personas subjektu {t['text']}"))
                decisions.append(EdgeDecision(j, "nsubj", margin_of(gate_ix), False, tuple(flags)))
    return decisions


class LvnlpAdapter:
    """lvnlp parsera aploksne: tokeni + arc margini + rakstzīmju spani."""

    def __init__(self, model_id: str | None = None, device: str = "cpu"):
        import torch  # noqa: F401 — agrīna, skaidra kļūda, ja 2b vide nav uzstādīta
        from lvnlp.parser import Parser
        from lvnlp.parser.inference import DEFAULT_PARSER_MODEL
        self._torch = torch
        self.model_id = model_id or DEFAULT_PARSER_MODEL
        self.parser = Parser.from_pretrained(self.model_id, device=device)

    def parse_with_margins(self, text: str) -> tuple[list[dict[str, Any]], list[float | None], list[tuple[int, int]]]:
        import math

        from torch.utils.data import DataLoader

        from lvnlp.parser.inference import decode
        from lvnlp.parser.ud_dataset import CollateFunctor, UDDataset
        from lvnlp.parser.utils import tokenize_sentence

        torch = self._torch
        prepared = self.parser._prepare_inference_input([tokenize_sentence(text)])
        dataset = UDDataset(prepared, self.parser.tokenizer, vocabs=self.parser.vocabs, random_mask=0)
        batch = next(iter(DataLoader(dataset, batch_size=1, collate_fn=CollateFunctor(dataset.pad_index))))
        with torch.inference_mode():
            self.parser.model.eval()
            output = self.parser.model(
                batch["subwords"].to(self.parser.device),
                batch["alignment"].to(self.parser.device),
                batch["subword_lengths"],
                batch["word_lengths"],
            )
        decoded_data = [list(map(dict, prepared[0]))]
        decode(decoded_data, output, self.parser.vocabs, in_place=True)  # in_place dicti patur 'text'
        tokens = decoded_data[0]
        arcs = output[4][0, : len(tokens), : len(tokens) + 1].detach().cpu()
        margins: list[float | None] = []
        for scores in arcs:
            finite = sorted((float(v) for v in scores.tolist() if math.isfinite(v)), reverse=True)
            margins.append(finite[0] - finite[1] if len(finite) > 1 else None)
        spans, cursor = [], 0
        for token in tokens:
            found = text.find(token["text"], cursor)
            if found < 0:
                spans.append((cursor, cursor))
            else:
                spans.append((found, found + len(token["text"])))
                cursor = found + len(token["text"])
        return tokens, margins, spans


def agreement_flags(
        text: str, adapter: LvnlpAdapter,
        margin_threshold: float | None = None) -> list[Flag]:
    """Gate līmeņa API: teksts -> b3 Flag saraksts (agreement.violation, issue).

    Tukša ievade -> [] (lvnlp tukšuma guards). Viena mala ar vairākiem pazīmju
    pārkāpumiem dod VIENU flagu (tas pats token span, apvienots detail).
    """
    if not text or not text.strip():
        return []
    tokens, margins, spans = adapter.parse_with_margins(text)
    decisions = check_tokens(tokens, margins, margin_threshold)
    flags: list[Flag] = []
    for decision in decisions:
        if decision.abstained or not decision.flags:
            continue
        start, end = spans[decision.token_index - 1]
        flags.append(Flag(start, end, f"{RULE_ID}.{decision.family}", "issue",
                          tokens[decision.token_index - 1]["text"]))
    return flags
