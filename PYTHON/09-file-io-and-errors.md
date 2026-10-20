# File I/O and Errors

Every real program reads from somewhere and writes to somewhere. Python programs get their
input from files, and they leave their output behind in files — datasets, logs, cached LLM
responses, saved user preferences. When something goes wrong, Python does not stop and
print "something failed". It raises an *exception*: a signal that carries information
about what broke.

This file is about two sides of the same coin: **moving data in and out of your program**,
and **surviving when it goes wrong**. By the end you will be able to read and write text, CSV
and JSON files safely, and handle failure with precise exceptions instead of crashes.

> **⏱️ Time:** ~35 minutes
> **📚 Prereqs:** [08 Modules and packages](08-modules-and-packages.md)
> **🎯 By the end you can:** Read, write and parse files (text, CSV, JSON) safely, and handle
> failures with specific exceptions instead of letting your program crash.

---

## Why this matters for AI engineering

AI pipelines are, underneath the model calls, a pile of file I/O. You load a dataset from
CSV, send prompts to an LLM, cache the answers as JSON so you do not pay twice, write
evaluation results to disk, and log every request. If any of those steps silently
truncates a file, writes mojibake, or crashes on one malformed row, the whole pipeline
dies.

Error handling is even more important here, because **LLM calls fail constantly**: rate
limits, timeouts, malformed JSON in a model reply, a 500 from the provider. A script with
no `try`/`except` dies on the first hiccup. A script with `try`/`except` retries, logs the
problem, and keeps going.

---

## 1. Files are just bytes on disk

A **file** is a named block of bytes stored by the operating system. Python gives you an
*object* (a *file object*, usually called a *file handle*) that points at one of those
blocks and lets you move a position through it, read bytes, or write bytes.

```text
    your program
        |
        |  read() / write()
        v
   +-------------+          +---------------------------+
   | file object | ------> | notes.txt  (on disk)      |
   +-------------+          |                           |
        |                   | b"Hello from Python!\n"   |
        |                   +---------------------------+
        |
   the OS copies bytes between RAM and the disk
```

The important thing to know now: Python does not read the whole file into memory when you
open it. It keeps a pointer and fetches bytes as you ask for them. That is why "read the
file line by line" is cheaper than "read the whole file" for large files.

---

## 2. The file modes table

When you call `open()`, the second argument is the **mode**. It decides what you are
allowed to do with the file, and whether the file gets created, emptied, or left alone.

| Mode | Full name | File must exist? | Truncates existing content? | You can read? | You can write? |
|---|---|---|---|---|---|
| `r` | read (the default) | yes | no | yes | no |
| `w` | write | no — it is created | **yes — the file is emptied** | no | yes |
| `a` | append | no — it is created | no | no | yes, always at the end |
| `x` | exclusive create | no — it **fails** if the file exists | no | no | yes |
| `+` | update (combine with the above) | depends on the base mode | depends on the base mode | yes | yes |
| `b` | binary | — | — | bytes, not text | bytes, not text |

Read the `+` row as a suffix: `r+`, `w+`, `a+` and `x+` all mean "the same thing as the
base mode, but you may read as well as write". Binary mode (`rb`, `wb`, `ab`, `xb`) makes
the file object hand you `bytes` instead of `str` — you need it for images, PDFs, audio,
`.npz` files, and anything else that is not text.

Here is the two modes beginners meet first, side by side:

```python
from pathlib import Path
from tempfile import TemporaryDirectory

with TemporaryDirectory() as folder:
    path = Path(folder) / "log.txt"

    # Mode 'w': create the file (or empty it) and write.
    with open(path, "w", encoding="utf-8") as handle:
        handle.write("first run\n")

    # Mode 'a': open the existing file and add to the end.
    with open(path, "a", encoding="utf-8") as handle:
        handle.write("second run\n")

    print(path.read_text(encoding="utf-8"))
```

```text
first run
second run
```

And `x` mode, which refuses to overwrite anything. This is a genuine safety feature, not a
curiosity — it is exactly what you want for "write this file only if it does not exist yet":

```python
from pathlib import Path
from tempfile import TemporaryDirectory

with TemporaryDirectory() as folder:
    path = Path(folder) / "lock.txt"

    with open(path, "x", encoding="utf-8") as handle:
        handle.write("acquired\n")
    print("created lock")

    try:
        with open(path, "x", encoding="utf-8") as handle:
            handle.write("acquired again\n")
    except FileExistsError:
        print("lock already exists, refusing to overwrite")
```

```text
created lock
lock already exists, refusing to overwrite
```

---

## 3. `w` destroys the file — the classic data-loss bug

Read this twice, because it is the single most expensive mistake in this chapter.

**Opening a file in `w` mode does not mean "write to it". It means "empty it, then write to it".**
If the file already had 5,000 lines of collected results, `open(path, "w")` deletes all
5,000 lines the instant you open it — before you have written a single character. If your
program then crashes one line later, the data is gone and the file is empty.

```python
from pathlib import Path
from tempfile import TemporaryDirectory

with TemporaryDirectory() as folder:
    path = Path(folder) / "results.jsonl"

    path.write_text('{"id": 1}\n{"id": 2}\n{"id": 3}\n', encoding="utf-8")
    print("before:", repr(path.read_text(encoding="utf-8")))

    # The moment this line runs, the file is empty.
    with open(path, "w", encoding="utf-8") as handle:
        handle.write('{"id": 4}\n')

    print("after: ", repr(path.read_text(encoding="utf-8")))
```

```text
before: '{"id": 1}\n{"id": 2}\n{"id": 3}\n'
after:  '{"id": 4}\n'
```

Ids 1, 2 and 3 are gone. Nothing warned you. Python did exactly what you asked.

The rule of thumb:

- You want to **replace** the whole file → `w` is correct, but only once you are sure the new
  content is worth more than the old content.
- You want to **add** to the file → use `a`.
- You want to **read** it → use `r`, and never open a file you intend to write in `r+` unless you
  are certain about the position.

---

## 4. Always pass `encoding="utf-8"`

