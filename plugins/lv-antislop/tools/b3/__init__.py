"""B3 style-rule scanner package.

Import submodules directly: `from b3.manifest import load_manifest`, etc.
Package-level re-exports are deferred to the final task (Task 9) so that this
file never imports a module that does not yet exist during early tasks.
"""

from .manifest import Manifest, load_manifest
from .scanner import Flag, scan, density_report
from .gate import GateResult, gate_style_only

__all__ = ["Manifest", "load_manifest", "Flag", "scan", "density_report",
           "GateResult", "gate_style_only"]
