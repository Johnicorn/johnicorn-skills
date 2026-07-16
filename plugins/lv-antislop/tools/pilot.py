from __future__ import annotations

import argparse
from collections import Counter
from html.parser import HTMLParser
import json
from pathlib import Path
import sys

from b.allowlist import load_allowlist
from b.analyze import analyze
from b.ondisk import load_index_ondisk
from b3.scanner import WORD_TOKEN


class _VisibleText(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.skipped = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in {"script", "style"}:
            self.skipped += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"} and self.skipped:
            self.skipped -= 1

    def handle_data(self, data: str) -> None:
        if not self.skipped and data.strip():
            self.parts.append(data.strip())


def _visible_text(path: Path) -> str:
    parser = _VisibleText()
    parser.feed(path.read_text(encoding="utf-8"))
    parser.close()
    return " ".join(parser.parts)


def _parse_args() -> argparse.Namespace:
    tools = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser()
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--html", type=Path)
    source.add_argument("--text", type=Path)
    parser.add_argument(
        "--index", type=Path, default=(tools / "../vendor/tezaurs/index/b2").resolve())
    parser.add_argument("--allow", type=Path, action="append", default=[])
    parser.add_argument("--out", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    args = _parse_args()
    text = _visible_text(args.html) if args.html else args.text.read_text(encoding="utf-8")
    allow = load_allowlist(*args.allow)
    lexicon, index = load_index_ondisk(args.index)
    flags = analyze(text, lexicon, index, allow)
    tokens_scanned = len(WORD_TOKEN.findall(text))
    flags_by_code = Counter(flag.rule_id for flag in flags)
    unique = Counter((flag.observed, flag.rule_id) for flag in flags)
    report = {
        "tokens_scanned": tokens_scanned,
        "flags_by_code": dict(sorted(flags_by_code.items())),
        "unique": [
            {"token": token, "code": code, "count": count}
            for (token, code), count in sorted(
                unique.items(), key=lambda item: (-item[1], item[0][0], item[0][1]))
        ],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"tokens scanned: {tokens_scanned}")
    for (code, severity), count in sorted(
            Counter((flag.rule_id, flag.severity) for flag in flags).items()):
        print(f"{code} ({severity}): {count}")
    for item in report["unique"]:
        print(f"{item['token']}\t{item['code']}\t{item['count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
