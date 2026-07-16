from __future__ import annotations
from .contract import AInput, Result, anchor_support
from .preserve import requirement_preservation

_ASSURANCE_RANK = {"complete": 0, "partial": 1, "unavailable": 2}


def _compose(a_input: AInput, prev=None, prev_flags=None) -> dict:
    # one composed request per attempt; untrusted parts kept as data
    return {
        "intent": a_input.intent,
        "constraints": "lv-antislop rules",
        "anchors": list(a_input.anchors),
        "voice_contract": a_input.voice_contract,
        "voice_examples": list(a_input.voice_examples),
        "prev_candidate": prev,
        "gate_feedback": list(prev_flags or []),
    }


def generate(a_input: AInput, gen_fn, gate_fn, max_repairs: int = 2) -> Result:
    if not a_input.policy.cloud_allowed:
        return Result(status="denied", reason="cloud_forbidden", needs_human=True)

    cands: list[tuple[int, str, object]] = []
    prev, prev_flags = None, None
    for k in range(max_repairs + 1):
        text = gen_fn(_compose(a_input, prev, prev_flags))
        gate = gate_fn(text)
        cands.append((k, text, gate))
        if gate.outcome == "clear" and requirement_preservation(text, a_input.requirements) == "pass":
            break                                   # early stop
        prev, prev_flags = text, gate.flags

    survivors = [(k, t, g) for (k, t, g) in cands
                 if requirement_preservation(t, a_input.requirements) != "fail"]
    asup = anchor_support(len(a_input.anchors))
    if not survivors:                               # no candidate preserved requirements
        k0, t0, g0 = cands[0]
        return Result(status="generated", text=t0, anchor_support=asup, revision=k0,
                      gate=g0, needs_human=True)

    def _issue_ids(g):
        return {(f.rule_id, f.start) for f in g.flags if f.severity == "issue"}

    best = min(survivors, key=lambda c: (
        len(_issue_ids(c[2])),                      # fewest distinct issue flags
        _ASSURANCE_RANK.get(c[2].assurance, 3),     # then best assurance
        c[0],                                       # then lowest revision
    ))
    k, text, gate = best
    needs_human = gate.needs_human or requirement_preservation(text, a_input.requirements) != "pass"
    return Result(status="generated", text=text, anchor_support=asup, revision=k,
                  gate=gate, needs_human=needs_human)
