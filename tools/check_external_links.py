"""Check that every external link in the repository still resolves.

Usage:
    python tools/check_external_links.py [repo-root]

Requests are made with a short timeout and a browser-like User-Agent. A link is reported as broken
if the server answers with 4xx or 5xx, or if the request fails entirely (DNS, TLS, timeout).

Some large sites answer 403 to automated clients while working perfectly in a browser. Those are
reported separately as "blocked" rather than "broken", so you can judge them yourself.

Exit code is 0 if no link is broken, 1 otherwise.
"""

from __future__ import annotations

import os
import re
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

LINK_RE = re.compile(r"\[[^\]]*\]\((https?://[^)\s]+)(?:\s+\"[^\"]*\")?\)")
FENCE_RE = re.compile(r"^```.*?^```", re.MULTILINE | re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
SKIP_DIRECTORIES = {".git", "__pycache__", ".venv", "venv", "node_modules"}
USER_AGENT = "Mozilla/5.0 (compatible; link-checker/1.0; +https://github.com)"
TIMEOUT = 20


def strip_code(text: str) -> str:
    """Remove fenced code blocks and inline code spans.

    Example links inside a code block are illustrations, not links a reader is meant to click.
    """
    return INLINE_CODE_RE.sub("", FENCE_RE.sub("", text))


def iter_markdown(root: str):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in SKIP_DIRECTORIES]
        for name in sorted(filenames):
            if name.lower().endswith(".md"):
                yield os.path.join(dirpath, name)


def collect_links(root: str) -> list[tuple[str, str]]:
    found: dict[str, str] = {}
    for path in iter_markdown(root):
        with open(path, "r", encoding="utf-8") as handle:
            text = handle.read()
        for url in LINK_RE.findall(strip_code(text)):
            found.setdefault(url, os.path.relpath(path, root))
    return sorted(found.items())


def check(url: str) -> tuple[str, str]:
    """Return (url, status) where status is 'ok', 'blocked' or 'broken:<detail>'."""
    request = urllib.request.Request(url, method="GET", headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            return url, "ok" if response.status < 400 else f"broken:HTTP {response.status}"
    except urllib.error.HTTPError as error:
        if error.code in (401, 403, 429):
            return url, "blocked"
        return url, f"broken:HTTP {error.code}"
    except urllib.error.URLError as error:
        return url, f"broken:{error.reason}"
    except Exception as error:  # noqa: BLE001
        return url, f"broken:{type(error).__name__}"


def main() -> int:
    root = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
    links = collect_links(root)
    print(f"checking {len(links)} unique external link(s)...\n")

    with ThreadPoolExecutor(max_workers=12) as pool:
        results = list(pool.map(check, [url for url, _ in links]))

    status_by_url = dict(results)
    broken: list[str] = []
    blocked: list[str] = []

    for url, source in links:
        status = status_by_url[url]
        if status == "ok":
            continue
        if status == "blocked":
            blocked.append(f"{source}: {url}")
        else:
            broken.append(f"{source}: {url}  ->  {status}")

    if blocked:
        print(f"BLOCKED (answer 401/403/429 to automated requests, usually fine in a browser): {len(blocked)}")
        for item in blocked:
            print(f"  {item}")
        print()

    if broken:
        print(f"BROKEN: {len(broken)}")
        for item in broken:
            print(f"  {item}")
        return 1

    print("no broken external links")
    return 0


if __name__ == "__main__":
    sys.exit(main())
