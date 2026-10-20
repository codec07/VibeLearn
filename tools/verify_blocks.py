"""Verify that every Python code block in a Markdown file actually runs.

Usage:
    python tools/verify_blocks.py <file.md> [<file.md> ...]

Two kinds of Python block are handled:

1. A **standalone** block (no filename header) is written to a temporary file and executed.
   It must run cleanly on its own.

2. A **file-backed** block, whose first line is a comment naming the file it belongs to:

       # my_module.py
       # tests/test_my_module.py

   is written to that path inside a temporary directory. After every file-backed block has been
   collected, the whole directory is run through pytest, so the example modules and their tests
   are executed together exactly as a reader would run them.

Flags
-----
A file-backed block may carry a flag after the filename:

    # src/runner.py [expected-failure] -- this file is meant to crash

A block marked `[expected-failure]` is run and must raise. It is used for examples that teach a
failure, such as an import error.

Interactive blocks
------------------
A block that calls `input()` cannot be fully checked without a person at the keyboard. Those
blocks are fed sample input; if they still stop on `EOFError` they are reported as interactive
rather than as failures.

The temporary directory is removed when the script finishes. Nothing is written to the repository.

Exit code is 0 if everything passed, 1 otherwise.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile

BLOCK_RE = re.compile(r"^```python[ \t]*\n(.*?)^```[ \t]*$", re.MULTILINE | re.DOTALL)
HEADER_RE = re.compile(
    r"^#[ \t]+([\w\-./]+\.py)"          # the file this block belongs to
    r"((?:[ \t]+\[[a-z\-]+\])*)"        # optional flags, e.g. [expected-failure]
    r"[ \t]*(?:--.*)?$"                 # optional trailing comment
)
STDIN_SAMPLE = "42\nhello\nAlice\n31\ny\nPeter\n3.5\n"

GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
RESET = "\033[0m"


def extract_blocks(text: str) -> list[str]:
    return [match.group(1) for match in BLOCK_RE.finditer(text)]


def run_block(script_path: str, workdir: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, script_path],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=workdir,
        input=STDIN_SAMPLE,
    )


def verify_file(path: str) -> tuple[int, int, list[str]]:
    """Returns (blocks_checked, failures, problems)."""
    with open(path, "r", encoding="utf-8") as handle:
        text = handle.read()

    blocks = extract_blocks(text)
    workdir = tempfile.mkdtemp(prefix="verify_blocks_")
    problems: list[str] = []
    checked = 0
    failures = 0
    skipped = 0
    file_backed = 0
    has_tests = False

    # A src-layout project is normally made importable with `pip install -e .`.
    # In the scratch directory we do the same thing with a conftest, so that
    # `import my_package` works for a package that lives under src/.
    with open(os.path.join(workdir, "conftest.py"), "w", encoding="utf-8") as handle:
        handle.write(
            "import os\n"
            "import sys\n"
            "_root = os.path.dirname(os.path.abspath(__file__))\n"
            "_src = os.path.join(_root, 'src')\n"
            "if os.path.isdir(_src) and _src not in sys.path:\n"
            "    sys.path.insert(0, _src)\n"
        )

    try:
        # Pass 1: write every file-backed block to disk first, so that a module defined
        # later in the document still exists when an earlier block imports it.
        for index, code in enumerate(blocks, start=1):
            first_line = code.splitlines()[0] if code.splitlines() else ""
            header = HEADER_RE.match(first_line)
            if not header:
                continue
            relative = header.group(1)
            target = os.path.join(workdir, relative)
            os.makedirs(os.path.dirname(target) or workdir, exist_ok=True)
            with open(target, "w", encoding="utf-8") as handle:
                handle.write(code)
            file_backed += 1
            checked += 1
            if relative.startswith("tests/") or os.path.basename(relative).startswith("test_"):
                has_tests = True
            if "expected-failure" in header.group(2):
                result = run_block(target, workdir)
                if result.returncode == 0:
                    failures += 1
                    problems.append(f"{path} block {index}: expected to fail but it ran cleanly")
                    print(f"  {RED}FAIL{RESET} block {index:>2} ({relative}) - expected to fail, but it did not")
                else:
                    last = (result.stderr.strip().splitlines() or [""])[-1][:88]
                    print(f"  {GREEN}ok  {RESET} block {index:>2} ({relative}) - fails as intended: {last}")
            else:
                print(f"  {YELLOW}file{RESET} block {index:>2} -> {relative}")

        # Pass 2: run the standalone blocks.
        for index, code in enumerate(blocks, start=1):
            first_line = code.splitlines()[0] if code.splitlines() else ""
            if HEADER_RE.match(first_line):
                continue

            scratch = os.path.join(workdir, f"__standalone_{index:03d}.py")
            with open(scratch, "w", encoding="utf-8") as handle:
                handle.write(code)
            try:
                result = run_block(scratch, workdir)
            except subprocess.TimeoutExpired:
                failures += 1
                problems.append(f"{path} block {index}: timed out after 180s")
                print(f"  {RED}FAIL{RESET} block {index:>2} (timeout)")
                continue

            checked += 1
            if result.returncode == 0:
                first_output = (result.stdout.strip().splitlines() or [""])[0][:88]
                print(f"  {GREEN}ok  {RESET} block {index:>2} -> {first_output}")
            elif "input(" in code and (
                "EOFError" in result.stderr or "invalid literal for int()" in result.stderr
            ):
                # an interactive example: it needs a human at the keyboard
                skipped += 1
                print(f"  {BLUE}int {RESET} block {index:>2} -> interactive, needs typed input")
            else:
                failures += 1
                problems.append(f"{path} block {index}: {result.stderr.strip()[-400:]}")
                print(f"  {RED}FAIL{RESET} block {index:>2}")
                for line in (result.stderr.strip().splitlines() or [""])[-8:]:
                    print(f"       {line}")

        if has_tests:
            print("  running pytest over the file-backed test blocks...")
            result = subprocess.run(
                [sys.executable, "-m", "pytest", workdir, "-q", "--no-header", "-p", "no:cacheprovider"],
                capture_output=True,
                text=True,
                timeout=900,
                cwd=workdir,
            )
            summary = [
                line
                for line in result.stdout.splitlines()
                if "passed" in line or "failed" in line or "error" in line
            ]
            for line in summary[-3:]:
                print(f"       {line}")
            if result.returncode != 0:
                failures += 1
                problems.append(
                    f"{path}: pytest failed for the file-backed blocks\n{result.stdout[-1500:]}"
                )
                print(f"  {RED}FAIL{RESET} pytest")
    finally:
        shutil.rmtree(workdir, ignore_errors=True)

    if skipped:
        print(f"  ({skipped} interactive block(s) skipped - they need input from a person)")
    return checked, failures, problems


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2

    total_checked = 0
    total_failures = 0
    all_problems: list[str] = []

    for path in sys.argv[1:]:
        print(f"\n=== {path} ===")
        checked, failures, problems = verify_file(path)
        total_checked += checked
        total_failures += failures
        all_problems.extend(problems)

    print(f"\n{total_checked - total_failures}/{total_checked} blocks passed, {total_failures} failed")
    for problem in all_problems:
        print(f"\n--- {problem}")

    return 1 if total_failures else 0


if __name__ == "__main__":
    sys.exit(main())
