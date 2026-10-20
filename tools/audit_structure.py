"""Audit that every chapter file follows the house structure.

Usage: python tools/audit_structure.py <repo-root>
"""
from __future__ import annotations

import os
import re
import sys

REQUIRED_HEADINGS = [
    "## Why this matters for AI engineering",
    "## 🧪 Try it yourself",
    "## ✅ Checkpoint",
    "## 🐛 Common mistakes",
    "## 🔗 Resources",
    "## ➡️ Next",
]
META_MARKERS = ["**⏱️ Time:**", "**📚 Prereqs:**", "**🎯 By the end you can:**"]
ALLOWED_EMOJI = {
    "⏱️", "📚", "🎯", "🧪", "✅", "🐛", "🔗", "➡️", "⬅️", "←", "👉",
}
EMOJI_RE = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF⬅➡⬜⬝]"
)


def audit(path: str) -> list[str]:
    problems = []
    with open(path, "r", encoding="utf-8") as handle:
        text = handle.read()

    name = os.path.basename(path)

    for heading in REQUIRED_HEADINGS:
        if heading not in text:
            problems.append(f"{name}: missing heading '{heading}'")

    for marker in META_MARKERS:
        if marker not in text:
            problems.append(f"{name}: missing metadata marker '{marker}'")

    if not text.lstrip().startswith("# "):
        problems.append(f"{name}: does not start with an H1")

    # the file must end with the Next section
    tail = text.rstrip().splitlines()[-25:]
    if not any(line.startswith("## ➡️ Next") for line in tail):
        problems.append(f"{name}: does not end with the '➡️ Next' section")

    # a Previous link must exist
    if "← Previous" not in text and "Previous" not in text:
        problems.append(f"{name}: no 'Previous' link")

    # empty sections
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.startswith("## ") and index + 1 < len(lines):
            following = [l for l in lines[index + 1 : index + 6] if l.strip()]
            if following and following[0].startswith("## "):
                problems.append(f"{name}: empty section '{line.strip()}'")

    # emoji outside the allowed set
    stripped = text
    for heading in REQUIRED_HEADINGS:
        stripped = stripped.replace(heading, "")
    for marker in META_MARKERS:
        stripped = stripped.replace(marker, "")
    for found in sorted(set(EMOJI_RE.findall(stripped))):
        if found not in ALLOWED_EMOJI:
            problems.append(
                f"{name}: unexpected emoji U+{ord(found):04X} ({found.encode('unicode_escape').decode()})"
            )

    # placeholder text
    for bad in ("TODO", "FIXME", "coming soon", "Coming soon", "Lorem ipsum", "XXX"):
        if bad in text:
            problems.append(f"{name}: contains placeholder text '{bad}'")

    return problems


def main() -> int:
    root = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
    all_problems = []
    files = 0

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in {".git", "__pycache__", "tools"}]
        for name in sorted(filenames):
            if not name.endswith(".md"):
                continue
            # only the numbered chapters follow the chapter skeleton;
            # guide.md and resources.md have their own shapes
            if not re.match(r"^\d\d-", name):
                continue
            path = os.path.join(dirpath, name)
            if os.path.basename(dirpath) != "PYTHON":
                continue
            files += 1
            all_problems.extend(audit(path))

    print(f"audited {files} chapter file(s)")
    if all_problems:
        print(f"\nISSUES ({len(all_problems)}):")
        for problem in all_problems:
            print("  " + problem.encode("ascii", "replace").decode("ascii"))
        return 1
    print("all chapters follow the house structure")
    return 0


if __name__ == "__main__":
    sys.exit(main())
