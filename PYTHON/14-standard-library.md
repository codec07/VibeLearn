# Standard Library

Everything you have used so far — `open`, `range`, `sorted`, `print` — comes from the
**standard library**: the collection of modules that ship with Python itself, free,
maintained by the core team, and guaranteed to be there on every machine. It is far, far
bigger than most beginners realise. This file is a guided tour of the parts that come up
again and again in real projects: paths and files, dates and times, containers, text
processing, running other programs, randomness and secrets, and command line arguments.
The goal is not to memorise an API — it is to know what already exists, so you never
reinvent a utility that shipped for free.

> **⏱️ Time:** ~40 minutes
> **📚 Prereqs:** [13 — Testing](13-testing.md)
> **🎯 By the end you can:** Reach for the right standard-library module for the job —
> manipulating paths, parsing dates, counting things, matching text, running subprocesses,
> reading secrets safely and building a real command line tool — and find any module you
> have never heard of without leaving Python.

---

## Why this matters for AI engineering

When you build an LLM application, a surprising amount of the work is not model work. You
need to read a 200-page PDF from disk, work out which of 40 chunks changed since yesterday,
parse a timestamp out of a log line, hash an API key so you can compare it safely, split a
large file into batches, and give a user a command line tool to run the whole thing. All of
that is standard-library work, and all of it used to be "write a utility function" before
you discovered the module that already does it perfectly.

Knowing the standard library also keeps your dependencies small. A service with three
third-party packages is easier to install, easier to audit and has fewer security updates
than one with thirty. In an AI team, "can we do this with the standard library?" is a
question that comes up in every code review.

---

## 1. How the standard library is organised

The modules are not all equal. There are three tiers you should know about:

| Tier | What it is | Examples |
|---|---|---|
| **Built-in** | Compiled into the interpreter, always available, no import needed | `print`, `len`, `range`, `list`, `dict`, `sum`, `sorted`, `open` |
| **Standard library** | Pure-Python modules shipped with Python, one `import` away | `pathlib`, `datetime`, `json`, `re`, `subprocess`, `collections` |
| **Third-party** | Installed from PyPI | `httpx`, `pandas`, `pydantic`, `pytest` |

