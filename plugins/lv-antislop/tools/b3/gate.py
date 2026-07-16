from __future__ import annotations
from dataclasses import dataclass, field
from .scanner import Flag

# per-check status:
#   completed     - ran and finished
#   incomplete    - ran but did not finish (partial progress)  <- distinct from unavailable
#   unavailable   - engine absent / never ran
#   not_requested - out of profile
CheckStatus = str

@dataclass
class GateResult:
    profile: str
    checks: dict                      # name -> {"requested": bool, "status": CheckStatus}
    flags: list[Flag] = field(default_factory=list)
    has_issues: bool = False
    assurance: str = "unavailable"    # complete | partial | unavailable
    outcome: str = "not_cleared"      # clear | issues | not_cleared
    needs_human: bool = True

def _assurance(requested_statuses: list[str]) -> str:
    if not requested_statuses:
        return "unavailable"
    if all(s == "completed" for s in requested_statuses):
        return "complete"
    if all(s == "unavailable" for s in requested_statuses):
        return "unavailable"
    return "partial"                  # any incomplete / mixed -> partial (NOT unavailable)

def gate_style_only(flags: list[Flag], b3_status: CheckStatus = "completed") -> GateResult:
    # profile style_only requires only B3
    checks = {"B3": {"requested": True, "status": b3_status}}
    # has_issues derives from RETAINED flags (severity=issue), NOT check status
    has_issues = any(f.severity == "issue" for f in flags)
    assurance = _assurance([c["status"] for c in checks.values() if c["requested"]])
    if has_issues:
        outcome = "issues"
    elif assurance == "complete":
        outcome = "clear"
    else:
        outcome = "not_cleared"
    needs_human = has_issues or assurance != "complete"
    return GateResult(profile="style_only", checks=checks, flags=flags,
                      has_issues=has_issues, assurance=assurance,
                      outcome=outcome, needs_human=needs_human)
