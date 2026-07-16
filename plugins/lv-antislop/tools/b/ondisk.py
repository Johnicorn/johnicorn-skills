"""SQLite-backed B2 wordform lookup for memory-bounded runtime use."""
from __future__ import annotations

import json
import os
from pathlib import Path
import sqlite3
import tempfile

from .index import FORMAT_VERSION, Lexicon, WordformIndex, _FILES, _sha256


def build_sqlite_wordforms(wordforms_tsv, db_path) -> None:
    """Stream a v1 wordforms.tsv file into a fresh SQLite lookup database."""
    source = Path(wordforms_tsv)
    database = Path(db_path)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{database.name}.", suffix=".tmp", dir=database.parent)
    os.close(descriptor)
    temporary_database = Path(temporary_name)
    try:
        source_sha256 = _sha256(source)
        connection = sqlite3.connect(temporary_database)
        try:
            connection.execute("PRAGMA journal_mode=OFF")
            connection.execute("PRAGMA synchronous=OFF")
            connection.execute(
                "CREATE TABLE wf (key TEXT PRIMARY KEY, lemmas TEXT) WITHOUT ROWID")
            connection.execute("CREATE TABLE meta (k TEXT PRIMARY KEY, v TEXT)")

            def records():
                with source.open("r", encoding="utf-8") as wordforms:
                    for line in wordforms:
                        if line == "\n":
                            continue
                        if line.endswith("\n"):
                            line = line[:-1]
                        key, lemmas = line.split("\t", 1)
                        yield key, lemmas

            connection.executemany(
                "INSERT INTO wf (key, lemmas) VALUES (?, ?)", records())
            connection.execute(
                "INSERT INTO meta (k, v) VALUES (?, ?)",
                ("source_sha256", source_sha256),
            )
            connection.commit()
        finally:
            connection.close()
        os.replace(temporary_database, database)
    except BaseException:
        temporary_database.unlink(missing_ok=True)
        raise


class SqliteWordforms:
    """Read-only, dict-like B2 form-to-lemma lookup; queries may be serialized across threads."""

    def __init__(self, db_path):
        database = Path(db_path).resolve()
        self._connection = sqlite3.connect(
            f"{database.as_uri()}?mode=ro", uri=True, check_same_thread=False)

    def get(self, key, default=None):
        if not isinstance(key, str):
            return default
        row = self._connection.execute(
            "SELECT lemmas FROM wf WHERE key = ?", (key,)).fetchone()
        return row[0].split(",") if row is not None else default

    def close(self):
        self._connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


def load_index_ondisk(index_dir, db_path=None) -> tuple[Lexicon, WordformIndex]:
    """Load a verified v1 index with B2 wordforms queried from SQLite."""
    directory = Path(index_dir)
    database = Path(db_path) if db_path is not None else directory / "wordforms.sqlite"
    if not database.exists():
        raise FileNotFoundError(
            f"SQLite wordform index not found: {database}. "
            "Build it with build_sqlite_wordforms first.")

    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise ValueError("manifest is not a JSON object")
    if manifest.get("format_version") != FORMAT_VERSION:
        raise ValueError(
            f"index format_version {manifest.get('format_version')!r} != {FORMAT_VERSION!r}")
    sha = manifest.get("sha256")
    if not isinstance(sha, dict) or any(name not in sha for name in _FILES):
        raise ValueError("manifest missing or malformed sha256 section")
    for name in _FILES:
        if _sha256(directory / name) != sha[name]:
            raise ValueError(f"sha256 mismatch for {name} (index tampered or corrupt)")

    connection = sqlite3.connect(
        f"{database.resolve().as_uri()}?mode=ro", uri=True)
    try:
        source_sha256 = connection.execute(
            "SELECT v FROM meta WHERE k = ?", ("source_sha256",)).fetchone()
    except sqlite3.Error as exc:
        raise ValueError("sqlite index stale: missing source metadata") from exc
    finally:
        connection.close()
    if source_sha256 is None or source_sha256[0] != sha["wordforms.tsv"]:
        raise ValueError("sqlite index stale: built from a different wordforms.tsv")

    forms = frozenset(
        line for line in (directory / "forms.txt").read_text(encoding="utf-8").split("\n") if line)
    freq: dict[str, int] = {}
    for line in (directory / "freq.tsv").read_text(encoding="utf-8").split("\n"):
        if not line:
            continue
        key, count = line.split("\t", 1)
        freq[key] = int(count)
    return Lexicon(forms=forms), WordformIndex(
        forms=SqliteWordforms(database), freq=freq)
