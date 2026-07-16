from __future__ import annotations
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Requirement:
    kind: str          # fact | quote | term | register
    value: str


@dataclass(frozen=True)
class Policy:
    cloud_allowed: bool
    consent_id: str | None = None
    redaction_policy_id: str | None = None
    redact: bool = False


@dataclass
class AInput:
    intent: str
    requirements: list[Requirement] = field(default_factory=list)
    context: str | None = None
    seed: str | None = None
    anchors: list[str] = field(default_factory=list)
    voice_contract: dict | None = None      # trusted allowlist
    voice_examples: list[str] = field(default_factory=list)  # untrusted
    profile: str = "style_only"
    policy: Policy = field(default_factory=lambda: Policy(cloud_allowed=True))


@dataclass
class Result:
    status: str                              # generated | denied
    text: str | None = None
    reason: str | None = None                # cloud_forbidden | redaction_failed | prohibited_class
    anchor_support: str = "none"
    revision: int = 0
    gate: object | None = None
    needs_human: bool = True


def anchor_support(n: int) -> str:
    return "none" if n == 0 else "limited" if n <= 2 else "recommended"