Text on disk is stored as **bytes**. To turn bytes into a `str`, Python uses an
**encoding** — a table that maps bytes to characters. There are many encodings. `utf-8` is
the modern world standard and can represent every language and every emoji.

The catch: **Python does not default to `utf-8` when opening files.** It uses the *locale*
encoding — the operating system's default. On most Linux machines that is `utf-8`. On many
Windows machines it is `cp1252`. Same file, same bytes, different characters depending on
where you run it.

```python
import locale

print("preferred encoding:", locale.getpreferredencoding(False))
```

```text
preferred encoding: cp1252
```

Now imagine you write a file containing the word "café" on Linux (2 bytes for `é` in
`utf-8`), and read it on Windows with `cp1252`. You get two garbage characters instead of
one `é`. This is called **mojibake** — text that has been decoded with the wrong table.

```python
text = "café"

# The right way: encode to bytes with utf-8, then decode with the wrong table.
broken = text.encode("utf-8").decode("latin-1")
print("correct: ", text)
print("mojibake:", broken)
```

```text
correct:  café
mojibake: cafÃ©
```

The two characters `Ã©` are what you get when the two bytes of `é` are decoded one at a
time with the wrong table. Scripts that mix scripts, emoji or non-Latin alphabets make
this even more visible — one wrong byte can become a completely unrelated character.

**The rule: always pass `encoding="utf-8"` to `open()`.** It costs four characters of typing and
removes an entire category of "works on my machine" bug. The same goes for
`Path.read_text()` and `Path.write_text()`.

---

## 5. Reading files

Let's use one concrete file for the whole section:

```text
Roses are red
Violets are blue
I write code
And so do you
```

There are four ways to pull data out of it.

### `read()` — the whole file as one string

```python
from pathlib import Path
from tempfile import TemporaryDirectory

with TemporaryDirectory() as folder:
    path = Path(folder) / "poem.txt"
    path.write_text(
        "Roses are red\nViolets are blue\nI write code\nAnd so do you\n",
        encoding="utf-8",
    )

    with open(path, "r", encoding="utf-8") as handle:
        content = handle.read()

    print(repr(content))
    print("characters:", len(content))
```

```text
'Roses are red\nViolets are blue\nI write code\nAnd so do you\n'
characters: 58
```

`read()` loads the **entire** file into memory as one string. Fine for a 4-line poem, a
terrible idea for a 2 GB log file.

### `readline()` — one line at a time

```python
from pathlib import Path
from tempfile import TemporaryDirectory

with TemporaryDirectory() as folder:
    path = Path(folder) / "poem.txt"
    path.write_text(
        "Roses are red\nViolets are blue\nI write code\nAnd so do you\n",
        encoding="utf-8",
    )

    with open(path, "r", encoding="utf-8") as handle:
        print(repr(handle.readline()))
        print(repr(handle.readline()))
```

```text
'Roses are red\n'
'Violets are blue\n'
```

Each call reads the next line, and the line still has its trailing `\n` (the "newline"
character). That is normal — you usually strip it off with `.strip()` or `.rstrip()`.

### `readlines()` — every line as a list of strings

```python
from pathlib import Path
from tempfile import TemporaryDirectory

with TemporaryDirectory() as folder:
    path = Path(folder) / "poem.txt"
    path.write_text(
        "Roses are red\nViolets are blue\nI write code\nAnd so do you\n",
        encoding="utf-8",
    )

    with open(path, "r", encoding="utf-8") as handle:
        lines = handle.readlines()

    print(lines)
```

```text
['Roses are red\n', 'Violets are blue\n', 'I write code\n', 'And so do you\n']
```

This is convenient, and it loads the whole file into memory just like `read()` did.

### Iterating the file object — the memory-efficient way

**This is the one you should reach for by default.** A file object is *iterable*: you can loop over
it directly, and Python fetches one line at a time from disk. Memory usage stays flat no
matter how big the file is.

```python
from pathlib import Path
from tempfile import TemporaryDirectory

with TemporaryDirectory() as folder:
    path = Path(folder) / "poem.txt"
    path.write_text(
        "Roses are red\nViolets are blue\nI write code\nAnd so do you\n",
        encoding="utf-8",
    )

    with open(path, "r", encoding="utf-8") as handle:
        for number, line in enumerate(handle, start=1):
            print(f"line {number}: {line.rstrip()}")
```

```text
line 1: Roses are red
line 2: Violets are blue
line 3: I write code
line 4: And so do you
```

`enumerate(handle, start=1)` gives you a running counter for free — very handy for error
messages that say "line 47 is malformed".

---

## 6. The `with` statement — always use it

Opening a file gives you an open handle. That handle holds an operating-system resource.
If your program never closes it, the file stays open until the object is garbage-collected
— and on Windows, an open file cannot be deleted or overwritten by other programs.

The `with` statement (a **context manager**) closes the file for you, **even if an
exception is raised inside the block**. This is the version you should write:

```python
from pathlib import Path
from tempfile import TemporaryDirectory

with TemporaryDirectory() as folder:
    path = Path(folder) / "log.txt"

    try:
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("partial write\n")
            raise RuntimeError("boom")
    except RuntimeError as error:
        print("caught:", error)

    # The `with` block already closed the file, even though the body crashed.
    print("handle closed:", handle.closed)
```

```text
caught: boom
handle closed: True
```

Under the hood, `with` is exactly this. The `finally` clause runs no matter what happens:

```python
from pathlib import Path
from tempfile import TemporaryDirectory

with TemporaryDirectory() as folder:
    path = Path(folder) / "log.txt"

    handle = open(path, "w", encoding="utf-8")
    try:
        handle.write("partial write\n")
        raise RuntimeError("boom")
    except RuntimeError as error:
        print("caught:", error)
    finally:
        handle.close()
        print("finally: file closed")
```

```text
caught: boom
finally: file closed
```

The `with` version is shorter and — this is the point — you cannot forget the `close()`.
Forgetting it is the most common bug in hand-written file code.

**Rule: always use `with open(...) as f:`.** Never write `f = open(...)` on its own.

---

## 7. `pathlib` — the modern way to handle paths

