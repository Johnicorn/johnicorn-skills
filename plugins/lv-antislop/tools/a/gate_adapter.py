from __future__ import annotations
from pathlib import Path
from b3.manifest import load_manifest
from b3.scanner import scan
from b3.gate import gate_style_only

_MANIFEST = load_manifest(Path(__file__).parents[2] / "contracts" / "b3-style-manifest.v1.yaml")


def b3_gate(text: str, b3_status: str = "completed"):
    """style_only B gate: scan for B3 flags -> GateResult."""
    flags = scan(text, _MANIFEST)
    return gate_style_only(flags=flags, b3_status=b3_status)
