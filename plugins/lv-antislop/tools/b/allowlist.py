from __future__ import annotations

from pathlib import Path

from .index import norm


def load_allowlist(*paths: str | Path) -> frozenset[str]:
    entries: set[str] = set()
    for path in paths:
        for line in Path(path).read_text(encoding="utf-8").splitlines():
            token = line.strip()
            if token and not token.startswith("#"):
                entries.add(norm(token))
    return frozenset(entries)