A **path** is the location of a file. `pathlib` gives you a `Path` object that understands
paths instead of making you paste strings together with backslashes.

```python
from pathlib import Path
from tempfile import TemporaryDirectory

with TemporaryDirectory() as folder:
    root = Path(folder)

    # The / operator joins path segments.
    data_dir = root / "data" / "raw"
    data_dir.mkdir(parents=True, exist_ok=True)

    notes = data_dir / "notes.txt"
    notes.write_text("hello from pathlib\n", encoding="utf-8")

    print("exists:", notes.exists())
    print("suffix:", notes.suffix)     # the extension, including the dot
    print("stem:", notes.stem)         # the name without the extension
    print("parent:", notes.parent.name)

    for child in sorted(data_dir.iterdir()):
        print("child:", child.name)
```

```text
exists: True
suffix: .txt
stem: notes
parent: raw
child: notes.txt
```

The methods worth memorising right now:

| Method | What it does |
|---|---|
| `Path("a/b/c.txt")` | build a path from parts |
| `path.exists()` | does it exist? |
| `path.read_text(encoding="utf-8")` | whole file as a string |
| `path.write_text(text, encoding="utf-8")` | write a string, replace the file |
| `path.iterdir()` | list the items inside a directory |
| `path.mkdir(parents=True, exist_ok=True)` | create the directory (and parents) |
| `path.name`, `path.stem`, `path.suffix`, `path.parent` | inspect the path |
| `path.unlink()` | delete the file |
| `path.rename(other)` | move/rename it |

`pathlib` has a lot more to it — `glob()`, `rglob()`, `resolve()`, `stat()` and more — and
you will meet the full tour in [14 Standard library](14-standard-library.md). For this
chapter, the table above is enough.

---

## 8. CSV files with the `csv` module

**CSV** (Comma-Separated Values) is the simplest way to store tabular data: one row per line,
columns separated by commas.

```text
name,language,year
Ada,Python,1843
Grace,Python,1952
```

You could split those lines on commas by hand — but that breaks the moment a cell contains
a comma (`"Smith, Ada",Python,1843`). The `csv` module handles the quoting rules for you.

### Writing CSV

```python
import csv
from pathlib import Path
from tempfile import TemporaryDirectory

rows = [
    {"name": "Ada", "language": "Python", "year": 1843},
    {"name": "Grace", "language": "Python", "year": 1952},
]

with TemporaryDirectory() as folder:
    path = Path(folder) / "pioneers.csv"

    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["name", "language", "year"])
        writer.writeheader()          # writes the column names as the first row
        writer.writerows(rows)        # writes every dict

    print(path.read_text(encoding="utf-8"))
```

```text
name,language,year
Ada,Python,1843
Grace,Python,1952
```

`csv.DictWriter` takes a list of dictionaries and asks for the column names up front
(`fieldnames`). It writes the header row for you with `writeheader()`.

### Reading CSV

`csv.DictReader` is the mirror image. It reads the first row as the column names and gives
you one dictionary per row.

```python
import csv
from pathlib import Path
from tempfile import TemporaryDirectory

with TemporaryDirectory() as folder:
    path = Path(folder) / "pioneers.csv"
    path.write_text(
        "name,language,year\nAda,Python,1843\nGrace,Python,1952\n",
        encoding="utf-8",
    )

    with open(path, "r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            print(row["name"], "->", row["language"], row["year"])
```

```text
Ada -> Python 1843
Grace -> Python 1952
```

### Why `newline=""` matters

The `csv` module writes `\r\n` line endings (the Windows convention). If you open the file
in Python's *text* mode **without** `newline=""`, Python's text layer also converts `\n`
into `\r\n` on the way out — and you end up with `\r\r\n`. The file is subtly corrupted:

```python
import csv
from pathlib import Path
from tempfile import TemporaryDirectory

rows = [{"name": "Ada", "language": "Python", "year": 1843}]

with TemporaryDirectory() as folder:
    path = Path(folder) / "pioneers.csv"

    # WRONG: no newline="" on write.
    with open(path, "w", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["name", "language", "year"])
        writer.writeheader()
        writer.writerows(rows)

    print("bytes:", path.read_bytes())
```

```text
bytes: b'name,language,year\r\r\nAda,Python,1843\r\r\n'
```

Look at those `\r\r\n` pairs. With `newline=""` you get clean `\r\n`.

**Rule: when you use the `csv` module, always pass `newline=""` to `open()`, both for reading and
for writing.** It is a two-word habit that prevents a subtle cross-platform bug.

---

## 9. JSON files with the `json` module

**JSON** (JavaScript Object Notation) is the default data format of the AI world. Every LLM API
request and response is JSON. Every config file you will ever meet is JSON.

JSON has exactly six types: **object** (`dict`), **array** (`list`), **string** (`str`),
**number** (`int`/`float`), **boolean** (`bool`), and **null** (`None`).

### `dumps` and `loads` — strings

| Function | Direction |
|---|---|
| `json.dumps(obj)` | Python object → JSON **string** |
| `json.loads(text)` | JSON **string** → Python object |

### `dump` and `load` — files

| Function | Direction |
|---|---|
| `json.dump(obj, file)` | Python object → JSON **file** |
| `json.load(file)` | JSON **file** → Python object |

Note the confusing part: `d` in `dumps`/`dump` means "**d**ata", `s` in `dumps`/`loads`
means "**s**tring". So `dumps` = "dump to string", `loads` = "load from string".

```python
import json
from pathlib import Path
from tempfile import TemporaryDirectory

payload = {
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "Hello, world!"}],
    "temperature": 0.2,
    "stream": False,
}

# indent=2 makes the output human-readable. ensure_ascii=False keeps
# non-ASCII characters (like emoji or accents) as themselves.
text = json.dumps(payload, indent=2, ensure_ascii=False)
print(text)

with TemporaryDirectory() as folder:
    path = Path(folder) / "request.json"
    path.write_text(text, encoding="utf-8")

    with open(path, "r", encoding="utf-8") as handle:
        loaded = json.load(handle)

    print("round trip equal:", loaded == payload)
```

