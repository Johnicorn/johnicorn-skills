from __future__ import annotations
from b3.scanner import Flag
from b3.gate import GateResult

_PROFILE_CHECKS = {
    "style_only": {"B3"},
    "lexical": {"B3", "LEX"},
    "morphology": {"B2", "B3"},
    "full": {"B1", "B2", "B3"},
}

def _assurance(statuses: list[str]) -> str:
    if not statuses:
        return "unavailable"
    if all(s == "completed" for s in statuses):
        return "complete"
    if all(s == "unavailable" for s in statuses):
        return "unavailable"
    return "partial"

def gate(profile: str, statuses: dict[str, str], flags: list[Flag]) -> GateResult:
    required = _PROFILE_CHECKS[profile]
    checks = {name: {"requested": name in required,
                     "status": statuses.get(name, "unavailable" if name in required else "not_requested")}
              for name in ("B1", "B2", "B3", "LEX")}
    req_statuses = [c["status"] for c in checks.values() if c["requested"]]
    has_issues = any(f.severity == "issue" for f in flags)
    assurance = _assurance(req_statuses)
    if has_issues:
        outcome = "issues"
    elif assurance == "complete":
        outcome = "clear"
    else:
        outcome = "not_cleared"
    return GateResult(profile=profile, checks=checks, flags=flags, has_issues=has_issues,
                      assurance=assurance, outcome=outcome,
                      needs_human=has_issues or assurance != "complete")