Everything in this file is the second tier. All of it is free, all of it is installed
already, and all of it is documented at [docs.python.org](https://docs.python.org/3/library/index.html).

---

## 2. Paths and files: `pathlib`

`pathlib` is the modern way to work with file paths. The old way was to glue strings
together with `os.path.join` and hope you got the separator right; `pathlib` gives you
**objects** that know how to do it.

```python
from pathlib import Path

# Build a path with /, regardless of operating system
config = Path("project") / "configs" / "settings.json"
print(config)
print(config.name)        # settings.json
print(config.stem)        # settings
print(config.suffix)      # .json
print(config.parent)      # project/configs

# Inspect without touching the file system
print(config.exists())    # False - we never created it
print(config.is_file())   # False
print(config.is_dir())    # False

# Create directories and files
config.parent.mkdir(parents=True, exist_ok=True)
config.write_text('{"model": "gpt-4o-mini"}', encoding="utf-8")
print(config.exists())    # True
print(config.read_text(encoding="utf-8"))

# Rename and remove
other = config.with_name("config.json")
config.rename(other)
print(other.exists(), config.exists())
other.unlink()
print(other.exists())
```

```text
project\configs\settings.json
settings.json
settings
.json
project\configs
False
False
False
True
{"model": "gpt-4o-mini"}
True False
False
```

The `Path` object is the single most useful thing in this file. Memorise these members:

| Member | What it does |
|---|---|
| `Path("a") / "b"` | join two path segments |
| `p.name` | the file name, with extension |
| `p.stem` | the file name, without extension |
| `p.suffix` | the extension, including the dot |
| `p.parent` | the containing directory |
| `p.exists()` / `p.is_file()` / `p.is_dir()` | checks that do not raise |
| `p.read_text()` / `p.write_text(text)` | read/write a whole text file |
| `p.read_bytes()` / `p.write_bytes(data)` | read/write binary data |
| `p.mkdir(parents=True, exist_ok=True)` | create a directory (and its parents) |
| `p.rename(target)` | rename or move |
| `p.unlink()` | delete a file |
| `p.stat().st_size` | size in bytes |
| `p.with_suffix(".md")` | same path, different extension |
| `p.relative_to(other)` | the path relative to a base directory |
| `p.glob("*.py")` | children matching a pattern |
| `p.rglob("*")` | every descendant matching a pattern |

### Finding the largest files in a folder

Here is a complete, runnable utility built entirely from `pathlib`:

```python
"""Find the five largest files in a folder tree."""

import tempfile
from pathlib import Path


def largest_files(root: Path, count: int = 5) -> list[tuple[int, Path]]:
    """Return the `count` largest files under `root`, biggest first."""
    files = [p for p in root.rglob("*") if p.is_file()]
    files.sort(key=lambda p: p.stat().st_size, reverse=True)
    return [(p.stat().st_size, p) for p in files[:count]]


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "a.txt").write_text("x" * 5000, encoding="utf-8")
        (root / "b.txt").write_text("x" * 12000, encoding="utf-8")
        nested = root / "nested"
        nested.mkdir()
        (nested / "c.bin").write_bytes(b"\x00" * 30000)

        for size, path in largest_files(root):
            print(f"{size:>8,} bytes  {path.relative_to(root)}")
```

```text
  30,000 bytes  nested\c.bin
  12,000 bytes  b.txt
   5,000 bytes  a.txt
```

---

## 3. Dates and times: `datetime`

```python
from datetime import date, datetime, timedelta, timezone

# A moment in time
now = datetime.now()
print(now)                          # 2026-10-20 10:22:55.371426
print(now.year, now.month, now.day)

# A calendar date, with no time component
today = date.today()
print(today)                        # e.g. 2026-10-20

# Arithmetic (using a fixed reference date so the number is stable)
age = date(2026, 10, 20) - date(1995, 6, 14)
print(age.days)                     # 11451 days

# Adding and subtracting
print(now + timedelta(hours=3))
print(now - timedelta(days=7))

# Formatting and parsing
stamp = datetime(2026, 3, 14, 15, 9, 26)
print(stamp.strftime("%Y-%m-%d %H:%M:%S"))   # 2026-03-14 15:09:26
print(stamp.strftime("%d %B %Y"))             # 14 March 2026
print(stamp.isoformat())                      # 2026-03-14T15:09:26
print(datetime.strptime("2026-03-14", "%Y-%m-%d"))
```

```text
2026-10-20 10:22:55.371426
2026 10 20
2026-10-20
11451
2026-10-20 13:22:55.371426
2026-10-13 10:22:55.371426
2026-03-14 15:09:26
14 March 2026
2026-03-14T15:09:26
2026-03-14 00:00:00
```

(The date and the clock are whatever they are when you run it.)

The `strftime` codes you will use most:

| Code | Meaning | Example |
|---|---|---|
| `%Y` / `%y` | year, 4 digits / 2 digits | `2026` / `26` |
| `%m` / `%d` | month, day (zero-padded) | `03` / `14` |
| `%H` / `%M` / `%S` | hour (24h), minute, second | `15` / `09` / `26` |
| `%B` / `%b` | month name, full / short | `March` / `Mar` |
| `%A` / `%a` | weekday name, full / short | `Saturday` / `Sat` |
| `%z` | UTC offset | `+0000` |
| `%f` | microseconds | `371426` |

### Naive versus aware datetimes — the bug you will meet

A **naive** datetime has no timezone attached. An **aware** datetime carries its UTC
offset, so Python can tell you unambiguously what moment it refers to.

```python
from datetime import datetime, timezone

naive = datetime(2026, 3, 14, 15, 9, 26)
aware = datetime(2026, 3, 14, 15, 9, 26, tzinfo=timezone.utc)

print(naive.tzinfo)        # None
print(aware.tzinfo)        # UTC
print(aware.utcoffset())   # 0:00:00

# Subtracting two aware datetimes works correctly
later = datetime(2026, 3, 14, 18, 9, 26, tzinfo=timezone.utc)
print(later - aware)       # 3:00:00

# Subtracting a naive from an aware raises
try:
    print(later - naive)
except TypeError as error:
    print("Error:", error)
```

```text
None
UTC
0:00:00
3:00:00
Error: can't subtract offset-naive and offset-aware datetimes
```

**Rule:** always work with aware datetimes. `datetime.now()` returns a naive value; use
`datetime.now(timezone.utc)` instead. Python 3.11 added the short alias `datetime.UTC`
for `timezone.utc`.

```python
from datetime import UTC, datetime

print(datetime.now(UTC).isoformat())
print(datetime.now(UTC).tzinfo)
```

```text
2026-10-20T10:22:55.371426+00:00
UTC
```

(Again, the exact moment depends on when you run it.)

### Local time zones with `zoneinfo`

`zoneinfo` converts a time zone *name* (like `"Europe/London"`) into a proper offset,
including daylight saving time. It is in the standard library from Python 3.9.

```python
from datetime import datetime
from zoneinfo import ZoneInfo

for city in ["UTC", "Asia/Kolkata", "Europe/London", "America/New_York"]:
    zone = ZoneInfo(city)
    moment = datetime(2026, 7, 4, 12, 0, tzinfo=zone)
    print(f"{city:<18} {moment.isoformat()}  {moment.tzname()}")
```

```text
UTC                2026-07-04T12:00:00+00:00  UTC
Asia/Kolkata       2026-07-04T12:00:00+05:30  IST
Europe/London      2026-07-04T12:00:00+01:00  BST
America/New_York   2026-07-04T12:00:00-04:00  EDT
```

On Windows, the IANA time zone database is not part of the operating system, so you may
need `python -m pip install tzdata` once. On macOS and Linux it is already there.

---

## 4. Collections: the right container for the job

`collections` adds specialised containers to the built-in `list`, `dict`, `set` and
`tuple`.

### `Counter` — counting things

```python
from collections import Counter

words = "the quick brown fox jumps over the lazy dog the fox".split()
counts = Counter(words)

print(counts)
print(counts["the"])              # 3
print(counts["fox"])               # 2
print(counts["cat"])               # 0 - missing keys do not raise
print(counts.most_common(2))       # [('the', 3), ('fox', 2)]
print(sum(counts.values()))        # 10

# The most useful trick: counting characters or words from any iterable
print(Counter("mississippi").most_common(3))
print(Counter([1, 2, 2, 3, 3, 3]).most_common())
```

```text
Counter({'the': 3, 'fox': 2, 'quick': 1, 'brown': 1, 'jumps': 1, 'over': 1, 'lazy': 1, 'dog': 1})
3
2
0
[('the', 3), ('fox', 2)]
11
[('i', 4), ('s', 4), ('p', 2)]
[(3, 3), (2, 2), (1, 1)]
```

### `defaultdict` — a dict that supplies a default

```python
from collections import defaultdict

# Without defaultdict you would need .get(key, [])
groups = defaultdict(list)
groups["fruit"].append("apple")
groups["fruit"].append("pear")
groups["veg"].append("carrot")
print(dict(groups))

# The factory can be any zero-argument callable
counts = defaultdict(int)
for word in "a b a c b a".split():
    counts[word] += 1
print(dict(counts))

totals = defaultdict(float)
totals["x"] += 1.5
print(dict(totals))
```

```text
{'fruit': ['apple', 'pear'], 'veg': ['carrot']}
{'a': 3, 'b': 2, 'c': 1}
{'x': 1.5}
```

### `deque` — a queue you can pop from both ends

A **deque** (double-ended queue) adds fast `append`, `appendleft`, `pop` and `popleft`
to a list. It is the right tool for breadth-first search, work queues and sliding windows.

```python
from collections import deque

queue = deque(["job1", "job2"])
queue.append("job3")
print(queue.popleft())        # job1 - removed from the left
print(queue)                  # deque(['job2', 'job3'])

# A sliding window over a list - the classic use case
data = [1, 2, 3, 4, 5, 6, 7, 8]
window = deque(maxlen=3)
for value in data:
    window.append(value)
    if len(window) == 3:
        print(f"window {list(window)} max={max(window)}")
```

```text
job1
deque(['job2', 'job3'])
window [1, 2, 3] max=3
window [2, 3, 4] max=4
window [3, 4, 5] max=5
window [4, 5, 6] max=6
window [5, 6, 7] max=7
window [6, 7, 8] max=8
```

### `namedtuple` — a tuple with named fields

```python
from collections import namedtuple

Point = namedtuple("Point", ["x", "y"])
p = Point(3, 4)
print(p.x, p.y)
print(p)

# It is still a tuple, so unpacking works
x, y = p
print(x, y)

# And you can convert it to a dictionary
print(p._asdict())
```

```text
3 4
Point(x=3, y=4)
3 4
{'x': 3, 'y': 4}
```

For a class with defaults and methods, use a `dataclass` instead — see section 9.

### `OrderedDict` — a dict that remembers insertion order

Since Python 3.7, plain `dict` already preserves insertion order, so `OrderedDict` is
rarely needed. It still has two useful extras: `move_to_end` and an `__eq__` that is
order-sensitive.

```python
from collections import OrderedDict

od = OrderedDict(a=1, b=2, c=3)
od.move_to_end("a")
print(list(od.items()))

# Plain dicts keep insertion order too
plain = {"a": 1, "b": 2}
plain["c"] = 3
print(list(plain))
```

```text
[('b', 2), ('c', 3), ('a', 1)]
['a', 'b', 'c']
```

---

## 5. `itertools` and `functools`

### `itertools` — lazy recipes for working with iterators

```python
from itertools import accumulate, chain, combinations, islice, permutations, product, repeat, zip_longest

# chain: glue iterables together
print(list(chain([1, 2], [3, 4], "ab")))
print(list(chain.from_iterable([[1, 2], [3]])))

# islice: take a slice of an iterator without making a list first
data = range(100)
print(list(islice(data, 5, 10)))

# product: every combination of several iterables
print(list(product(["S", "M"], ["red", "blue"])))

# permutations and combinations
print(list(permutations([1, 2, 3], 2)))
print(list(combinations([1, 2, 3], 2)))

# accumulate: running totals
print(list(accumulate([1, 2, 3, 4])))
print(list(accumulate([1, 2, 3, 4], lambda a, b: a * b)))

# repeat: the same value over and over
print(list(repeat("x", 3)))

# zip_longest: zip that pads with a fill value instead of stopping
print(list(zip_longest([1, 2, 3], "ab", fillvalue="?")))
```

```text
[1, 2, 3, 4, 'a', 'b']
[1, 2, 3]
[5, 6, 7, 8, 9]
[('S', 'red'), ('S', 'blue'), ('M', 'red'), ('M', 'blue')]
[(1, 2), (1, 3), (2, 1), (2, 3), (3, 1), (3, 2)]
[(1, 2), (1, 3), (2, 3)]
[1, 3, 6, 10]
[1, 2, 6, 24]
['x', 'x', 'x']
[(1, 'a'), (2, 'b'), (3, '?')]
```

### `groupby` — and the trap that catches everybody

`groupby` groups *consecutive* equal items. It does not sort for you, and it does not
group equal items that are separated by something else.

```python
from itertools import groupby

# The WRONG way: the data must be sorted first
raw = ["apple", "banana", "apple", "cherry"]
groups = {key: list(group) for key, group in groupby(raw)}
print(groups)

# The RIGHT way: sort first, then group
sorted_raw = sorted(raw)
groups = {key: list(group) for key, group in groupby(sorted_raw)}
print(groups)

# groupby with a key function
records = [
    {"dept": "eng", "name": "Ana"},
    {"dept": "eng", "name": "Bo"},
    {"dept": "sales", "name": "Cy"},
]
for dept, group in groupby(records, key=lambda r: r["dept"]):
    print(dept, [r["name"] for r in group])
```

```text
{'apple': ['apple'], 'banana': ['banana'], 'cherry': ['cherry']}
{'apple': ['apple', 'apple'], 'banana': ['banana'], 'cherry': ['cherry']}
eng ['Ana', 'Bo']
sales ['Cy']
```

Notice the first result: the two `apple` entries ended up in *different* groups, so the
dictionary ends up with one `apple` key. That is the trap in one picture.

### `functools` — higher-order helpers

```python
import functools
from functools import cache, cmp_to_key, lru_cache, partial, reduce, wraps

# lru_cache: remember the results of a function
calls = 0


@cache
def slow_power(base: int, exponent: int) -> int:
    global calls
    calls += 1
    return base**exponent


print(slow_power(2, 10))
print(slow_power(2, 10))
print(slow_power(2, 10))
print(f"the function body ran {calls} time(s)")
```

```text
1024
1024
1024
the function body ran 1 time(s)
```

`@cache` (Python 3.9+) keeps the cache forever; `@lru_cache(maxsize=128)` keeps the most
recent 128 results and evicts the oldest. **Only cache functions whose arguments are
hashable** — lists and dicts are not.

```python
from functools import partial, reduce, wraps

# partial: pre-fill some arguments
def greet(greeting: str, name: str) -> str:
    return f"{greeting}, {name}!"


hello = partial(greet, "Hello")
print(hello("Ada"))
print(hello("Alan"))

# reduce: fold a sequence into one value
print(reduce(lambda a, b: a + b, [1, 2, 3, 4], 0))

# wraps: keep the decorated function's name and docstring
def logged(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        print(f"calling {fn.__name__}")
        return fn(*args, **kwargs)

    return wrapper


@logged
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


print(add(2, 3))
print(add.__name__, "-", add.__doc__)

# cmp_to_key: sort with a comparison function
from functools import cmp_to_key

pairs = [(1, "apple"), (2, "fig"), (3, "banana")]
print(sorted(pairs, key=cmp_to_key(lambda a, b: len(a[1]) - len(b[1]))))
```

```text
Hello, Ada!
Hello, Alan!
10
calling add
5
add - Add two numbers.
[(2, 'fig'), (1, 'apple'), (3, 'banana')]
```

---

## 6. Text and data: `json`, `csv`, `re`, `textwrap`, `difflib`

### `json`

```python
import json
from pathlib import Path

data = {"model": "gpt-4o-mini", "temperature": 0.2, "tags": ["fast", "cheap"]}

# Compact for an API, indented for a human
print(json.dumps(data))
print(json.dumps(data, indent=2))
print(json.dumps(data, sort_keys=True, separators=(",", ":")))

# Reading it back
text = '{"name": "Ada", "languages": ["Python", "C"]}'
parsed = json.loads(text)
print(parsed["name"], parsed["languages"][0])

# default= handles objects json does not know how to serialise
from datetime import datetime
from pathlib import Path as P

payload = {"created": datetime(2026, 3, 14, 15, 9, 26), "file": P("notes.txt")}
print(json.dumps(payload, default=str))

# Pretty-print an existing JSON file
Path("config.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
print(Path("config.json").read_text(encoding="utf-8"))
```

```text
{"model": "gpt-4o-mini", "temperature": 0.2, "tags": ["fast", "cheap"]}
{
  "model": "gpt-4o-mini",
  "temperature": 0.2,
  "tags": [
    "fast",
    "cheap"
  ]
}
{"model":"gpt-4o-mini","tags":["fast","cheap"],"temperature":0.2}
Ada Python
{"created": "2026-03-14 15:09:26", "file": "notes.txt"}
{
  "model": "gpt-4o-mini",
  "temperature": 0.2,
  "tags": [
    "fast",
    "cheap"
  ]
}
```

### `csv`

```python
import csv
from io import StringIO

rows = [
    {"name": "Ada", "role": "engineer", "years": 3},
    {"name": "Alan", "role": "researcher", "years": 7},
]

# Writing: DictWriter uses the field names you give it
buffer = StringIO()
writer = csv.DictWriter(
    buffer, fieldnames=["name", "role", "years"], lineterminator="\n"
)
writer.writeheader()
writer.writerows(rows)
print(buffer.getvalue(), end="")

# Reading: DictReader turns each line into a dictionary
reader = csv.DictReader(StringIO(buffer.getvalue()))
for row in reader:
    print(row["name"], "->", row["role"], row["years"])
```

```text
name,role,years
Ada,engineer,3
Alan,researcher,7
Ada -> engineer 3
Alan -> researcher 7
```

When you write CSV to a *file*, always pass `newline=""`:

```python
import csv
from pathlib import Path

with Path("people.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=["name", "role"])
    writer.writeheader()
    writer.writerow({"name": "Ada", "role": "engineer"})

with Path("people.csv").open("r", newline="", encoding="utf-8") as handle:
    print(list(csv.DictReader(handle)))
```

```text
[{'name': 'Ada', 'role': 'engineer'}]
```

Without `newline=""`, Windows turns every `\n` into `\r\n`, and the file ends up with
stray blank lines.

### `re` — regular expressions

A **regular expression** is a small language for describing patterns in text. `re` is
built in.

```python
import re

text = "Order #1024 shipped on 2026-03-14 for $49.99"

# r"" is a RAW string: backslashes are not interpreted by Python
pattern = r"Order #(\d+)"

# match: only at the START of the string
print(re.match(r"Order", text))
print(re.match(r"shipped", text))       # None - not at the start

# search: anywhere in the string
print(re.search(r"\d{4}-\d{2}-\d{2}", text))
print(re.search(r"\d{4}-\d{2}-\d{2}", text).group())

# findall: every match, as a list
print(re.findall(r"\d+", text))
print(re.findall(r"[a-z]+", text))

# finditer: every match, as match objects (use when you need groups)
for match in re.finditer(r"(\d{4})-(\d{2})-(\d{2})", text):
    print(match.group(0), match.groups())

# sub: replace
print(re.sub(r"\d+", "#", text))

# split: cut on a pattern
print(re.split(r"[,;]\s*", "a, b; c, d"))
```

```text
<re.Match object; span=(0, 5), match='Order'>
None
<re.Match object; span=(23, 33), match='2026-03-14'>
2026-03-14
['1024', '2026', '03', '14', '49', '99']
['rder', 'shipped', 'on', 'for']
2026-03-14 ('2026', '03', '14')
Order ## shipped on #-#-# for $#.#
['a', 'b', 'c', 'd']
```

The essential pattern language:

| Pattern | Matches |
|---|---|
| `.` | any character except a newline |
| `^` / `$` | start / end of the string (or line, with `re.MULTILINE`) |
| `\d` / `\D` | a digit / a non-digit |
| `\w` / `\W` | a word character (letters, digits, underscore) / not |
| `\s` / `\S` | whitespace / not whitespace |
| `*` / `+` / `?` | zero or more / one or more / zero or one |
| `{3}` / `{3,5}` | exactly 3 / between 3 and 5 |
| `[abc]` / `[^abc]` / `[a-z]` | one of these / not one of these / a range |
| `(...)` | a group (captured) |
| `(?P<name>...)` | a **named** group |
| `|` | "or" |
| `*?` `+?` | **non-greedy** — match as little as possible |

#### Named groups and non-greedy matching

```python
import re

log = "2026-03-14T15:09:26Z INFO worker started pid=4211"

# Named groups make the result readable
match = re.search(r"(?P<date>\d{4}-\d{2}-\d{2})T(?P<time>\d{2}:\d{2}:\d{2})", log)
print(match.group("date"), match.group("time"))
print(match.groupdict())

# Greedy vs non-greedy: <.*> is greedy, <.*?> is not
html = "<b>bold</b> and <i>italic</i>"
print(re.search(r"<.*>", html).group())
print(re.search(r"<.*?>", html).group())

# Flags
print(re.search(r"info", "INFO", re.IGNORECASE).group())
print(re.findall(r"^INFO", "INFO\nWARN", re.MULTILINE))

# Compile a pattern you use many times
number = re.compile(r"\b\d{3}-\d{4}\b")
print(number.findall("call 555-1234 or 555-9999"))
```

```text
2026-03-14 15:09:26
{'date': '2026-03-14', 'time': '15:09:26'}
<b>bold</b> and <i>italic</i>
<b>
INFO
['INFO']
['555-1234', '555-9999']
```

### `textwrap` and `difflib`

```python
import difflib
import textwrap

paragraph = "Python is a programming language that lets you work quickly and integrate systems more effectively."

print(textwrap.fill(paragraph, width=40))
print(textwrap.fill(paragraph, width=40, initial_indent="> ", subsequent_indent="> "))
print(textwrap.shorten(paragraph, width=30, placeholder="..."))
print(textwrap.indent("line one\nline two", "  "))

# A quick diff between two versions of some text
before = "The quick brown fox jumps over the lazy dog."
after = "The quick red fox leaps over the sleepy dog."
diff = difflib.unified_diff(
    before.splitlines(), after.splitlines(), "before", "after", lineterm=""
)
print("\n".join(diff))
```

```text
Python is a programming language that
lets you work quickly and integrate
systems more effectively.
> Python is a programming language that
> lets you work quickly and integrate
> systems more effectively.
Python is a programming...
  line one
  line two
--- before
+++ after
@@ -1 +1 @@
-The quick brown fox jumps over the lazy dog.
+The quick red fox leaps over the sleepy dog.
```

---

## 7. Processes and the system: `subprocess`, `os`, `sys`, `shutil`, `platform`, `tempfile`

### `subprocess` — run another program

```python
import subprocess
import sys

# Run a program and capture what it prints
result = subprocess.run(
    [sys.executable, "-c", "print('hello from a subprocess')"],
    capture_output=True,
    text=True,
    check=True,
)
print(result.stdout.strip())
print(result.returncode)

# check=True raises CalledProcessError if the program fails
try:
    subprocess.run(
        [sys.executable, "-c", "import sys; sys.exit(3)"],
        capture_output=True,
        text=True,
        check=True,
    )
except subprocess.CalledProcessError as error:
    print("failed with code", error.returncode)

# shell=True is dangerous - never use it with user input
print(subprocess.run("echo safe literal", shell=True, capture_output=True, text=True).stdout.strip())
```

```text
hello from a subprocess
0
failed with code 3
safe literal
```

**Never use `shell=True` with input you did not write yourself.** On a system command
like `rm -rf`, an attacker-controlled value can inject extra commands. Pass a *list* of
arguments instead and let Python handle the quoting.

### `os` and `sys`

```python
import os
import sys
import tempfile
from pathlib import Path

print(os.getcwd())
print(sys.platform)
print(sys.version.split()[0])

# Environment variables (the home folder is spelled differently per OS)
home = os.environ.get("HOME") or os.environ.get("USERPROFILE", "not set")
print("home:", home)
os.environ["MY_APP_MODE"] = "test"
print("app mode:", os.environ["MY_APP_MODE"])

# Walking a directory tree
with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    (root / "a.txt").write_text("x", encoding="utf-8")
    (root / "sub").mkdir()
    (root / "sub" / "b.txt").write_text("y", encoding="utf-8")

    for current, dirs, files in os.walk(root):
        relative = Path(current).relative_to(root)
        print(f"{str(relative) or '.'}: {sorted(files)}")

# Making directories
os.makedirs("build/nested", exist_ok=True)
print(os.path.isdir("build/nested"))

# Command line arguments live in sys.argv
print("sys.argv has", len(sys.argv), "entries")
```

```text
C:\Users\you\project
win32
3.13.1
home: C:\Users\you
app mode: test
.: ['a.txt']
sub: ['b.txt']
True
sys.argv has 1 entries
```

(Your working directory and home folder will obviously be different.)

### `shutil`, `platform`, `tempfile`

```python
import platform
import shutil
import tempfile
from pathlib import Path

print(platform.python_version())
print(platform.system())
print(platform.machine())

# Copy, move and delete
with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    source = root / "source.txt"
    source.write_text("hello", encoding="utf-8")

    copied = root / "copied.txt"
    shutil.copy(source, copied)
    print(copied.read_text(encoding="utf-8"))

    moved = root / "moved.txt"
    shutil.move(copied, moved)
    print("copied gone:", not copied.exists(), "moved here:", moved.exists())

    shutil.rmtree(root / "subtree", ignore_errors=True)

# Temporary files
with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as handle:
    handle.write("scratch data")
    temp_name = handle.name
print("temp file written to a temp folder:", "AppData" in temp_name or "/tmp" in temp_name)
Path(temp_name).unlink()

# shutil has a copytree too
print(shutil.disk_usage(".").total > 0)
```

```text
3.13.1
Windows
AMD64
hello
copied gone: True moved here: True
temp file written to a temp folder: True
True
```

---

## 8. Maths, randomness and hashing

```python
import base64
import hashlib
import math
import random
import secrets
import uuid

print(math.sqrt(2), math.floor(2.7), math.ceil(2.1))
print(math.pi, round(math.pi, 4))
print(math.log(math.e), math.log10(1000))

# random: for simulations, shuffling, sampling - never for secrets
random.seed(42)
print(random.random())
print(random.randint(1, 6))
print(random.choice(["rock", "paper", "scissors"]))
deck = ["a", "b", "c", "d"]
random.shuffle(deck)
print(deck)
print(random.sample(range(100), 5))

# secrets: for tokens, passwords, API keys
print(secrets.token_urlsafe(32))
print(secrets.token_hex(16))
print(secrets.choice(["rock", "paper", "scissors"]))

# hashlib: a one-way fingerprint
digest = hashlib.sha256(b"hello world").hexdigest()
print(digest)
print(hashlib.sha256(b"hello world").hexdigest() == digest)   # deterministic
print(len(digest), "hex characters =", 256, "bits")

# base64: encoding, not encryption
encoded = base64.b64encode(b"hello world").decode()
print(encoded)
print(base64.b64decode(encoded).decode())

# uuid: unique identifiers
identifier = uuid.uuid4()
print(identifier)
print(len(str(identifier)))
```

```text
1.4142135623730951 2 3
3.141592653589793 3.1416
1.0 3.0
0.6394267984578837
1
scissors
['b', 'd', 'a', 'c']
[17, 94, 13, 86, 69]
5EiPIYmaxdtFimJ-iio0oHkBv5PgIx1vCFqbFhPxZYc
0e36690d40bb8a71a5cfb7d337c417f0
rock
b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9
True
64 hex characters = 256 bits
aGVsbG8gd29ybGQ=
hello world
2cacef70-9dba-4d63-972d-da250caaf61b
36
```

The three `secrets` lines produce a different value every time you run it — that is the
whole point of them. The rest is deterministic.

**Never use `random` for anything secret.** `random.seed(42)` makes the sequence
completely predictable. Use `secrets`, which draws from the operating system's
cryptographically secure random source.

---

## 9. Programming helpers

### `enum` — named constants

```python
from enum import Enum, auto


class Status(Enum):
    PENDING = auto()
    RUNNING = auto()
    DONE = auto()


print(Status.RUNNING)
print(Status.RUNNING.value)
print(Status(2) is Status.RUNNING)
print(list(Status))
```

```text
Status.RUNNING
2
True
[<Status.PENDING: 1>, <Status.RUNNING: 2>, <Status.DONE: 3>]
```

### `dataclasses` — data classes without boilerplate

```python
from dataclasses import dataclass, field


@dataclass
class ModelConfig:
    name: str
    temperature: float = 0.7
    max_tokens: int = 1024
    tags: list[str] = field(default_factory=list)


config = ModelConfig("gpt-4o-mini", tags=["fast"])
print(config)
print(config.name, config.temperature, config.max_tokens, config.tags)
```

```text
ModelConfig(name='gpt-4o-mini', temperature=0.7, max_tokens=1024, tags=['fast'])
gpt-4o-mini 0.7 1024 ['fast']
```

### `contextlib` — clean resource handling

```python
import contextlib
import tempfile
from pathlib import Path

# contextmanager turns a generator into a context manager
@contextlib.contextmanager
def tracked_file(path: Path):
    print(f"opening {path.name}")
    path.write_text("data", encoding="utf-8")
    try:
        yield path
    finally:
        print(f"cleaning up {path.name}")
        path.unlink()


with tempfile.TemporaryDirectory() as tmp:
    target = Path(tmp) / "scratch.txt"
    with tracked_file(target) as handle:
        print("inside the block:", handle.read_text(encoding="utf-8"))

# suppress: ignore a specific exception for a block
with contextlib.suppress(FileNotFoundError):
    Path("does-not-exist.txt").read_text(encoding="utf-8")
print("suppressed the missing file")

# ExitStack: manage a variable number of resources
with contextlib.ExitStack() as stack:
    paths = []
    for name in ["a.txt", "b.txt"]:
        path = Path(tempfile.gettempdir()) / name
        path.write_text("x", encoding="utf-8")
        stack.callback(path.unlink)
        paths.append(path)
    print("created", len(paths), "files")
print("all cleaned up:", not any(p.exists() for p in paths))
```

```text
opening scratch.txt
inside the block: data
cleaning up scratch.txt
suppressed the missing file
created 2 files
all cleaned up: True
```

### `argparse` — build a real command line tool

```python
import argparse
from collections import Counter
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the wordcount tool."""
    parser = argparse.ArgumentParser(
        prog="wordcount",
        description="Count the words in a text file.",
    )
    parser.add_argument("path", help="the file to read")
    parser.add_argument(
        "--min-length", type=int, default=1, help="ignore words shorter than this"
    )
    parser.add_argument(
        "--top", type=int, default=5, choices=[1, 3, 5, 10], help="how many words to show"
    )
    parser.add_argument("--ignore-case", action="store_true", help="treat Hello = hello")
    parser.add_argument("--encoding", default="utf-8", help="the file's encoding")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    text = Path(args.path).read_text(encoding=args.encoding)
    words = [w for w in text.split() if len(w) >= args.min_length]
    counts = Counter(w.lower() for w in words) if args.ignore_case else Counter(words)
    for word, count in counts.most_common(args.top):
        print(f"{count:>5}  {word}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 1:
        build_parser().print_help()
    else:
        main()
```

```text
usage: wordcount [-h] [--min-length MIN_LENGTH] [--top {1,3,5,10}]
                 [--ignore-case] [--encoding ENCODING]
                 path

Count the words in a text file.

positional arguments:
  path                  the file to read

options:
  -h, --help            show this help message and exit
  --min-length MIN_LENGTH
                        ignore words shorter than this
  --top {1,3,5,10}      how many words to show
  --ignore-case         treat Hello = hello
  --encoding ENCODING   the file's encoding
```

Run it like this:

```bash
python wordcount.py notes.txt --top 3 --ignore-case
```

### A few more worth knowing

```python
import abc
import operator
import statistics
from decimal import Decimal
from fractions import Fraction

# statistics: mean, median, mode, stdev
scores = [12, 15, 15, 18, 22, 25]
print(statistics.mean(scores))
print(statistics.median(scores))
print(statistics.stdev(scores))

# Decimal and Fraction: exact arithmetic
print(Decimal("0.1") + Decimal("0.2"))
print(0.1 + 0.2)
print(Fraction(1, 3) + Fraction(1, 6))

# operator: function versions of the operators
people = [{"name": "Ada", "age": 36}, {"name": "Alan", "age": 41}]
print(sorted(people, key=operator.itemgetter("age")))
print(max(people, key=operator.itemgetter("age"))["name"])

# abc: an abstract base class
class Shape(abc.ABC):
    @abc.abstractmethod
    def area(self) -> float:
        """Return the area of the shape."""


class Square(Shape):
    def __init__(self, side: float) -> None:
        self.side = side

    def area(self) -> float:
        return self.side**2


print(Square(3).area())
```

```text
17.833333333333332
16.5
4.875106836436168
0.3
0.30000000000000004
1/2
[{'name': 'Ada', 'age': 36}, {'name': 'Alan', 'age': 41}]
Alan
9
```

---

## 10. How to discover the standard library yourself

You cannot memorise 200 modules, and you do not need to. Here is how to find what you
need in under a minute.

```python
import json
import sys

# 1. What is in this module?
print([name for name in dir(json) if not name.startswith("_")][:12])

# 2. What does this function do?
print(json.dumps.__doc__.splitlines()[0])

# 3. How many top-level modules does the standard library have?
print(len(sys.stdlib_module_names))
```

```text
['JSONDecodeError', 'JSONDecoder', 'JSONEncoder', 'codecs', 'decoder', 'detect_encoding', 'dump', 'dumps', 'encoder', 'load', 'loads', 'scanner']
Serialize ``obj`` to a JSON formatted ``str``.
289
```

(The exact module count depends on your Python version — 289 on Python 3.13.)

The four tools at your disposal:

| Tool | What it does |
|---|---|
| `help(module)` | in the REPL, prints the module's docstring and every function |
| `dir(module)` | lists every name in the module |
| `help(module.function)` | prints the docstring and signature of one function |
| `pydoc module` | the same as `help()`, from the command line |

For example, in the Python REPL:

```text
>>> import collections
>>> help(collections.deque)
>>> import json
>>> help(json.dumps)
```

And on the command line:

```bash
python -m pydoc collections
python -m pydoc json.dumps
```

The official **Library Reference** at
[docs.python.org/3/library/index.html](https://docs.python.org/3/library/index.html) is
the full catalogue, grouped by topic. It is a reference, not a tutorial — use it to look
things up, and use `help()` to understand a specific object.

The habit to build: **before you write a utility function, ask "does the standard library
already have this?"** The answer is more often "yes" than you expect.

---

## 11. Cheat sheet: task to module

| If you want to… | Use | Key call |
|---|---|---|
| Build a file path | `pathlib` | `Path("a") / "b.txt"` |
| List files in a folder | `pathlib` | `p.glob("*.py")`, `p.rglob("*")` |
| Get today's date | `datetime` | `date.today()` |
| Format a timestamp | `datetime` | `t.strftime("%Y-%m-%d")` |
| Parse a timestamp | `datetime` | `datetime.strptime(s, "%Y-%m-%d")` |
| Handle time zones | `datetime`, `zoneinfo` | `datetime.now(ZoneInfo("Europe/London"))` |
| Count occurrences | `collections` | `Counter(items).most_common(5)` |
| Group items by key | `collections` | `defaultdict(list)` |
| Build a queue | `collections` | `deque(maxlen=100)` |
| Read a named record | `collections` | `namedtuple("Point", "x y")` |
| Chain / slice / group iterables | `itertools` | `chain`, `islice`, `groupby` |
| All combinations | `itertools` | `product`, `permutations`, `combinations` |
| Cache an expensive call | `functools` | `@cache`, `@lru_cache(maxsize=...)` |
| Sum a sequence | `functools` | `reduce(fn, seq, 0)` |
| Read/write JSON | `json` | `json.loads`, `json.dumps(obj, indent=2)` |
| Read/write CSV | `csv` | `csv.DictReader`, `csv.DictWriter` |
| Match text patterns | `re` | `re.search`, `re.findall`, `re.sub` |
| Wrap long text | `textwrap` | `textwrap.fill(text, width=80)` |
| Compare two texts | `difflib` | `difflib.unified_diff(a, b)` |
| Run another program | `subprocess` | `subprocess.run([...], capture_output=True)` |
| Read environment variables | `os` | `os.environ.get("KEY")` |
| Walk a directory tree | `os` | `os.walk(".")` |
| Copy / move / delete files | `shutil` | `shutil.copy`, `shutil.move`, `shutil.rmtree` |
| Temporary files | `tempfile` | `tempfile.TemporaryDirectory()` |
| Random simulation | `random` | `random.choice(items)` |
| Secure tokens | `secrets` | `secrets.token_urlsafe(32)` |
| Hash a value | `hashlib` | `hashlib.sha256(data).hexdigest()` |
| Unique IDs | `uuid` | `uuid.uuid4()` |
| Named constants | `enum` | `class Status(Enum): ...` |
| Data classes | `dataclasses` | `@dataclass` |
| Clean up resources | `contextlib` | `with contextlib.suppress(...)` |
| Command line arguments | `argparse` | `ArgumentParser().add_argument("--flag")` |
| Fake an object in a test | `unittest.mock` | `MagicMock()`, `patch(...)` |
| Abstract base class | `abc` | `@abc.abstractmethod` |
| Sort by a key | `operator` | `key=operator.itemgetter("age")` |
| Average / median | `statistics` | `statistics.mean(values)` |
| Exact money maths | `decimal` | `Decimal("0.1")` |
| Exact fractions | `fractions` | `Fraction(1, 3)` |

---

## 🧪 Try it yourself

**Exercise 1 — A file inventory tool.**
Write a script that takes a folder and prints: the number of files, the number of
folders, the total size in bytes, and the five most common file extensions. Use `pathlib`
for the traversal and `Counter` for the extensions.

<details>
<summary>Hint</summary>

`p.rglob("*")` gives every descendant. Filter with `p.is_file()` and `p.is_dir()`.
`p.suffix` gives the extension, but remember that `.gitignore`-style dotfiles give an
empty suffix, so filter those out.
</details>

<details>
<summary>Solution</summary>

```python
from collections import Counter
from pathlib import Path


def inventory(root: Path) -> None:
    files = [p for p in root.rglob("*") if p.is_file()]
    folders = [p for p in root.rglob("*") if p.is_dir()]
    total = sum(p.stat().st_size for p in files)
    extensions = Counter(p.suffix.lower() for p in files if p.suffix)

    print(f"root:    {root}")
    print(f"files:   {len(files)}")
    print(f"folders: {len(folders)}")
    print(f"size:    {total:,} bytes")
    print("top extensions:")
    for suffix, count in extensions.most_common(5):
        print(f"  {suffix or '(none)':<8} {count}")


if __name__ == "__main__":
    import sys

    inventory(Path(sys.argv[1] if len(sys.argv) > 1 else "."))
```

```text
root:    C:\Users\you\project
files:   42
folders: 7
size:    318,204 bytes
top extensions:
  .py       18
  .md        6
  .toml      3
  .txt       3
```

(Those numbers describe one particular project. Point the script at your own folder to
see yours.)
</details>

**Exercise 2 — Parse a log line.**
Write a function that takes a log line like
`2026-03-14T15:09:26Z INFO worker started pid=4211` and returns a dictionary with
`timestamp`, `level`, `message` and `pid`. Then use it to count how many lines per level
appear in a multi-line string.

<details>
<summary>Hint</summary>

One named-group regular expression does the whole job:
`r"(?P<ts>\S+) (?P<level>\w+) (?P<msg>.+) pid=(?P<pid>\d+)"`. Then feed the matches to
`Counter`.
</details>

<details>
<summary>Solution</summary>

```python
import re
from collections import Counter

LINE = re.compile(r"(?P<ts>\S+) (?P<level>\w+) (?P<msg>.+) pid=(?P<pid>\d+)")


def parse_log_line(line: str) -> dict[str, str]:
    """Return the fields of one structured log line."""
    match = LINE.search(line)
    if match is None:
        raise ValueError(f"not a log line: {line!r}")
    fields = match.groupdict()
    fields["pid"] = int(fields["pid"])
    return fields


if __name__ == "__main__":
    log = "\n".join(
        [
            "2026-03-14T15:09:26Z INFO worker started pid=4211",
            "2026-03-14T15:09:27Z ERROR worker crashed pid=4211",
            "2026-03-14T15:09:28Z INFO worker restarted pid=4211",
        ]
    )
    records = [parse_log_line(line) for line in log.splitlines()]
    print(records[0])
    print(Counter(r["level"] for r in records))
```

```text
{'ts': '2026-03-14T15:09:26Z', 'level': 'INFO', 'msg': 'worker started', 'pid': 4211}
Counter({'INFO': 2, 'ERROR': 1})
```
</details>

**Exercise 3 — A safe secret generator.**
Write a function that generates a URL-safe token of a given length, using `secrets` (not
`random`), and prints two of them plus their SHA-256 fingerprints so you can see that
the same input always gives the same fingerprint but the tokens are always different.

<details>
<summary>Hint</summary>

`secrets.token_urlsafe(nbytes)` gives roughly `nbytes * 1.3` characters.
`hashlib.sha256(token.encode()).hexdigest()` gives the fingerprint.
</details>

<details>
<summary>Solution</summary>

```python
import hashlib
import secrets


def make_token(num_bytes: int = 32) -> str:
    """Return a cryptographically secure, URL-safe token."""
    return secrets.token_urlsafe(num_bytes)


if __name__ == "__main__":
    first = make_token()
    second = make_token()
    print(first)
    print(second)
    print("different:", first != second)
    for token in (first, second):
        print(hashlib.sha256(token.encode()).hexdigest()[:32], "...")
```

```text
Lm8roMt1NpgdxUgwI-hqvsn6q4zbgjg12dQpHS3OUUw
wtQOXt87WWU2WD-Cx2REQspB9pbAED2e7fpCtd0vjY4
different: True
4d79e34fd9e12ac83aad8d5246b4d6d0 ...
68e8a59cca7f6a7f2f3996da65ae4d73 ...
```

(Your tokens and fingerprints will be different — that is the point.)
</details>

**Exercise 4 — Build a real CLI.**
Write `wordcount.py` using `argparse` with a required `path` argument, a `--top`
option with `choices`, and a `--min-length` option with `type=int`. Then run it on a file
you create.

<details>
<summary>Hint</summary>

Copy the `build_parser` and `main` functions from section 9. To make the script show its
help when run with no arguments, check `len(sys.argv) == 1` before calling `main()`.
</details>

<details>
<summary>Solution</summary>

```python
import argparse
from collections import Counter
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="wordcount", description="Count words in a file.")
    parser.add_argument("path", help="the file to read")
    parser.add_argument("--min-length", type=int, default=1, help="ignore shorter words")
    parser.add_argument("--top", type=int, default=5, choices=[1, 3, 5, 10], help="rows to show")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    text = Path(args.path).read_text(encoding="utf-8")
    words = [w for w in text.split() if len(w) >= args.min_length]
    for word, count in Counter(words).most_common(args.top):
        print(f"{count:>5}  {word}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 1:
        build_parser().print_help()
    else:
        main()
```

```bash
python wordcount.py notes.txt --top 3 --min-length 4
```

```text
   12  python
    7  standard
    5  library
```
</details>

---

## ✅ Checkpoint

**1. What does `p.stem` and `p.suffix` return for the path `report.final.pdf`?**

<details>
<summary>Answer</summary>

`p.stem` is `"report.final"` and `p.suffix` is `".pdf"`. The stem is everything before the
*last* dot.
</details>

**2. Why should you avoid `assert` for input validation in application code?**

<details>
<summary>Answer</summary>

Because Python removes all `assert` statements when run with `-O`, so the check silently
disappears. Use explicit `raise ValueError(...)`.
</details>

**3. What is the difference between a naive and an aware datetime?**

<details>
<summary>Answer</summary>

A naive datetime has no timezone attached (`t.tzinfo is None`); an aware one carries a
UTC offset. Mixing the two in arithmetic raises `TypeError`, and naive values are
ambiguous across time zones — so use `datetime.now(timezone.utc)`.
</details>

**4. Why must data be sorted before you use `itertools.groupby`?**

<details>
<summary>Answer</summary>

`groupby` groups *consecutive* equal items, so equal items separated by another value end
up in different groups. Sorting first puts all the equal values next to each other.
</details>

**5. What is the difference between `random` and `secrets`?**

<details>
<summary>Answer</summary>

`random` is fast and reproducible (and can be seeded), so it is fine for simulations and
shuffles. `secrets` uses the operating system's cryptographically secure source and is
the only correct choice for tokens, passwords and API keys.
</details>

**6. Why do you pass `newline=""` when writing a CSV file?**

<details>
<summary>Answer</summary>

Because on Windows Python would otherwise translate every `\n` into `\r\n` inside the
file, producing stray blank lines. `newline=""` tells Python not to translate.
</details>

**7. What is the difference between `re.match` and `re.search`?**

<details>
<summary>Answer</summary>

`re.match` only tries to match at the very start of the string. `re.search` scans the
whole string and returns the first match anywhere in it.
</details>

**8. What are three ways to discover an unfamiliar standard-library module?**

<details>
<summary>Answer</summary>

`help(module)` and `dir(module)` in the REPL, `python -m pydoc module` on the command
line, and the official Library Reference at
[docs.python.org/3/library/index.html](https://docs.python.org/3/library/index.html).
</details>

---

## 🐛 Common mistakes

| Mistake | What you see | Fix |
|---|---|---|
| Building paths with `"/".join(...)` or `f"{folder}/{name}"` | `FileNotFoundError` on Windows, or a doubled separator | Use `Path(folder) / name` |
| `datetime.now()` without a timezone | Off-by-hours bugs that only appear at midnight, or in summer | Use `datetime.now(timezone.utc)` or `datetime.now(ZoneInfo(...))` |
| Comparing a naive and an aware datetime | `TypeError: can't subtract offset-naive and offset-aware datetimes` | Pick one kind and stick to it; aware is the right choice |
| `groupby` on unsorted data | Groups look wrong and keys repeat | `sorted(data, key=...)` before `groupby` |
| `random` for API keys or passwords | The value is predictable — `random.seed(0)` reproduces it | Use `secrets.token_urlsafe()` |
| `json.dumps` on a `datetime` or `Path` | `TypeError: Object of type datetime is not JSON serializable` | Pass `default=str`, or convert the values first |
| Writing a CSV without `newline=""` | Blank lines appear between rows on Windows | `open(path, "w", newline="", encoding="utf-8")` |
| Using `re.match` when you meant "anywhere" | `None` returned even though the text is there | Use `re.search`, or `re.findall` |
| Greedy `.*` in a regex | `<.*>` swallows the whole line instead of the first tag | Use the non-greedy `<.*?>` |
| `subprocess.run(cmd, shell=True)` with any user input | Command injection — a real security hole | Pass a list of arguments and never use `shell=True` |
| Catching `Exception` and printing the message | Errors disappear silently and the program continues in a broken state | Catch the specific exception you expect, and let the rest propagate |
| Writing a utility function without checking the standard library | You maintain a buggy version of something that already exists | Search [the Library Reference](https://docs.python.org/3/library/index.html) first |

---

## 🔗 Resources

- [The Python Standard Library — official reference](https://docs.python.org/3/library/index.html)
  — the full catalogue, grouped by topic. Bookmark this.
- [pathlib — Python documentation](https://docs.python.org/3/library/pathlib.html) — every
  method of `Path`, with examples.
- [datetime — Python documentation](https://docs.python.org/3/library/datetime.html) —
  `strftime` codes, `timedelta` arithmetic and timezone handling.
- [collections — Python documentation](https://docs.python.org/3/library/collections.html) —
  `Counter`, `deque`, `defaultdict`, `namedtuple` and the rest.
- [itertools — Python documentation](https://docs.python.org/3/library/itertools.html) — every
  iterator recipe, including `groupby`.
- [functools — Python documentation](https://docs.python.org/3/library/functools.html) —
  `cache`, `lru_cache`, `partial`, `reduce` and `wraps`.
- [re — Python documentation](https://docs.python.org/3/library/re.html) — the regular
  expression syntax reference.
- [subprocess — Python documentation](https://docs.python.org/3/library/subprocess.html) —
  running other programs safely, without `shell=True`.
- [argparse — Python documentation](https://docs.python.org/3/library/argparse.html) — the
  official guide to command line arguments.
- [Python Module Index](https://docs.python.org/3/py-modindex.html) — an alphabetical list
  of every module in the standard library.
- [The standard library source on GitHub](https://github.com/python/cpython/tree/main/Lib) —
  read the actual implementation when the documentation is unclear.

---

## ➡️ Next

- [15 — Concurrency and async](15-concurrency-and-async.md) — your programs now have a
  large toolbox; next, make them fast: threads, processes, `asyncio` and the GIL.

**← Previous:** [13 — Testing](13-testing.md)