```text
{
  "model": "gpt-4o-mini",
  "messages": [
    {
      "role": "user",
      "content": "Hello, world!"
    }
  ],
  "temperature": 0.2,
  "stream": false
}
round trip equal: True
```

Two options you will use constantly:

- `indent=2` — pretty-print with two-space indentation. Use it for anything a human will read.
- `ensure_ascii=False` — keep `café` and `naïve` as themselves instead of escaping them to
  `caf\u00e9`. Always pass it for human-facing output.

### The rule: JSON only holds six types

JSON has no `set`, no `datetime`, no `tuple`, no custom class. Try to serialise one and
you get a `TypeError`:

```python
import json
from datetime import datetime

bad = {
    "tags": {"ai", "agent"},            # a set - not JSON
    "created": datetime(2026, 1, 15),   # a datetime - not JSON
}

try:
    json.dumps(bad)
except TypeError as error:
    print("TypeError:", error)

# The fix: convert to JSON-friendly types first.
fixed = {
    "tags": sorted(bad["tags"]),          # set -> list
    "created": bad["created"].isoformat(),  # datetime -> string
}
print(json.dumps(fixed, indent=2))
```

```text
TypeError: Object of type set is not JSON serializable
{
  "tags": [
    "agent",
    "ai"
  ],
  "created": "2026-01-15T00:00:00"
}
```

The general rule: **tuples become lists, sets become lists, datetimes become ISO-8601
strings, and custom objects need a `to_dict()` method (or a `default=` function).** When
you get a `TypeError: Object of type X is not JSON serializable`, this table is the
answer.

| Python type | JSON equivalent | How to convert |
|---|---|---|
| `dict` | object | already fine |
| `list` | array | already fine |
| `tuple` | array | already fine (becomes a list) |
| `str` | string | already fine |
| `int`, `float` | number | already fine |
| `bool` | `true` / `false` | already fine |
| `None` | `null` | already fine |
| `set` | array | `sorted(my_set)` or `list(my_set)` |
| `datetime` | string | `my_dt.isoformat()` |
| custom object | object | `obj.to_dict()` or `json.dumps(..., default=str)` |

---

## 10. Exceptions: what they are

An **exception** is Python's way of saying "this operation could not be completed". When
something goes wrong, Python raises an exception object. If nothing catches it, the
exception travels up through your call stack, and the program stops and prints a
**traceback**.

A **traceback** is the list of function calls that were in progress when the exception was
raised. Read it from the bottom up: the last line tells you what went wrong, and the lines
above tell you where.

```python
import traceback


def divide(a, b):
    return a / b


def average(values):
    return divide(sum(values), len(values))


try:
    average([])          # an empty list means dividing by zero
except ZeroDivisionError:
    print(traceback.format_exc())
```

```text
Traceback (most recent call last):
  File "example.py", line 13, in <module>
    average([])          # an empty list means dividing by zero
    ~~~~~~~^^^^
  File "example.py", line 9, in average
    return divide(sum(values), len(values))
  File "example.py", line 5, in divide
    return a / b
           ~~^~~
ZeroDivisionError: division by zero
```

(Your file name and line numbers will be different — the shape is the same.)

The anatomy:

```text
Traceback (most recent call last):
  File "example.py", line 12, in <module>      <-- the line that started it all
    average([10, 20, 30])
  File "example.py", line 9, in average          <-- the call chain, innermost last
    return divide(sum(values), len(values))
  File "example.py", line 6, in divide
    return a / b
ZeroDivisionError: division by zero             <-- the actual problem
```

[00 How to use this course](00-how-to-use-this-course.md) has a full walkthrough of how to
read a traceback. The one-second version: **the last line is the diagnosis, the line above
it is the offending code**.

### The common built-in exceptions

| Exception | What it means | What you probably did wrong |
|---|---|---|
| `ValueError` | a value has the right type but the wrong contents | passed `int("abc")` or an out-of-range number |
| `TypeError` | an operation is not supported for this type | added a `str` to an `int`, or called a method that does not exist on the type |
| `KeyError` | a key is not in a dictionary | `config["api_key"]` where the key is missing or misspelled |
| `IndexError` | a list index is out of range | `items[10]` on a list of 3 items |
| `AttributeError` | an object has no such attribute | typo like `text.lenght`, or `None.something` |
| `FileNotFoundError` | the file does not exist | wrong path, or you did not create the directory |
| `FileExistsError` | the file already exists | used `x` mode on a file that is there |
| `IsADirectoryError` | the path is a folder, not a file | tried to `read_text()` a directory |
| `ZeroDivisionError` | you divided by zero | a divisor was 0 — a classic off-by-one or empty list |
| `RuntimeError` | something went wrong that has no more specific type | generic "this cannot work right now" |
| `UnicodeDecodeError` | the bytes are not valid in the encoding you chose | wrong `encoding=` — usually reading a binary file as text |
| `ModuleNotFoundError` | the import failed | the package is not installed — run `pip install` |

`KeyError` and `IndexError` both deserve a second look, because they are the "you asked for
something that is not there" pair:

```python
config = {"model": "gpt-4o-mini"}
items = ["a", "b"]

try:
    print(config["temperature"])
except KeyError as error:
    print("KeyError:", error)

try:
    print(items[5])
except IndexError as error:
    print("IndexError:", error)
```

```text
KeyError: 'temperature'
IndexError: list index out of range
```

---

## 11. `try` / `except` / `else` / `finally`

Four clauses, each with a precise job. The `else` and `finally` clauses are the ones
people get wrong, so here is exactly when each one runs.

| Clause | Runs when |
|---|---|
| `try` | always — this is the code you are protecting |
| `except` | only if the `try` block raised a matching exception |
| `else` | only if the `try` block finished **without** raising |
| `finally` | **always**, whether or not an exception happened |

```python
def divide(a, b):
    try:
        result = a / b
    except ZeroDivisionError:
        print("except: division by zero")
        return None
    else:
        print("else: no error, result is", result)
        return result
    finally:
        print("finally: always runs")


divide(10, 2)
divide(10, 0)
```

