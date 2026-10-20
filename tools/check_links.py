"""Check that every relative Markdown link in the repository points at a file that exists.

Usage:
    python tools/check_links.py [repo-root]

External links (http, https, mailto) are ignored here - use check_external_links.py for those.
Exit code is 0 if every internal link resolves, 1 otherwise.
"""

from __future__ import annotations

import os
import re
import sys
from urllib.parse import unquote

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
FENCE_RE = re.compile(r"^```.*?^```", re.MULTILINE | re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
SKIP_PREFIXES = ("http://", "https://", "mailto:", "#", "tel:", "data:", "ftp://")
SKIP_DIRECTORIES = {".git", "__pycache__", ".venv", "venv", "node_modules", ".pytest_cache", ".mypy_cache"}


def strip_code_blocks(text: str) -> str:
    """Remove fenced code blocks and inline code spans so example links inside them are not checked."""
    text = FENCE_RE.sub("", text)
    return INLINE_CODE_RE.sub("", text)


def iter_markdown(root: str):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in SKIP_DIRECTORIES]
        for name in sorted(filenames):
            if name.lower().endswith(".md"):
                yield os.path.join(dirpath, name)


def main() -> int:
    root = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
    broken: list[str] = []
    checked = 0
    files = 0

    for path in iter_markdown(root):
        files += 1
        with open(path, "r", encoding="utf-8") as handle:
            text = handle.read()

        for raw in LINK_RE.findall(strip_code_blocks(text)):
            target = raw.strip()
            if not target or target.startswith(SKIP_PREFIXES):
                continue
            if target.startswith("<") and target.endswith(">"):
                target = target[1:-1]
            target = target.split("#")[0].split("?")[0]
            if not target:
                continue

            checked += 1
            resolved = os.path.normpath(os.path.join(os.path.dirname(path), unquote(target)))
            if not os.path.exists(resolved):
                relative = os.path.relpath(path, root)
                broken.append(f"{relative}: [{raw}] -> {os.path.relpath(resolved, root)}")

    print(f"scanned {files} markdown file(s), checked {checked} internal link(s)")
    if broken:
        print(f"\nBROKEN ({len(broken)}):")
        for item in broken:
            print(f"  {item}")
        return 1
    print("all internal links resolve")
    return 0


if __name__ == "__main__":
    sys.exit(main())
