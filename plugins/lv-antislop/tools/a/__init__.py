"""A generation-layer orchestration. Import submodules directly (a.contract, a.orchestrate)."""

from .contract import AInput, Requirement, Policy, Result, anchor_support
from .preserve import requirement_preservation
from .orchestrate import generate
from .gate_adapter import b3_gate
from .acceptance import load_oracle, check_output

__all__ = ["AInput", "Requirement", "Policy", "Result", "anchor_support",
           "requirement_preservation", "generate", "b3_gate", "load_oracle", "check_output"]