```text
else: no error, result is 5.0
finally: always runs
except: division by zero
finally: always runs
```

The ordering is visible in that output: `except` **or** `else` runs first, and `finally`
runs last, either way.

The idiomatic reason to put the "success" work in `else` rather than at the end of `try`:
anything in the `try` block is inside the danger zone. If the success path lives in
`else`, it cannot accidentally raise the exception you thought you were handling.

```python
def read_count(raw):
    """SAFE: the success path lives in `else`, out of the handler's reach."""
    try:
        count = int(raw)
    except ValueError:
        return 0
    else:
        return count + 1


def read_count_unsafe(raw):
    """UNSAFE: a bug in the success path is blamed on the wrong thing."""
    try:
        count = int(raw)
        return count + 1
    except ValueError:
        return 0


print(read_count("41"))         # 42
print(read_count("nope"))       # 0
print(read_count_unsafe("41"))  # 42
```

```text
42
0
42
```

Both versions give the same answer here, because nothing goes wrong. The difference shows
up the first time the code after the risky call has a bug of its own — in the unsafe
version that bug sits inside the `try` block, so the handler is one step closer to
swallowing it and reporting a misleading error.

---

## 12. Catch specific exceptions, never a bare `except`

You can write `except:` with nothing after it. **Do not.** A bare `except` catches *every*
exception, including `KeyboardInterrupt` (Ctrl+C), `SystemExit`, and genuine bugs like
`NameError` and `TypeError`. It hides the problem instead of handling it.

```python
def parse_port(value):
    try:
        return int(value)
    except ValueError as error:
        print(f"ValueError caught: {error}")
        return 0


print(parse_port("8080"))
print(parse_port("not-a-port"))
```

```text
8080
ValueError caught: invalid literal for int() with base 10: 'not-a-port'
0
```

The `as error` part binds the exception object to a name, so you can read its message
(`str(error)` or just `error`) and its attributes. That is how you find out *which* bad
value caused the problem.

Two more shapes worth knowing:

```python
# Catch several unrelated exception types in one clause.
def load(path):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()
    except (FileNotFoundError, PermissionError) as error:
        print(f"could not read {path}: {error}")
        return None


load("definitely-not-here.txt")
load("also-not-here.txt")
```

```text
could not read definitely-not-here.txt: [Errno 2] No such file or directory: 'definitely-not-here.txt'
could not read also-not-here.txt: [Errno 2] No such file or directory: 'also-not-here.txt'
```

```python
# Catch a type and everything that inherits from it.
class RetryableError(Exception):
    pass


def call():
    raise RetryableError("temporary glitch")


try:
    call()
except Exception as error:   # catches RetryableError, ValueError, everything
    print("broad catch:", type(error).__name__)
```

```text
broad catch: RetryableError
```

Use the narrowest handler that covers the failure you actually expect. `except Exception`
is acceptable at the top level of a program (so the program prints something friendly
instead of a raw traceback) — `except:` never is.

---

## 13. Raising your own errors, and chaining

`raise` starts an exception. It is how you tell the caller "this input is not acceptable":

```python
def set_temperature(value):
    if not 0.0 <= value <= 2.0:
        raise ValueError(f"temperature must be between 0 and 2, got {value}")
    return value


try:
    set_temperature(5)
except ValueError as error:
    print("rejected:", error)
```

```text
rejected: temperature must be between 0 and 2, got 5
```

Raising is better than returning a special "error value" like `None` or `-1`, because the
error message travels with the exception, and the stack trace tells you *where* it
happened.

### Chaining with `raise ... from e`

When you catch an error and raise a more meaningful one, use `raise NewError(...) from e`.
The `from` part **chains** the two: the new error keeps a reference to the original in
`__cause__`, and Python prints both — "The above exception was the direct cause of the
following exception".

```python
class ConfigError(Exception):
    """Raised when the application configuration is missing or invalid."""


def load_settings(path):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()
    except FileNotFoundError as error:
        raise ConfigError(f"no settings file at {path}") from error


try:
    load_settings("missing.json")
except ConfigError as error:
    print("caught:", error)
    print("root cause:", type(error.__cause__).__name__)
```

```text
caught: no settings file at missing.json
root cause: FileNotFoundError
```

Without the `from error`, the original error would be swallowed and the traceback would
only show `ConfigError` — you would lose the fact that the real problem was a missing
file.

---

## 14. Custom exceptions

A **custom exception** is a class of your own that inherits from `Exception`. Define it so
callers can catch *your* errors specifically instead of catching everything.

```python
class RateLimitError(Exception):
    """Raised when the model provider rejects a request for quota reasons."""

    def __init__(self, message, retry_after=60):
        super().__init__(message)          # sets up Exception's own state
        self.retry_after = retry_after      # your extra attribute


try:
    raise RateLimitError("quota exceeded", retry_after=30)
except RateLimitError as error:
    print("message:", error)
    print("retry after:", error.retry_after)
```

```text
message: quota exceeded
retry after: 30
```

Two rules:

1. **Inherit from `Exception`, not from `BaseException`.** `BaseException` is the parent of
`KeyboardInterrupt` and `SystemExit`; inheriting from it means Ctrl+C would no longer stop
your program cleanly.
2. **Give it a docstring.** One line that says when it is raised. Your future self will thank you.

---

## 15. `logging` beats `print`

`print()` writes to standard output. It has no levels, no timestamps, no file destination,
and it cannot be turned off without editing your code. That is fine for a quick script and
wrong for anything you will run more than once.

The `logging` module gives you **levels** (how important is this message?),
**timestamps**, and
**destinations** (the terminal, a file, both).

| Level | When to use it |
|---|---|
| `DEBUG` | detailed diagnostics you only want while debugging |
| `INFO` | normal progress: "loaded 1200 rows" |
| `WARNING` | something is off but the program continues |
| `ERROR` | this operation failed |
| `CRITICAL` | the program cannot continue |

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)-8s %(name)s: %(message)s",
)

logger = logging.getLogger("pipeline")
logger.debug("loading dataset")
logger.info("loaded 1200 rows")
logger.warning("row 87 has an empty embedding")
logger.error("failed to embed row 88")
logger.critical("shutting down")
```

```text
DEBUG    pipeline: loading dataset
INFO     pipeline: loaded 1200 rows
WARNING  pipeline: row 87 has an empty embedding
ERROR    pipeline: failed to embed row 88
CRITICAL pipeline: shutting down
```

Now change the level to `logging.WARNING` and the first three lines disappear. **That is
the point of levels** — one line of configuration controls the noise, and you never have
to delete your debug statements.

### Logging to a file

Pass a `FileHandler` to `basicConfig` to write the log to disk instead of the terminal.

```python
import logging
from pathlib import Path
from tempfile import TemporaryDirectory

with TemporaryDirectory() as folder:
    log_path = Path(folder) / "pipeline.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.FileHandler(log_path, encoding="utf-8")],
        force=True,        # replace any handlers set up earlier
    )

    logger = logging.getLogger("pipeline")
    logger.info("job started")
    logger.warning("cache miss for prompt %s", "summarise-42")

    logging.shutdown()     # flush the file buffer before reading it

    print(log_path.read_text(encoding="utf-8"))
```

```text
2026-10-20 15:02:11,204 INFO job started
2026-10-20 15:02:11,205 WARNING cache miss for prompt summarise-42
```

(The timestamps will of course show your machine's clock.)

Two details worth copying:

- `logger.warning("cache miss for prompt %s", "summarise-42")` — pass the values as extra
  arguments instead of building the string yourself. The message is only formatted if the
  log record is actually emitted, so unused `DEBUG` messages cost nothing.
- `logging.shutdown()` flushes the buffer, so the file is complete when you read it immediately
  afterwards.

---

## 16. Missing files, and creating directories safely

Two errors show up constantly in real scripts:

- `FileNotFoundError` — the file is not there.
- `FileNotFoundError` when you try to write to `output/data/report.json` and the `output/data`
  directory does not exist.

The fix for the second one is `mkdir(parents=True, exist_ok=True)`:

- `parents=True` — create any missing parent directories, not just the last one.
- `exist_ok=True` — do not raise if the directory already exists.

```python
from pathlib import Path
from tempfile import TemporaryDirectory

with TemporaryDirectory() as folder:
    root = Path(folder)
    target = root / "data" / "raw" / "input.json"

    try:
        target.read_text(encoding="utf-8")
    except FileNotFoundError:
        print("not found, creating it")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("{}", encoding="utf-8")

    print("exists:", target.exists())
    print("content:", target.read_text(encoding="utf-8"))
```

```text
not found, creating it
exists: True
content: {}
```

`mkdir(parents=True, exist_ok=True)` is the single most useful line in this file. Put it
at the top of every script that writes output.

---

## 17. Writing files safely (the atomic write)

There is one more way to be destroyed by `w` mode: your program crashes *between*
truncating the file and writing the new content. The old content is already gone, and the
new content is not there yet.

The fix is an **atomic write**: write to a temporary file first, then move it into place
with `os.replace()`. On both Windows and Linux, `os.replace()` swaps the files in a single
filesystem operation — so readers see either the old file or the new file, never a
half-written one.

```python
import os
from pathlib import Path
from tempfile import TemporaryDirectory


def write_atomically(path, text):
    """Write to a temporary file, then rename it into place."""
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    os.replace(temporary, path)      # atomic rename


with TemporaryDirectory() as folder:
    path = Path(folder) / "state.json"

    write_atomically(path, '{"status": "ok"}')
    print("content:", path.read_text(encoding="utf-8"))
    print("temp file left behind:", path.with_name(path.name + ".tmp").exists())
```

```text
content: {"status": "ok"}
temp file left behind: False
```

Keep the temporary file in the **same folder** as the target — `os.replace()` cannot move
a file across filesystems, and a different volume means a copy-then-delete, which is not
atomic.

---

## 18. Why AI pipelines are full of file and JSON I/O

Now let's put the whole chapter together in the place you will actually meet it: **a
response cache** that stops you paying for the same LLM call twice.

```python
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory


def cache_key(prompt):
    """A short, stable filename derived from the prompt text."""
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:16]


def fake_llm_call(prompt):
    """Stands in for a real API call so the example runs offline."""
    print("   [network] calling the model...")
    return f"ANSWER({prompt[:20]}...)"


def ask_with_cache(prompt, cache_dir):
    cache_file = cache_dir / f"{cache_key(prompt)}.json"

    if cache_file.exists():
        with open(cache_file, "r", encoding="utf-8") as handle:
            return json.load(handle)["answer"]

    answer = fake_llm_call(prompt)
    with open(cache_file, "w", encoding="utf-8") as handle:
        json.dump({"prompt": prompt, "answer": answer}, handle, indent=2)
    return answer


with TemporaryDirectory() as folder:
    cache_dir = Path(folder) / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    print(ask_with_cache("What is RAG?", cache_dir))
    print(ask_with_cache("What is RAG?", cache_dir))
```

```text
   [network] calling the model...
ANSWER(What is RAG?...)
ANSWER(What is RAG?...)
```

The second call did not hit the network. That pattern — **hash the key, check the file,
write the file** — is what every LLM caching layer, evaluation runner and
prompt-management tool is built from.

The same three ideas cover most of what real AI code does with files:

| Goal | The pattern |
|---|---|
| Cache an expensive LLM answer | hash the prompt → filename → JSON file |
| Store evaluation results | one JSON object per result, or one JSONL file with one object per line |
| Load a dataset | `csv.DictReader` for tables, `json.load` for nested records |
| Record what happened | `logging` with a file handler, not `print` |
| Survive a bad row | `try`/`except` around the row, `logging.error`, keep going |

---

## 🧪 Try it yourself

Do these in order. Type the code yourself — typing is the part that teaches.

### Exercise 1 — Predict the truncation

Write a script that:

1. Creates a file `notes.txt` containing the text `important\n`.
2. Prints the file's contents.
3. Opens it in `w` mode and writes `replaced\n`.
4. Prints the file's contents again.

Then, without running it, write down what you think the second print will show. Run it,
then check your prediction.

<details>
<summary>Hint</summary>

`open(path, "w")` empties the file at the moment you open it, not when you write to it.

</details>

<details>
<summary>Solution</summary>

```python
from pathlib import Path
from tempfile import TemporaryDirectory

with TemporaryDirectory() as folder:
    path = Path(folder) / "notes.txt"
    path.write_text("important\n", encoding="utf-8")

    print(path.read_text(encoding="utf-8"))

    with open(path, "w", encoding="utf-8") as handle:
        handle.write("replaced\n")

    print(path.read_text(encoding="utf-8"))
```

```text
important
replaced
```

</details>

### Exercise 2 — A line counter that scales

Write a function `count_lines(path)` that returns the number of non-empty lines in a text
file. Use iteration over the file object, not `readlines()`. Test it on a file with 3
lines, one of which is blank.

<details>
<summary>Hint</summary>

Loop over the file object directly: `for line in handle:`. Strip the line, then check
whether it is empty.

</details>

<details>
<summary>Solution</summary>

```python
from pathlib import Path
from tempfile import TemporaryDirectory


def count_lines(path):
    """Count the non-empty lines in a file without loading it all into memory."""
    total = 0
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                total += 1
    return total


with TemporaryDirectory() as folder:
    path = Path(folder) / "notes.txt"
    path.write_text("alpha\n\nbeta\n", encoding="utf-8")
    print(count_lines(path))
```

```text
2
```

</details>

### Exercise 3 — Filter a CSV

Write a script that reads `scores.csv` (columns `name,score`) and writes `passed.csv`
containing only the students whose score is 80 or more. The header must be written to the
new file too.

<details>
<summary>Hint</summary>

`csv.DictReader` gives you dictionaries. Remember `row["score"]` is a **string**, so
convert it with `int(...)` before comparing it with 80.

</details>

<details>
<summary>Solution</summary>

```python
import csv
from pathlib import Path
from tempfile import TemporaryDirectory

with TemporaryDirectory() as folder:
    source = Path(folder) / "scores.csv"
    target = Path(folder) / "passed.csv"

    source.write_text(
        "name,score\nAda,98\nGrace,72\nAlan,80\nEdsger,91\n",
        encoding="utf-8",
    )

    with open(source, "r", encoding="utf-8", newline="") as reader:
        rows = list(csv.DictReader(reader))

    with open(target, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["name", "score"])
        writer.writeheader()
        for row in rows:
            if int(row["score"]) >= 80:
                writer.writerow(row)

    print(target.read_text(encoding="utf-8"))
```

```text
name,score
Ada,98
Alan,80
Edsger,91
```

</details>

### Exercise 4 — Make a set JSON-safe

Write a function `to_json_safe(value)` that converts a `set` into a sorted `list` and a
`datetime` into an ISO string, and leaves everything else alone. Then use `json.dumps` to
prove it works.

<details>
<summary>Hint</summary>

`isinstance(value, set)` and `isinstance(value, datetime)` are your friends. Remember to
import `datetime` from the `datetime` module.

</details>

<details>
<summary>Solution</summary>

```python
import json
from datetime import datetime


def to_json_safe(value):
    """Convert the two common non-JSON types into JSON-friendly ones."""
    if isinstance(value, set):
        return sorted(value)
    if isinstance(value, datetime):
        return value.isoformat()
    return value


payload = {"tags": {"ai", "agent"}, "created": datetime(2026, 1, 15)}
print(json.dumps(payload, default=to_json_safe, indent=2))
```

```text
{
  "tags": [
    "agent",
    "ai"
  ],
  "created": "2026-01-15T00:00:00"
}
```

</details>

### Exercise 5 — A custom error with a retry policy

Define `class RateLimitError(Exception)`. Write a function `call_model(attempts)` that
raises `RateLimitError` on the first two attempts and returns `"ok"` on the third, using a
`try`/`except` loop. Print each attempt.

<details>
<summary>Hint</summary>

`for attempt in range(1, attempts + 1):` with a `try`/`except RateLimitError` inside.
`return` exits the function.

</details>

<details>
<summary>Solution</summary>

```python
class RateLimitError(Exception):
    """Raised when the model provider rejects a request for quota reasons."""


def call_model(attempts):
    for attempt in range(1, attempts + 1):
        try:
            print(f"attempt {attempt}")
            if attempt < 3:
                raise RateLimitError("429 Too Many Requests")
            return "ok"
        except RateLimitError as error:
            print("  retrying after:", error)
    return "gave up"


print(call_model(5))
```

```text
attempt 1
  retrying after: 429 Too Many Requests
attempt 2
  retrying after: 429 Too Many Requests
attempt 3
ok
```

</details>

### Exercise 6 — Filter a log file by level

Configure `logging` to write to `app.log` with `level=logging.INFO`, then emit one `INFO`
and one `DEBUG` message. Read the file back and print how many lines it contains. Explain
why the `DEBUG` line is missing.

<details>
<summary>Hint</summary>

`logging.basicConfig(level=logging.INFO, handlers=[logging.FileHandler(path,
encoding="utf-8")], force=True)`. Remember `logging.shutdown()` before reading the file.

</details>

<details>
<summary>Solution</summary>

```python
import logging
from pathlib import Path
from tempfile import TemporaryDirectory

with TemporaryDirectory() as folder:
    log_path = Path(folder) / "app.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(message)s",
        handlers=[logging.FileHandler(log_path, encoding="utf-8")],
        force=True,
    )

    logger = logging.getLogger("app")
    logger.info("job started")
    logger.debug("this one is filtered out")
    logging.shutdown()

    lines = log_path.read_text(encoding="utf-8").splitlines()
    print("lines in the file:", len(lines))
    for line in lines:
        print(line)
```

```text
lines in the file: 1
INFO job started
```

The `DEBUG` message was filtered out because the handler's level is `INFO`, and `DEBUG` is
less important than `INFO`.

</details>

---

## ✅ Checkpoint

Answer these without looking back. If you cannot, go re-read the section it came from.

**1. What does `open("data.txt", "w")` do to `data.txt` if it already exists?**

<details>
<summary>Answer</summary>

It **empties the file** (truncates it to zero bytes) the moment you open it, then writes
what you give it. Any previous content is gone, even if your program crashes before
writing a single character.

</details>

**2. Why should you always pass `encoding="utf-8"` to `open()`?**

<details>
<summary>Answer</summary>

Python's default is the operating system's locale encoding, which is `cp1252` on many
Windows machines and `utf-8` on Linux. The same bytes then decode into different
characters on different machines, producing mojibake. `utf-8` is the world standard and
removes the whole class of bug.

</details>

**3. Which read method should you use for a 1 GB log file, and why?**

<details>
<summary>Answer</summary>

Iterate over the file object (`for line in handle:`). `read()` and `readlines()` load the
whole file into memory; iterating pulls one line at a time, so memory usage stays flat.

</details>

**4. What is the difference between `except`, `else` and `finally`?**

<details>
<summary>Answer</summary>

`except` runs only if the `try` block raised a matching exception. `else` runs only if the
`try` block finished successfully. `finally` always runs, either way.

</details>

**5. Why is a bare `except:` discouraged?**

<details>
<summary>Answer</summary>

It catches everything — including `KeyboardInterrupt`, `SystemExit`, and real bugs like
`NameError` — and hides the cause instead of handling it. Catch the specific exception
types you expect.

</details>

**6. What does `raise ConfigError("no settings file") from error` do that plain `raise` does not?**

<details>
<summary>Answer</summary>

It **chains** the new exception to the original one. The original is kept in
`error.__cause__` and Python prints both tracebacks, so you keep the root cause (for
example `FileNotFoundError`) instead of losing it.

</details>

**7. Which JSON-native Python types are *not* supported by `json.dumps`, and how do you fix that?**

<details>
<summary>Answer</summary>

`set`, `datetime`, `tuple` (as a tuple, it becomes a list) and custom objects are not JSON
types. Convert them first: `sorted(my_set)`, `my_dt.isoformat()`, `list(my_tuple)`, or
pass `default=str` / a custom function to `json.dumps`.

</details>

**8. When must you pass `newline=""` to `open()`?**

<details>
<summary>Answer</summary>

Whenever you use the `csv` module, for both reading and writing. The csv module writes
`\r\n` itself; without `newline=""` Python's text layer converts it again and you get
`\r\r\n` — a corrupted file.

</details>

---

## 🐛 Common mistakes

| Mistake | What you see | Fix |
|---|---|---|
| Using `w` mode to "append" to a file | the old content vanishes, silently | use `a` mode, or read + write to a new path |
| Opening a file without `with` | the file stays open; on Windows you cannot delete or overwrite it | always `with open(...) as f:` |
| Forgetting `encoding="utf-8"` | `UnicodeDecodeError` on Windows, or mojibake like `cafÃ©` | pass `encoding="utf-8"` to `open`, `read_text` and `write_text` |
| Using `csv` without `newline=""` | `\r\r\n` in the file; blank rows when reading on Windows | always pass `newline=""` with the `csv` module |
| Bare `except:` | the real error is swallowed and you see "something went wrong" | catch the specific exception types |
| `except Exception:` around everything | genuine bugs get hidden and mislabelled | narrow the handler; use `except Exception` only at the top level |
| Comparing `row["score"] >= 80` from a CSV | `TypeError: '>=' not supported between 'str' and 'int'` | convert first: `int(row["score"]) >= 80` |
| `json.dumps` on a `set` or `datetime` | `TypeError: Object of type set is not JSON serializable` | convert to a `list` / an ISO string, or use `default=` |
| Writing to `output/report.json` when `output/` does not exist | `FileNotFoundError: [Errno 2] No such file or directory` | `path.parent.mkdir(parents=True, exist_ok=True)` first |
| `print()` for anything you want to keep | no timestamps, no levels, lost when the terminal closes | use `logging` with a file handler |
| Assuming the file exists | `FileNotFoundError` on the first run of your script | create it, or handle the error with `try`/`except FileNotFoundError` |
| Catching `Exception` and returning `None` | the caller cannot tell "no result" from "it broke" | log the error and re-raise, or return a result object that carries the error |

---

## 🔗 Resources

- [Input and Output — Python Tutorial](https://docs.python.org/3/tutorial/inputoutput.html) — the
  official tutorial chapter on reading and writing files, including the `with` statement.
- [csv — CSV File Reading and Writing](https://docs.python.org/3/library/csv.html) — the reference
  for `DictReader`, `DictWriter` and the `newline=""` rule.
- [json — JSON encoder and decoder](https://docs.python.org/3/library/json.html) — every option for
  `dumps`, `loads`, `dump` and `load`, including `indent` and `ensure_ascii`.
- [logging — Logging HOWTO](https://docs.python.org/3/library/logging.html) — the official guide to
  levels, handlers, formatters and `basicConfig`.
- [pathlib — Object-oriented filesystem paths](https://docs.python.org/3/library/pathlib.html) — the
  full `Path` API; the standard library chapter in this course covers the essentials.
- [Errors and Exceptions — Python Tutorial](https://docs.python.org/3/tutorial/errors.html) — the
  official explanation of `try`/`except`/`else`/`finally` and exception chaining.
- [Built-in Exceptions](https://docs.python.org/3/library/exceptions.html) — the complete list of
  Python's built-in exception types.
- [traceback — Extract, format and print information about Python stack traces](https://docs.python.org/3/library/traceback.html)
  — how to capture a traceback as text, which is what you need to log a failure properly.
- [tempfile — Generate temporary files and directories](https://docs.python.org/3/library/tempfile.html)
  — `TemporaryDirectory`, the cleanest way to test file-handling code without leaving junk
  behind.
- [os.replace()](https://docs.python.org/3/library/os.html#os.replace) — the documentation for the
  atomic rename used by the safe-write pattern.

---

## ➡️ Next

- [10 Object-oriented programming](10-object-oriented-programming.md) — bundle data and behaviour
  into classes, then use `dataclass` to write them without boilerplate.

**← Previous:** [08 Modules and packages](08-modules-and-packages.md)
