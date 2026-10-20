# Practice Projects

> **⏱️ Time:** ~2 hours per project (8 projects, ~12 hours total)
> **📚 Prereqs:** [15 — Concurrency and async](15-concurrency-and-async.md)
> **🎯 By the end you can:** build a complete, tested, structured Python program from a blank file

---

Reading about code is not the same as being able to write it. This file is the bridge.

Each project below is small enough to finish in one sitting and big enough to force you to use
something you have just learned. **Do them in order.** Each one adds exactly one new idea on top of
the last, and by Project 8 you will have written a small search engine over your own notes.

**The rules:**

1. **Do not look at the solution until you have tried.** The hints are folded away for a reason.
2. **Write it in a real folder, not a scratch file.** Each project gets its own directory.
3. **Every project gets tests.** Even a small one. Testing is a habit, not a punishment.
4. **Break it on purpose at least once.** Introduce a bug, see the traceback, fix it. That is
   debugging practice, and debugging is 60% of the job.
5. **Commit after each project.** `git commit -m "Project 3: expense tracker"`. You will be
   surprised how much your own history teaches you.

---

## Why this matters for AI engineering

Almost every AI system you will ever build is a program that reads something, decides something, and
writes something. That is exactly what these eight projects are, in miniature:

- **Project 3** reads and writes JSON — the format every LLM API, vector store and config file
  uses.
- **Project 6** walks a folder and checks every link — the shape of a documentation crawler, a
  dataset validator or an ingestion pipeline.
- **Project 7** is a small, well-layered, well-tested application: a `dataclass` for the data, a
  class that owns it, a CLI at the edge, and a test suite. That is the structure of a real Python
  service, at toy scale.
- **Project 8** is a retrieval engine: load documents, index them, score a query, return the best
  passages. Strip out the TF-IDF and put in an embedding model, and you have the core of a RAG
  system.

The habits are the point, not the projects. Write the test before you trust the code. Handle the
error instead of crashing. Keep the data logic separate from the printing. **Those four habits are
the difference between a script that works on your machine and a service that works in production.**

---

## How to use this file

Each project has the same structure:

| Section | What it gives you |
|---|---|
| **Brief** | What you are building, in one paragraph. |
| **You will practise** | The specific Python you are forced to use. |
| **Requirements** | A numbered checklist. Tick these off. |
| **Starter** | A working skeleton you can run immediately, with the fiddly parts done for you. |
| **Hints** | Folded. Open them one at a time, only when you are genuinely stuck. |
| **Tests to write** | Folded, with example test code you can adapt. |
| **Stretch goals** | For when the project is finished and you want more. |
| **Done means** | The definition of finished. Do not move on before this. |

---

## The project ladder

| # | Project | New idea it forces you to learn | Time |
|:-:|---|---|---|
| 1 | [Number guessing game](#project-1--the-number-guessing-game) | Loops, user input, randomness | 30 min |
| 2 | [Unit converter CLI](#project-2--unit-converter-cli) | `argparse`, functions, lookup tables | 45 min |
| 3 | [Expense tracker](#project-3--expense-tracker) | JSON files, dataclasses, error handling | 90 min |
| 4 | [CSV log analyser](#project-4--csv-log-analyser) | `csv`, `collections`, generators | 60 min |
| 5 | [Password tools](#project-5--password-generator-and-strength-checker) | `secrets`, strings, entropy | 60 min |
| 6 | [Markdown link checker](#project-6--markdown-link-checker) | Regex, `pathlib`, concurrency | 90 min |
| 7 | [Task tracker](#project-7--task-tracker-with-oop) | Classes, enums, `pytest` | 120 min |
| 8 | [Notes search engine](#project-8--notes-search-engine-mini-rag) | Putting it all together | 120 min |

---

## Project 1 — The number guessing game

**Brief.** The computer picks a random number between 1 and 100. The player guesses. After each
guess the computer says "too high" or "too low". The game ends when the player finds the number, and
reports how many guesses it took. The player can then play again.

**You will practise:** `input()`, `int()`, `while` loops, `random`, f-strings, and the habit of
printing clearly.

### Requirements

1. Pick a random integer from 1 to 100 inclusive.
2. Ask the player for a guess and convert it to an integer.
3. Tell the player whether the guess was too high, too low, or correct.
4. Count the guesses and report the total when the player wins.
5. Reject non-numeric input without crashing — tell the player and ask again.
6. Ask "Play again? (y/n)" and loop if the answer is `y`.

### Starter

```python
# guessing_game.py
import random


def play_round(minimum: int = 1, maximum: int = 100) -> int:
    """Play one round. Returns the number of guesses the player needed."""
    secret = random.randint(minimum, maximum)
    guesses = 0

    while True:
        raw = input(f"Guess a number between {minimum} and {maximum}: ").strip()
        try:
            guess = int(raw)
        except ValueError:
            print("That is not a whole number. Try again.")
            continue

        guesses += 1

        if guess < secret:
            print("Too low.")
        elif guess > secret:
            print("Too high.")
        else:
            print(f"Correct! It was {secret}, and you found it in {guesses} guesses.")
            return guesses


def main() -> None:
    print("=== Number Guessing Game ===")
    while True:
        play_round()
        again = input("Play again? (y/n): ").strip().lower()
        if again != "y":
            print("Thanks for playing.")
            break


if __name__ == "__main__":
    main()
```

Run it: `python guessing_game.py`

### Hints

<details>
<summary>Hint for requirement 5</summary>

Wrap the `int()` call in `try` / `except ValueError` and `continue` the loop. The `except` block
should print a friendly message. Note that the `continue` skips the rest of the loop body, so the
guess counter is not incremented for invalid input — which is what you want.

</details>

<details>
<summary>Hint for requirement 6</summary>

`input(...).strip().lower()` normalises the answer, so `"Y"`, `" y "` and `"y"` all work. Compare
against `"y"` and break out of the `while` loop otherwise.

</details>

### Tests to write

```python
# tests/test_guessing_game.py
import guessing_game


def test_random_range_is_respected(monkeypatch):
    """The secret must always be inside the requested range."""
    captured = []

    def fake_randint(low, high):
        captured.append((low, high))
        return 42

    monkeypatch.setattr(guessing_game.random, "randint", fake_randint)
    monkeypatch.setattr("builtins.input", lambda prompt="": "42")

    guesses = guessing_game.play_round(1, 100)

    assert captured == [(1, 100)]
    assert guesses == 1
```

The `monkeypatch` fixture (from [file 13](13-testing.md)) replaces `random.randint` so the test is
deterministic. Without it, the test would sometimes pass and sometimes fail — the worst kind of
test.

### Stretch goals

- Add a difficulty setting: easy is 1–10, medium 1–100, hard 1–1000.
- Track a high score across rounds in a module-level variable.
- Add a mode where the computer guesses your number (binary search).

### Done means

- The game never crashes, no matter what the player types.
- The guess count is correct.
- `python -m pytest` passes with at least two tests.

---

## Project 2 — Unit converter CLI

**Brief.** A command-line tool that converts between units: length, mass, temperature and volume.
Running it looks like this:

```text
python convert.py 10 km miles
python convert.py 32 celsius fahrenheit
python convert.py --help
```

**You will practise:** `argparse`, functions that return values, dictionaries as lookup tables,
`ValueError` and friendly error messages.

### Requirements

1. Accept a value, a source unit and a target unit as three positional arguments.
2. Support length (metre, kilometre, mile, foot, inch), mass (kilogram, gram, pound), volume
   (litre, millilitre, gallon) and temperature (celsius, fahrenheit, kelvin).
3. Print the converted value with sensible precision.
4. Print a helpful error and exit with a non-zero status for an unknown unit.
5. Support `--list` to print every supported unit and its factor.
6. Support `--precision N` to control how many decimal places are printed.

### Starter

```python
# convert.py
import argparse
import sys

# Every unit except temperature is a simple multiplication.
# The value is "how many of this unit in one base unit".
LENGTH = {"metre": 1.0, "kilometre": 1000.0, "mile": 1609.344, "foot": 0.3048, "inch": 0.0254}
MASS = {"kilogram": 1.0, "gram": 0.001, "pound": 0.45359237}
VOLUME = {"litre": 1.0, "millilitre": 0.001, "gallon": 3.78541}

CATEGORIES = {"length": LENGTH, "mass": MASS, "volume": VOLUME}


def find_unit(name: str) -> tuple[str, float]:
    """Return (category, factor) for a unit name, or raise ValueError."""
    for category, units in CATEGORIES.items():
        if name in units:
            return category, units[name]
    raise ValueError(f"unknown unit: {name}")


def convert_temperature(value: float, source: str, target: str) -> float:
    """Temperature needs an offset, not just a multiplier."""
    # Convert to Celsius first, then to the target unit.
    if source == "celsius":
        celsius = value
    elif source == "fahrenheit":
        celsius = (value - 32) * 5 / 9
    elif source == "kelvin":
        celsius = value - 273.15
    else:
        raise ValueError(f"unknown unit: {source}")

    if target == "celsius":
        return celsius
    if target == "fahrenheit":
        return celsius * 9 / 5 + 32
    if target == "kelvin":
        return celsius + 273.15
    raise ValueError(f"unknown unit: {target}")


def convert(value: float, source: str, target: str) -> float:
    """Convert a value from one unit to another."""
    if source in {"celsius", "fahrenheit", "kelvin"} or target in {"celsius", "fahrenheit", "kelvin"}:
        if source in {"celsius", "fahrenheit", "kelvin"} and target in {"celsius", "fahrenheit", "kelvin"}:
            return convert_temperature(value, source, target)
        raise ValueError("cannot convert between temperature and a non-temperature unit")

    source_category, source_factor = find_unit(source)
    target_category, target_factor = find_unit(target)
    if source_category != target_category:
        raise ValueError(f"cannot convert {source_category} to {target_category}")

    return value * source_factor / target_factor


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert between units.")
    parser.add_argument("value", type=float, nargs="?", help="the number to convert")
    parser.add_argument("source", nargs="?", help="the unit you are converting from")
    parser.add_argument("target", nargs="?", help="the unit you are converting to")
    parser.add_argument("--precision", type=int, default=4, help="decimal places to print")
    parser.add_argument("--list", action="store_true", help="list every supported unit")
    args = parser.parse_args()

    if args.list:
        for category, units in CATEGORIES.items():
            print(f"{category}: {', '.join(sorted(units))}")
        print("temperature: celsius, fahrenheit, kelvin")
        return 0

    if args.value is None or args.source is None or args.target is None:
        parser.print_help()
        return 1

    try:
        result = convert(args.value, args.source, args.target)
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    print(f"{args.value} {args.source} = {result:.{args.precision}f} {args.target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

Try it:

```bash
python convert.py 10 km miles
python convert.py 32 celsius fahrenheit
python convert.py 1 kilogram pound
python convert.py --list
python convert.py 5 kg miles
```

### Hints

<details>
<summary>Hint for requirement 4</summary>

Print the error to `sys.stderr` with `file=sys.stderr` and return `1` from `main()`. Then use
`sys.exit(main())` at the bottom so the process actually exits with that status code. A tool that
prints an error but exits with status 0 will break every script that calls it.

</details>

<details>
<summary>Hint for requirement 2</summary>

The `CATEGORIES` dictionary in the starter already holds three of the four categories. The
`find_unit` helper searches all of them. Temperature is special because it has an offset, so it
needs its own function — which the starter already provides.

</details>

### Tests to write

```python
# tests/test_convert.py
import pytest

from convert import convert, convert_temperature


def test_length_conversion():
    assert convert(1, "kilometre", "metre") == pytest.approx(1000.0)


def test_mile_to_foot():
    assert convert(1, "mile", "foot") == pytest.approx(5280.0)


def test_temperature_round_trip():
    assert convert_temperature(0, "celsius", "fahrenheit") == pytest.approx(32.0)
    assert convert_temperature(32, "fahrenheit", "celsius") == pytest.approx(0.0)


def test_unknown_unit_raises():
    with pytest.raises(ValueError):
        convert(1, "parsec", "metre")


def test_mismatched_categories_raise():
    with pytest.raises(ValueError):
        convert(1, "kilogram", "metre")
```

`pytest.approx` is how you compare floats. Never use `==` on floating point numbers — it will fail
for reasons that have nothing to do with your logic.

### Stretch goals

- Add a `--from-file` mode that reads a value from standard input.
- Support compound conversions like `10 kg pounds ounces`.
- Add a `table` subcommand that prints a full conversion table.

### Done means

- `--help` works and reads clearly.
- Unknown units and mismatched categories produce a helpful message and exit code 1.
- At least five tests pass.

---

## Project 3 — Expense tracker

**Brief.** A command-line tool to record and review personal expenses. Data is stored in a JSON file
so it survives between runs.

```text
python expenses.py add 12.50 coffee --category food
python expenses.py list
python expenses.py summary
```

**You will practise:** `dataclasses`, JSON file I/O, `argparse` subcommands, exception handling,
and the discipline of separating "compute" from "input/output".

### Requirements

1. `add AMOUNT DESCRIPTION --category CATEGORY` records an expense with a timestamp.
2. `list` prints every expense, newest first, one per line.
3. `summary` prints the total, the total per category, and the number of expenses.
4. `summary --category food` filters to one category.
5. The data file is created automatically if it does not exist.
6. A corrupt or empty data file produces a clear error, not a stack trace.
7. Amounts are stored as exact decimals, not floats.

### Starter

```python
# expenses.py
import argparse
import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from decimal import Decimal
from pathlib import Path

DATA_FILE = Path("expenses.json")


@dataclass
class Expense:
    amount: str          # stored as a string so Decimal is exact
    description: str
    category: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    @property
    def amount_decimal(self) -> Decimal:
        return Decimal(self.amount)


def load_expenses(path: Path) -> list[Expense]:
    """Read the data file. Returns an empty list if the file does not exist."""
    if not path.exists():
        return []

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"{path} is not valid JSON ({error}). Fix or delete it.") from error

    if not isinstance(raw, list):
        raise ValueError(f"{path} should contain a list of expenses.")

    return [Expense(**item) for item in raw]


def save_expenses(path: Path, expenses: list[Expense]) -> None:
    """Write all expenses back to disk."""
    path.write_text(
        json.dumps([asdict(expense) for expense in expenses], indent=2),
        encoding="utf-8",
    )


def add_expense(path: Path, amount: str, description: str, category: str) -> Expense:
    expenses = load_expenses(path)
    expense = Expense(amount=amount, description=description, category=category)
    expenses.append(expense)
    save_expenses(path, expenses)
    return expense


def summarise(expenses: list[Expense], category: str | None = None) -> dict:
    """Totals overall and per category."""
    selected = [e for e in expenses if category is None or e.category == category]
    total = sum((e.amount_decimal for e in selected), Decimal("0"))
    by_category: dict[str, Decimal] = {}
    for expense in selected:
        by_category[expense.category] = by_category.get(expense.category, Decimal("0")) + expense.amount_decimal
    return {
        "count": len(selected),
        "total": total,
        "by_category": by_category,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Track your expenses.")
    sub = parser.add_subparsers(dest="command", required=True)

    add_cmd = sub.add_parser("add", help="record an expense")
    add_cmd.add_argument("amount", help="the amount, e.g. 12.50")
    add_cmd.add_argument("description", help="what it was for")
    add_cmd.add_argument("--category", default="uncategorised")

    list_cmd = sub.add_parser("list", help="list all expenses")
    list_cmd.add_argument("--category", default=None)

    summary_cmd = sub.add_parser("summary", help="show totals")
    summary_cmd.add_argument("--category", default=None)

    args = parser.parse_args()

    try:
        if args.command == "add":
            try:
                Decimal(args.amount)
            except Exception:
                print(f"error: '{args.amount}' is not a valid amount", file=sys.stderr)
                return 1
            expense = add_expense(DATA_FILE, args.amount, args.description, args.category)
            print(f"Recorded {expense.amount} for {expense.description} ({expense.category})")
            return 0

        expenses = load_expenses(DATA_FILE)

        if args.command == "list":
            for expense in sorted(expenses, key=lambda e: e.created_at, reverse=True):
                if args.category and expense.category != args.category:
                    continue
                print(f"{expense.created_at}  {expense.amount:>10}  {expense.category:<14} {expense.description}")
            return 0

        if args.command == "summary":
            report = summarise(expenses, args.category)
            print(f"Total: {report['total']}  ({report['count']} expenses)")
            for name, amount in sorted(report["by_category"].items()):
                print(f"  {name:<16} {amount}")
            return 0
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
```

### Hints

<details>
<summary>Hint for requirement 7</summary>

Floats cannot represent `0.1` exactly, so `0.1 + 0.2` is not exactly `0.3` — you saw this in
[file 03](03-data-types-and-operators.md). For money, use `decimal.Decimal`. The starter stores the
amount as a **string** in the dataclass and converts it to `Decimal` when you need to do maths, so
nothing is lost on the way to and from JSON (JSON has no decimal type, only float).

</details>

<details>
<summary>Hint for requirement 2</summary>

`created_at` is an ISO 8601 string, and ISO 8601 sorts correctly as a plain string. That is why
`datetime.now().isoformat()` is such a common choice — no parsing needed to sort.

</details>

### Tests to write

```python
# tests/test_expenses.py
import pytest

from expenses import Expense, add_expense, load_expenses, summarise


def test_add_and_load_round_trip(tmp_path):
    data_file = tmp_path / "expenses.json"
    add_expense(data_file, "12.50", "coffee", "food")
    add_expense(data_file, "3.00", "bus", "transport")

    expenses = load_expenses(data_file)
    assert len(expenses) == 2
    assert expenses[0].description == "coffee"


def test_missing_file_returns_empty_list(tmp_path):
    assert load_expenses(tmp_path / "nothing.json") == []


def test_corrupt_file_raises_clear_error(tmp_path):
    data_file = tmp_path / "expenses.json"
    data_file.write_text("{not json at all", encoding="utf-8")
    with pytest.raises(ValueError, match="not valid JSON"):
        load_expenses(data_file)


def test_summary_totals_by_category():
    expenses = [
        Expense(amount="10.00", description="a", category="food"),
        Expense(amount="5.50", description="b", category="food"),
        Expense(amount="20.00", description="c", category="transport"),
    ]
    report = summarise(expenses)
    assert report["count"] == 3
    assert str(report["total"]) == "35.50"
    assert str(report["by_category"]["food"]) == "15.50"


def test_summary_filters_by_category():
    expenses = [
        Expense(amount="10.00", description="a", category="food"),
        Expense(amount="20.00", description="c", category="transport"),
    ]
    report = summarise(expenses, category="transport")
    assert report["count"] == 1
```

`tmp_path` gives every test its own temporary directory, so the tests never touch your real
`expenses.json` and never interfere with each other. This is the single most useful pytest fixture.

### Stretch goals

- Add a `remove` command that deletes an expense by index.
- Add a `monthly` command that groups by month.
- Export to CSV.
- Write the summary to a JSON file for a dashboard to read.

### Done means

- Data survives between runs.
- A corrupt `expenses.json` produces one clear line of error, not a stack trace.
- Totals are exact — `0.10 + 0.20` is `0.30`.
- At least five tests pass.

---

## Project 4 — CSV log analyser

**Brief.** You have a CSV file of web server access logs. Write a tool that summarises it: how many
requests, the most common status codes, the busiest paths, error rates, and requests per hour.

**You will practise:** the `csv` module, `collections.Counter`, `pathlib`, generators, and
`statistics`.

### Requirements

1. Read a CSV file with columns `timestamp`, `method`, `path`, `status`, `bytes`.
2. Report the total number of requests and the number of unique paths.
3. Report the top 5 paths by request count.
4. Report the count of each status code, and the error rate (`4xx + 5xx` over total).
5. Report the busiest hour of the day.
6. Report mean and median response size in bytes.
7. Skip malformed rows instead of crashing.

### Starter

```python
# log_analyser.py
import csv
import statistics
from collections import Counter
from pathlib import Path


def read_log_rows(path: Path):
    """Yield one dict per row, skipping anything malformed."""
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not row.get("status"):
                continue
            try:
                row["status"] = int(row["status"])
                row["bytes"] = int(row["bytes"]) if row.get("bytes") else 0
            except (TypeError, ValueError):
                continue
            yield row


def analyse(path: Path) -> dict:
    rows = list(read_log_rows(path))
    if not rows:
        return {"total": 0}

    statuses = Counter(row["status"] for row in rows)
    paths = Counter(row["path"] for row in rows)
    hours = Counter(row["timestamp"][11:13] for row in rows)
    sizes = [row["bytes"] for row in rows if row["bytes"] > 0]
    errors = sum(count for code, count in statuses.items() if code >= 400)

    return {
        "total": len(rows),
        "unique_paths": len(paths),
        "top_paths": paths.most_common(5),
        "statuses": statuses.most_common(),
        "error_rate": errors / len(rows),
        "busiest_hour": hours.most_common(1)[0][0] if hours else None,
        "mean_bytes": statistics.mean(sizes) if sizes else 0,
        "median_bytes": statistics.median(sizes) if sizes else 0,
    }


if __name__ == "__main__":
    import sys

    result = analyse(Path(sys.argv[1] if len(sys.argv) > 1 else "access.log.csv"))
    for key, value in result.items():
        print(f"{key:>14}: {value}")
```

Create a sample file to test against:

```python
# make_sample_log.py
import csv
import random
from datetime import datetime, timedelta

random.seed(7)  # same data every run, so your output is stable

paths = ["/", "/products", "/login", "/api/search", "/api/users", "/static/app.js"]
start = datetime(2024, 3, 1, 8, 0, 0)

with open("access.log.csv", "w", encoding="utf-8", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=["timestamp", "method", "path", "status", "bytes"])
    writer.writeheader()
    for _ in range(500):
        row = {
            "timestamp": (start + timedelta(seconds=random.randint(0, 40000))).isoformat(),
            "method": random.choice(["GET", "GET", "GET", "POST"]),
            "path": random.choice(paths),
            "status": random.choices([200, 301, 404, 500], weights=[80, 8, 9, 3])[0],
            "bytes": random.randint(120, 90000),
        }
        writer.writerow(row)

print("wrote access.log.csv")
```

### Hints

<details>
<summary>Hint for requirement 6</summary>

`statistics.mean` and `statistics.median` do the maths for you. The median is often more useful
than the mean for response sizes, because a handful of very large files drag the mean up. Drop
zero-byte responses first — they are usually redirects, not real content.

</details>

<details>
<summary>Hint for requirement 7</summary>

`csv.DictReader` gives you a dict per row. If a row has the wrong number of columns, the extra
value lands under the key `None` (or `restkey`). Guard the conversion with `try` / `except
(ValueError, TypeError)` and `continue` to skip the bad row. Malformed data is normal; a tool that
dies on one bad row is not production-ready.

</details>

### Tests to write

```python
# tests/test_log_analyser.py
import csv

import pytest

from log_analyser import analyse, read_log_rows


def write_sample(path, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["timestamp", "method", "path", "status", "bytes"])
        writer.writeheader()
        writer.writerows(rows)
    return path


def test_counts_requests(tmp_path):
    sample = write_sample(tmp_path / "log.csv", [
        {"timestamp": "2024-03-01T08:00:00", "method": "GET", "path": "/", "status": "200", "bytes": "100"},
        {"timestamp": "2024-03-01T08:01:00", "method": "GET", "path": "/", "status": "404", "bytes": "10"},
    ])
    result = analyse(sample)
    assert result["total"] == 2
    assert result["unique_paths"] == 1


def test_error_rate(tmp_path):
    sample = write_sample(tmp_path / "log.csv", [
        {"timestamp": "2024-03-01T08:00:00", "method": "GET", "path": "/", "status": "200", "bytes": "100"},
        {"timestamp": "2024-03-01T08:01:00", "method": "GET", "path": "/", "status": "500", "bytes": "10"},
        {"timestamp": "2024-03-01T08:02:00", "method": "GET", "path": "/", "status": "200", "bytes": "10"},
        {"timestamp": "2024-03-01T08:03:00", "method": "GET", "path": "/", "status": "200", "bytes": "10"},
    ])
    assert analyse(sample)["error_rate"] == pytest.approx(0.25)


def test_malformed_rows_are_skipped(tmp_path):
    sample = write_sample(tmp_path / "log.csv", [
        {"timestamp": "2024-03-01T08:00:00", "method": "GET", "path": "/", "status": "200", "bytes": "100"},
        {"timestamp": "2024-03-01T08:01:00", "method": "GET", "path": "/", "status": "oops", "bytes": "10"},
    ])
    assert analyse(sample)["total"] == 1
```

### Stretch goals

- Stream the file instead of building a list, and keep only counters.
- Break the analysis down by path: which path has the worst error rate?
- Parse a real Apache/Nginx combined log line with `re` and feed it into the same pipeline.
- Add a `--by-hour` chart using `matplotlib` (you will meet it in Step 3).

### Done means

- The tool never crashes on a malformed row.
- The error rate is a float between 0 and 1.
- At least three tests pass.

---

## Project 5 — Password generator and strength checker

**Brief.** Two tools in one program: a generator that produces strong random passwords, and a
checker that rates the strength of a password you give it.

**You will practise:** `secrets` (not `random`), string manipulation, `math.log2` for entropy, and
`argparse`.

### Requirements

1. Generate a password of a requested length using uppercase, lowercase, digits and symbols.
2. Guarantee at least one character from each selected category.
3. Use `secrets`, never `random` — explain in a comment why.
4. Check a password's strength using an entropy estimate, and also reject passwords that appear on
   a small list of common passwords.
5. Report the number of possible combinations and the equivalent entropy in bits.
6. Support `--generate N` and `--check PASSWORD` modes.

### Starter

```python
# passwords.py
import argparse
import math
import secrets
import string
import sys

LOWER = string.ascii_lowercase
UPPER = string.ascii_uppercase
DIGITS = string.digits
SYMBOLS = "!@#$%^&*()-_=+[]{};:,.<>?"

CATEGORIES = {"lower": LOWER, "upper": UPPER, "digits": DIGITS, "symbols": SYMBOLS}

COMMON_PASSWORDS = {
    "password", "123456", "12345678", "qwerty", "abc123", "letmein",
    "monkey", "dragon", "111111", "iloveyou", "admin", "welcome",
}


def generate_password(length: int = 20, categories: list[str] | None = None) -> str:
    """Generate a random password, guaranteeing one char from each category."""
    if length < len(categories or CATEGORIES):
        raise ValueError("length is too short for the requested categories")

    pools = [CATEGORIES[name] for name in (categories or CATEGORIES)]
    chars = [secrets.choice(pool) for pool in pools]          # one from each category

    combined = "".join(pools)
    chars += [secrets.choice(combined) for _ in range(length - len(chars))]

    secrets.SystemRandom().shuffle(chars)                     # shuffle securely
    return "".join(chars)


def estimate_entropy(password: str) -> float:
    """Bits of entropy, assuming the password was chosen uniformly at random."""
    if not password:
        return 0.0
    alphabet = 0
    if any(c.islower() for c in password):
        alphabet += 26
    if any(c.isupper() for c in password):
        alphabet += 26
    if any(c.isdigit() for c in password):
        alphabet += 10
    if any(c in SYMBOLS for c in password):
        alphabet += len(SYMBOLS)
    return len(password) * math.log2(alphabet) if alphabet else 0.0


def check_password(password: str) -> dict:
    """Assess a password and return a report."""
    if password.lower() in COMMON_PASSWORDS:
        return {"verdict": "terrible", "reason": "this is one of the most common passwords",
                "entropy": 0.0, "combinations": 0}

    entropy = estimate_entropy(password)
    if entropy < 40:
        verdict, reason = "weak", "too short or too predictable"
    elif entropy < 60:
        verdict, reason = "reasonable", "fine for low-stakes accounts"
    elif entropy < 80:
        verdict, reason = "strong", "good for most accounts"
    else:
        verdict, reason = "excellent", "use this for your important accounts"

    combinations = int(2 ** entropy) if entropy < 1024 else 2 ** 1024
    return {"verdict": verdict, "reason": reason, "entropy": entropy, "combinations": combinations}


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate and check passwords.")
    parser.add_argument("--generate", type=int, metavar="LENGTH", help="generate a password")
    parser.add_argument("--check", metavar="PASSWORD", help="check a password")
    parser.add_argument("--no-symbols", action="store_true", help="exclude symbols")
    args = parser.parse_args()

    if args.generate:
        categories = [name for name in CATEGORIES if not (name == "symbols" and args.no_symbols)]
        print(generate_password(args.generate, categories))
        return 0

    if args.check:
        report = check_password(args.check)
        print(f"verdict   : {report['verdict']}")
        print(f"reason    : {report['reason']}")
        print(f"entropy   : {report['entropy']:.1f} bits")
        print(f"combinations: ~{report['combinations']:,}")
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
```

### Hints

<details>
<summary>Hint for requirement 3</summary>

`random` is a **pseudo**-random generator: it is fast and reproducible, which is what you want for
simulations and tests, and exactly what you do not want for secrets. Its output is predictable from
a small seed. `secrets` uses the operating system's cryptographically secure source. The one place
`random` is correct is in your *tests* — where you want determinism.

</details>

<details>
<summary>Hint for requirement 5</summary>

Entropy is `length * log2(alphabet_size)`. A 20-character password from a 94-character alphabet has
`20 * log2(94)` ≈ 130 bits. To know the alphabet size, check which character classes actually
appear in the password. The `combinations` count is `2 ** entropy`.

</details>

<details>
<summary>Hint for requirement 2</summary>

Pick one character from each category first, then fill the remaining slots from the combined
alphabet, then shuffle. Shuffling matters: if the first character is always lowercase, an attacker
knows one character for free.

</details>

### Tests to write

```python
# tests/test_passwords.py
import pytest

from passwords import check_password, estimate_entropy, generate_password


def test_generated_password_has_requested_length():
    assert len(generate_password(24)) == 24


def test_generated_password_contains_every_category():
    password = generate_password(20)
    assert any(c.islower() for c in password)
    assert any(c.isupper() for c in password)
    assert any(c.isdigit() for c in password)
    assert any(not c.isalnum() for c in password)


def test_short_length_is_rejected():
    with pytest.raises(ValueError):
        generate_password(2)


def test_common_password_is_rejected():
    assert check_password("password")["verdict"] == "terrible"


def test_entropy_of_long_password_is_high():
    assert estimate_entropy("aB3$xY9!qT2@mN5#kL8&") > 100
```

Note the last test does not check *which* characters are generated — it checks properties. Testing
a random generator by checking an exact output would fail half the time.

### Stretch goals

- Read a list of leaked passwords from a file instead of hard-coding it.
- Add a passphrase mode: generate 4 random words from a word list.
- Add a `--diceware` mode using the EFF large wordlist idea.
- Add a `strength` check that also penalises repeated characters and sequences (`aaaa`, `1234`).

### Done means

- The generator never produces a password missing a category.
- The checker rejects `password123` as terrible.
- At least five tests pass.

---

## Project 6 — Markdown link checker

**Brief.** Scan a folder of Markdown files, find every link, and report the ones that are broken.
Local links (to other `.md` files or to files in the folder) are checked on disk. External links
are checked over HTTP, concurrently, so 50 links do not take 50 seconds.

**You will practise:** regex, `pathlib`, generators, `httpx` with `asyncio`, error handling, and
structured output.

### Requirements

1. Find Markdown links of the form `[text](url)` in a file.
2. Ignore links inside fenced code blocks.
3. Skip URL fragments (`#section`) but verify that the target file exists for local links.
4. Check external links with a HEAD request, falling back to GET.
5. Check external links concurrently, with a timeout and a bounded number of parallel requests.
6. Print a report: total links, broken local links, broken external links.
7. Exit with status 1 if anything is broken, so it can be used in CI.

### Starter

```python
# link_checker.py
import asyncio
import re
import sys
from pathlib import Path

import httpx

LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
FENCE_RE = re.compile(r"^```", re.MULTILINE)


def strip_code_blocks(text: str) -> str:
    """Remove fenced code blocks so we do not scan examples of links."""
    parts = FENCE_RE.split(text)
    # parts alternates: outside, inside, outside, inside ...
    return "".join(part for index, part in enumerate(parts) if index % 2 == 0)


def find_links(path: Path) -> list[tuple[str, str]]:
    """Return (text, url) for every markdown link in a file."""
    text = path.read_text(encoding="utf-8")
    return LINK_RE.findall(strip_code_blocks(text))


def is_external(url: str) -> bool:
    return url.startswith(("http://", "https://"))


async def check_external(client: httpx.AsyncClient, url: str) -> tuple[str, int | None]:
    """Return (url, status code or None if it failed)."""
    try:
        response = await client.head(url, follow_redirects=True)
        if response.status_code in (403, 405, 501):    # some servers refuse HEAD
            response = await client.get(url, follow_redirects=True)
        return url, response.status_code
    except httpx.HTTPError:
        return url, None


async def check_all_external(urls: list[str], limit: int = 20) -> list[tuple[str, int | None]]:
    """Check many URLs at once, with a hard cap on parallelism."""
    semaphore = asyncio.Semaphore(limit)

    async def guarded(client, url):
        async with semaphore:
            return await check_external(client, url)

    async with httpx.AsyncClient(timeout=10.0) as client:
        tasks = [guarded(client, url) for url in urls]
        return await asyncio.gather(*tasks)


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    markdown_files = sorted(root.rglob("*.md"))

    local_problems: list[str] = []
    external_urls: list[str] = []

    for path in markdown_files:
        for text, url in find_links(path):
            if is_external(url):
                external_urls.append(url)
            elif url.startswith("#"):
                continue                                # a fragment in the same file
            else:
                target = (path.parent / url.split("#")[0]).resolve()
                if not target.exists():
                    local_problems.append(f"{path}: [{text}]({url}) -> missing file {target}")

    print(f"scanned {len(markdown_files)} file(s)")
    print(f"external links found: {len(external_urls)}")

    for problem in local_problems:
        print(f"BROKEN LOCAL: {problem}")

    if external_urls:
        unique = sorted(set(external_urls))
        print(f"checking {len(unique)} unique external link(s)...")
        results = asyncio.run(check_all_external(unique))
        broken = [(url, status) for url, status in results if status is None or status >= 400]
        for url, status in broken:
            print(f"BROKEN EXTERNAL: {url} -> {status if status else 'no response'}")
    else:
        broken = []

    if local_problems or broken:
        print(f"\nFAILED: {len(local_problems)} local, {len(broken)} external")
        return 1

    print("\nAll links OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

### Hints

<details>
<summary>Hint for requirement 2</summary>

`FENCE_RE.split(text)` on a document with two fenced blocks produces five pieces: text, fence, text,
fence, text. The pieces at even indices are outside the code blocks, so joining those removes the
code. Watch out for fences with more than three backticks — this simple version handles the common
case, and you can improve it later.

</details>

<details>
<summary>Hint for requirement 5</summary>

`asyncio.Semaphore(limit)` is a counter that allows at most `limit` tasks inside the `async with`
block at once. Without it, 500 links means 500 simultaneous connections, which will get you
rate-limited or banned.

</details>

<details>
<summary>Hint for requirement 3</summary>

`url.split("#")[0]` removes the fragment. Then resolve relative to the **file's** directory, not the
current working directory: `(path.parent / url).resolve()`. Getting this wrong is why link
checkers only work when run from one specific folder.

</details>

### Tests to write

```python
# tests/test_link_checker.py
from link_checker import check_all_external, find_links, is_external, strip_code_blocks


def test_find_links_ignores_code_blocks(tmp_path):
    sample = tmp_path / "doc.md"
    sample.write_text(
        "Real [link](https://example.com) here.\n"
        "```\n"
        "Fake [example](https://not-real.example)\n"
        "```\n",
        encoding="utf-8",
    )
    links = find_links(sample)
    assert [url for _, url in links] == ["https://example.com"]


def test_is_external():
    assert is_external("https://example.com")
    assert is_external("http://example.com")
    assert not is_external("./other.md")
    assert not is_external("#anchor")


def test_local_link_to_missing_file_is_detected(tmp_path):
    sample = tmp_path / "doc.md"
    sample.write_text("[missing](nope.md)", encoding="utf-8")
    _, url = find_links(sample)[0]
    target = (sample.parent / url).resolve()
    assert not target.exists()
```

### Stretch goals

- Cache results so re-running does not re-check known-good links.
- Support `--ignore` patterns for domains you do not control.
- Check that anchor fragments actually exist in the target file.
- Run it in GitHub Actions on every pull request (you will learn this in Step 2).

### Done means

- Code examples containing links are not flagged.
- External links are checked concurrently, not one at a time.
- The exit code is 1 when something is broken.
- At least three tests pass.

---

## Project 7 — Task tracker with OOP

**Brief.** A small but properly structured application. A `Task` is a dataclass. A `TaskList` is a
class that owns the collection, handles persistence, and knows how to add, complete, sort and
filter. A thin CLI sits on top. It has a proper `pytest` suite.

**You will practise:** dataclasses, enums, class design, JSON persistence, type hints, `pytest`,
and separation of concerns.

### Requirements

1. A `Task` has an id, a title, a priority (enum), a done flag, and a creation timestamp.
2. A `TaskList` can add, complete (by id), remove, and list tasks.
3. Tasks can be filtered by priority and by done/not-done.
4. Tasks are sorted by priority, then by creation time.
5. `TaskList` saves to and loads from a JSON file, and handles a corrupt file gracefully.
6. The CLI has subcommands: `add`, `list`, `done`, `remove`.
7. Every non-trivial method has at least one test.

### Starter

```python
# tasks.py
import argparse
import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path


class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

    @classmethod
    def parse(cls, text: str) -> "Priority":
        try:
            return cls[text.upper()]
        except KeyError:
            raise ValueError(f"unknown priority: {text}") from None


@dataclass
class Task:
    title: str
    priority: Priority = Priority.MEDIUM
    done: bool = False
    id: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    def to_dict(self) -> dict:
        data = asdict(self)
        data["priority"] = self.priority.name
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        return cls(
            title=data["title"],
            priority=Priority.parse(data.get("priority", "MEDIUM")),
            done=bool(data.get("done", False)),
            id=int(data.get("id", 0)),
            created_at=data.get("created_at", ""),
        )


class TaskList:
    def __init__(self, path: Path | None = None):
        self.path = path
        self.tasks: list[Task] = []
        self._next_id = 1

    def add(self, title: str, priority: Priority = Priority.MEDIUM) -> Task:
        task = Task(title=title, priority=priority, id=self._next_id)
        self._next_id += 1
        self.tasks.append(task)
        self.save()
        return task

    def complete(self, task_id: int) -> bool:
        for task in self.tasks:
            if task.id == task_id:
                task.done = True
                self.save()
                return True
        return False

    def remove(self, task_id: int) -> bool:
        before = len(self.tasks)
        self.tasks = [task for task in self.tasks if task.id != task_id]
        changed = len(self.tasks) != before
        if changed:
            self.save()
        return changed

    def filter(self, priority: Priority | None = None, done: bool | None = None) -> list[Task]:
        result = self.tasks
        if priority is not None:
            result = [task for task in result if task.priority is priority]
        if done is not None:
            result = [task for task in result if task.done is done]
        return sorted(result, key=lambda task: (-task.priority.value, task.created_at))

    def save(self) -> None:
        if self.path is None:
            return
        self.path.write_text(
            json.dumps([task.to_dict() for task in self.tasks], indent=2),
            encoding="utf-8",
        )

    def load(self) -> None:
        if self.path is None or not self.path.exists():
            return
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return                      # a corrupt file means an empty list, not a crash
        self.tasks = [Task.from_dict(item) for item in raw]
        self._next_id = max((task.id for task in self.tasks), default=0) + 1


def main() -> int:
    parser = argparse.ArgumentParser(description="A small task tracker.")
    sub = parser.add_subparsers(dest="command", required=True)

    add_cmd = sub.add_parser("add")
    add_cmd.add_argument("title")
    add_cmd.add_argument("--priority", default="medium")

    list_cmd = sub.add_parser("list")
    list_cmd.add_argument("--priority", default=None)
    list_cmd.add_argument("--done", action="store_true", default=None)

    for name in ("done", "remove"):
        command = sub.add_parser(name)
        command.add_argument("id", type=int)

    args = parser.parse_args()
    tasks = TaskList(Path("tasks.json"))
    tasks.load()

    if args.command == "add":
        try:
            priority = Priority.parse(args.priority)
        except ValueError as error:
            print(f"error: {error}", file=sys.stderr)
            return 1
        task = tasks.add(args.title, priority)
        print(f"Added #{task.id}: {task.title}")
        return 0

    if args.command == "list":
        for task in tasks.filter(priority=Priority.parse(args.priority) if args.priority else None,
                                 done=args.done):
            mark = "x" if task.done else " "
            print(f"[{mark}] #{task.id} {task.title} ({task.priority.name})")
        return 0

    if args.command == "done":
        if tasks.complete(args.id):
            print(f"Completed #{args.id}")
            return 0
        print(f"No task with id {args.id}", file=sys.stderr)
        return 1

    if args.command == "remove":
        if tasks.remove(args.id):
            print(f"Removed #{args.id}")
            return 0
        print(f"No task with id {args.id}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
```

### Hints

<details>
<summary>Hint for requirement 1</summary>

`Priority` is an `Enum`, so it has a fixed, valid set of values — a typo becomes an error instead
of a silent string that breaks sorting later. `parse` turns user input into a member, and raises a
clear `ValueError` for anything else.

</details>

<details>
<summary>Hint for requirement 5</summary>

`Task.to_dict` and `Task.from_dict` are the JSON boundary. Note that `asdict()` on a dataclass with
an `Enum` field gives you the enum object, not a string, and `json.dumps` cannot serialise it — so
`to_dict` converts it to `.name` first. That is the whole reason those two methods exist.

</details>

<details>
<summary>Hint for requirement 7</summary>

Test the `TaskList` methods, not the CLI. Construct a `TaskList` with `path=None` (so it never
touches the disk), add tasks, and assert on the results. Then write one integration-style test that
uses `tmp_path` to check save/load.

</details>

### Tests to write

```python
# tests/test_tasks.py
import pytest

from tasks import Priority, Task, TaskList


@pytest.fixture
def task_list():
    return TaskList(path=None)


def test_add_assigns_incrementing_ids(task_list):
    first = task_list.add("write code")
    second = task_list.add("write tests")
    assert first.id == 1
    assert second.id == 2


def test_complete_marks_task_done(task_list):
    task = task_list.add("write code")
    assert task_list.complete(task.id) is True
    assert task_list.tasks[0].done is True


def test_complete_unknown_id_returns_false(task_list):
    assert task_list.complete(999) is False


def test_remove_unknown_id_returns_false(task_list):
    assert task_list.remove(999) is False


def test_filter_by_priority(task_list):
    task_list.add("low thing", Priority.LOW)
    task_list.add("high thing", Priority.HIGH)
    high = task_list.filter(priority=Priority.HIGH)
    assert len(high) == 1
    assert high[0].title == "high thing"


def test_sort_is_by_priority_then_time(task_list):
    task_list.add("a", Priority.LOW)
    task_list.add("b", Priority.HIGH)
    task_list.add("c", Priority.MEDIUM)
    assert [task.title for task in task_list.filter()] == ["b", "c", "a"]


def test_save_and_load_round_trip(tmp_path):
    path = tmp_path / "tasks.json"
    original = TaskList(path)
    original.add("write code", Priority.HIGH)

    restored = TaskList(path)
    restored.load()

    assert len(restored.tasks) == 1
    assert restored.tasks[0].title == "write code"
    assert restored.tasks[0].priority is Priority.HIGH


def test_load_corrupt_file_gives_empty_list(tmp_path):
    path = tmp_path / "tasks.json"
    path.write_text("{{{ not json", encoding="utf-8")
    tasks = TaskList(path)
    tasks.load()
    assert tasks.tasks == []


def test_priority_parse_rejects_unknown():
    with pytest.raises(ValueError):
        Priority.parse("urgent")
```

### Stretch goals

- Add due dates and a `due` command that lists overdue tasks.
- Add tags: a task can have several, stored as a list.
- Add `export` to write a Markdown checklist.
- Add a `TaskList.__len__` and `__iter__` so the class behaves like a sequence.

### Done means

- All seven requirements work.
- The test suite has at least nine tests and they all pass.
- The class has no global state and no direct `print` calls — it returns data and the CLI prints it.

---

## Project 8 — Notes search engine (mini RAG)

**Brief.** The final project. A search engine over your own Markdown notes. It reads a folder of
notes, splits them into chunks, builds a **TF-IDF** index, and answers a query by returning the
most relevant passages. This is the core of every retrieval-augmented generation system, with none
of the dependencies.

**You will practise:** everything. File I/O, generators, `math`, `collections`, a clean class
design, a CLI, and tests. It is also the bridge to Step 9 of this repository.

### Requirements

1. Read all `.md` files in a folder.
2. Split each file into overlapping chunks of about 300 characters, on word boundaries.
3. Build a **TF-IDF** index: for every word, how often it appears in a chunk (term frequency),
   multiplied by how rare that word is across all chunks (inverse document frequency).
4. Score a query against every chunk using cosine similarity.
5. Return the top 3 chunks with their scores, and print the source file and line number.
6. If the top score is below a threshold, say "no relevant notes found".
7. Build the index once and reuse it — do not rebuild it on every query.

### Starter

```python
# search.py
import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

TOKEN_RE = re.compile(r"[a-z0-9']+")
STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "of", "to", "in", "on", "and", "or",
    "for", "it", "this", "that", "with", "as", "at", "by", "be", "i", "you",
}


@dataclass
class Chunk:
    text: str
    source: str
    line: int


def tokenize(text: str) -> list[str]:
    return [word for word in TOKEN_RE.findall(text.lower()) if word not in STOP_WORDS]


def split_into_chunks(text: str, source: str, size: int = 300, overlap: int = 50) -> list[Chunk]:
    """Split text into overlapping chunks on word boundaries, tracking line numbers."""
    words = text.split()
    chunks: list[Chunk] = []
    step_chars = max(1, size - overlap)
    search_from = 0
    start = 0

    while start < len(words):
        # grow the window until we would exceed `size` characters
        end = start
        length = 0
        while end < len(words) and length + len(words[end]) + 1 <= size:
            length += len(words[end]) + 1
            end += 1
        if end == start:                 # a single word longer than `size`
            end = start + 1

        chunk_words = words[start:end]
        chunk_text = " ".join(chunk_words)

        # find where this chunk starts so we can report the line number
        position = text.find(chunk_text, search_from)
        if position >= 0:
            line = text.count("\n", 0, position) + 1
            search_from = position + 1
        else:
            line = 1

        chunks.append(Chunk(text=chunk_text, source=source, line=line))

        if end >= len(words):
            break

        # slide the window forward, keeping roughly `overlap` characters of overlap
        next_start = end
        moved = 0
        while next_start > start and moved < step_chars:
            next_start -= 1
            moved += len(words[next_start]) + 1
        start = max(next_start, start + 1)

    return chunks


class SearchIndex:
    """A TF-IDF index over a set of chunks."""

    def __init__(self, chunks: list[Chunk]):
        self.chunks = chunks
        self.vocabulary: list[str] = []
        self.idf: dict[str, float] = {}
        self.vectors: list[dict[str, float]] = []
        self._build()

    def _build(self) -> None:
        documents = [tokenize(chunk.text) for chunk in self.chunks]
        document_frequency = Counter()
        for tokens in documents:
            document_frequency.update(set(tokens))

        total = len(documents) or 1
        self.idf = {word: math.log(total / (1 + count)) + 1.0
                    for word, count in document_frequency.items()}
        self.vocabulary = sorted(self.idf)

        self.vectors = [self._vectorize(tokens) for tokens in documents]

    def _vectorize(self, tokens: list[str]) -> dict[str, float]:
        counts = Counter(tokens)
        total = sum(counts.values()) or 1
        return {word: (count / total) * self.idf.get(word, 0.0)
                for word, count in counts.items()}

    def search(self, query: str, top_k: int = 3, min_score: float = 0.0) -> list[tuple[float, Chunk]]:
        query_vector = self._vectorize(tokenize(query))
        if not query_vector:
            return []

        scored = []
        for vector, chunk in zip(self.vectors, self.chunks):
            score = self._cosine(query_vector, vector)
            if score >= min_score:
                scored.append((score, chunk))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return scored[:top_k]

    @staticmethod
    def _cosine(a: dict[str, float], b: dict[str, float]) -> float:
        shared = set(a) & set(b)
        if not shared:
            return 0.0
        dot = sum(a[word] * b[word] for word in shared)
        norm_a = math.sqrt(sum(value * value for value in a.values()))
        norm_b = math.sqrt(sum(value * value for value in b.values()))
        return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0


def build_index(folder: Path, size: int = 300) -> SearchIndex:
    chunks: list[Chunk] = []
    for path in sorted(folder.rglob("*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        chunks.extend(split_into_chunks(text, str(path), size))
    return SearchIndex(chunks)


def main() -> int:
    import sys

    folder = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    query = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""

    if not query:
        print("usage: python search.py <folder> <query words>")
        return 1

    index = build_index(folder)
    results = index.search(query, top_k=3, min_score=0.05)

    if not results:
        print("No relevant notes found.")
        return 0

    for score, chunk in results:
        print(f"[{score:.3f}] {chunk.source}:{chunk.line}")
        print(f"        {chunk.text[:160]}...")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

### Hints

<details>
<summary>Hint for requirement 3</summary>

TF-IDF has two halves. **Term frequency**: how often the word appears in this chunk, divided by
the chunk length, so long chunks do not automatically win. **Inverse document frequency**:
`log(total_chunks / (1 + chunks_containing_the_word))`. A word in every chunk gets an IDF near
zero and stops mattering; a rare, meaningful word gets a high IDF and dominates. The `+ 1.0` keeps
the IDF positive.

</details>

<details>
<summary>Hint for requirement 5</summary>

Track the line number when you create each chunk. The starter's `split_into_chunks` computes it by
counting newlines before the chunk's position in the file. You will probably want to restructure
that to track the position as you walk, rather than searching for the text afterwards.

</details>

<details>
<summary>Hint for requirement 7</summary>

This is the whole point of the `SearchIndex` class: build it once, then query it many times. If you
rebuild the index inside `search()`, you are throwing away the expensive part. This is the same
separation you saw in the LLM client in
[file 17](17-python-for-ai-and-data.md).

</details>

### Tests to write

```python
# tests/test_search.py
from search import Chunk, SearchIndex, split_into_chunks, tokenize


def test_tokenize_removes_stop_words():
    assert tokenize("The cat and the hat") == ["cat", "hat"]


def test_split_produces_chunks():
    text = " ".join(f"word{i}" for i in range(200))
    chunks = split_into_chunks(text, "test.md", size=100)
    assert len(chunks) > 1
    assert all(len(chunk.text) <= 110 for chunk in chunks)


def test_search_finds_the_right_chunk():
    chunks = [
        Chunk(text="Python is a programming language used for data analysis.", source="a.md", line=1),
        Chunk(text="The capital of France is Paris and it is in Europe.", source="b.md", line=1),
    ]
    index = SearchIndex(chunks)
    results = index.search("programming language data")
    assert results
    assert results[0][1].source == "a.md"


def test_search_returns_nothing_for_unrelated_query():
    chunks = [Chunk(text="Python is a programming language.", source="a.md", line=1)]
    index = SearchIndex(chunks)
    assert index.search("zebra giraffe elephant", min_score=0.05) == []


def test_empty_index_is_safe():
    index = SearchIndex([])
    assert index.search("anything") == []
```

### Stretch goals

- Handle the case where the query contains a word that appears in no chunk.
- Add a `--json` output mode so the results can feed another program.
- Add stemming and stop-word configuration.
- Add a `--watch` mode that rebuilds the index when a file changes.
- **Then**: swap TF-IDF for real embeddings and watch the quality jump. That is Step 9.

### Done means

- Searching for a phrase returns the chunk that contains it, ranked first.
- An unrelated query returns "no relevant notes found".
- The index is built once and reused across queries.
- At least five tests pass.

---

## After the ladder

You have now written, tested and structured eight programs. Two things follow from that:

**You are ready for Step 2.** [DEVELOPER FOUNDATIONS](../DEVELOPER%20FOUNDATIONS/guide.md) — Git,
GitHub, Linux, FastAPI and system design. Everything you write from here on should be committed to
version control, and this is where you learn how.

**You are ready for real work.** Pick an open problem that interests you — a dataset, an API, a tool
you use — and build something small and complete with it. The projects in this repository all follow
the same shape: a `guide.md`, a clear order, runnable examples and real tests. Build yours the
same way.

---

## 🧪 Try it yourself

### Exercise 1 — track your own progress

Create a `PROGRESS.md` in this repository (or your own notes folder) and add a table with one row per
project: name, date started, date finished, and one sentence about what you found hardest. Write
it in the format you learned in
[file 09](09-file-io-and-errors.md) — Markdown tables, because they are readable everywhere.

<details>
<summary>Why this matters</summary>

Keeping a learning log is the single most underrated study technique. It forces you to notice what
you actually struggled with, and six months from now that list will tell you exactly what to
review. A Git repository full of small, well-described commits is also the best portfolio you can
build for an AI engineering job.

</details>

### Exercise 2 — build a seventh project of your own

Design a small tool you actually want: a habit tracker, a recipe search tool, a script that renames
your downloads, a Markdown table formatter. Build it with the same structure as Project 7 — a
dataclass for the data, a class for the logic, a CLI at the edge, and tests.

<details>
<summary>What to aim for</summary>

- 100 to 300 lines of real code.
- At least five tests.
- One dataclass, one class that owns the data, one CLI layer.
- No global variables, and no `print` inside your logic classes.
- A README that explains how to run it.

If you can do all five, you have internalised the structure of a small professional Python project.

</details>

### Exercise 3 — refactor one project for quality

Take Project 3 (the expense tracker) and improve it:

- Add type hints to every function.
- Run `mypy --strict` and fix what it finds.
- Run `ruff check` and `ruff format`.
- Extract the CLI into its own module so `expenses.py` can be imported without side effects.

<details>
<summary>What to notice</summary>

`mypy --strict` on code that "obviously works" usually finds 5 to 15 real issues — most often
functions that can return `None` without saying so, and dictionaries with mixed value types. This
is exactly the value of type hints: they turn a runtime crash into a build-time error.

</details>

---

## ✅ Checkpoint

1. Why is a `try` / `except ValueError` around `int(input(...))` better than letting the error
   crash the program?
   <details><summary>Answer</summary>Because the user is expected to make mistakes. A program that
   dies because someone typed a letter instead of a number is a program nobody wants to use.
   </details>

2. What is the difference between `argparse` positional arguments and optional arguments?
   <details><summary>Answer</summary>Positional arguments are identified by their position
   (`value`, `source`, `target`); optional ones start with `-` or `--` and are identified by name
   (`--precision`).
   </details>

3. Why store money amounts as strings or `Decimal` rather than floats?
   <details><summary>Answer</summary>Because binary floating point cannot represent values like
   `0.1` exactly, so repeated addition drifts. `Decimal` is exact for base-10 values.
   </details>

4. What does `tmp_path` do in a pytest test, and why is it better than a hard-coded path?
   <details><summary>Answer</summary>It gives the test its own unique temporary directory that is
   cleaned up afterwards. Tests never interfere with each other, and they never touch your real
   data.
   </details>

5. What is the difference between `random` and `secrets`?
   <details><summary>Answer</summary>`random` is fast and reproducible but predictable — fine for
   simulations and tests, wrong for security. `secrets` uses the operating system's cryptographic
   source and is the correct choice for passwords, tokens and keys.
   </details>

6. Why does a `TaskList` class save and load its own data rather than letting the CLI do it?
   <details><summary>Answer</summary>Separation of concerns. The class owns the data and its
   invariants; the CLI only translates between text and calls. That makes the class testable
   without running a command line, and the CLI testable without touching the disk.
   </details>

7. In Project 8, what does the IDF part of TF-IDF do?
   <details><summary>Answer</summary>It down-weights words that appear in many chunks and
   up-weights words that appear in few. Without it, common words dominate the score and rare,
   meaningful words are drowned out.
   </details>

8. Why is `asyncio.Semaphore` needed when checking many links?
   <details><summary>Answer</summary>Without it, every request starts at once. That will hit rate
   limits, use up your file descriptors, and can get you blocked by the target server.
   </details>

9. What does "the index is built once and reused" buy you?
   <details><summary>Answer</summary>Building a TF-IDF index means reading and tokenising every
   document. Doing that on every query is wasted work. This is the same pattern as keeping one LLM
   client around instead of constructing one per request.
   </details>

10. Name one thing this ladder taught you that no tutorial would.
    <details><summary>Answer</summary>There is no single right answer — but if you had to pick one,
    it is that "it works" and "it is finished" are very different claims. Every project here had a
    point where it ran, and then a further point where it was actually done: tested, error-handled
    and clean.
    </details>

---

## 🐛 Common mistakes

| Mistake | What you see | Fix |
|---|---|---|
| `int(input(...))` with no error handling | `ValueError` crash on bad input | Wrap in `try` / `except ValueError` and loop |
| Using `random` for anything security-related | Predictable passwords and tokens | Use `secrets` |
| Comparing floats with `==` | Tests fail for no clear reason | Use `pytest.approx` or `math.isclose` |
| Hard-coding file paths in tests | Tests fail when run in parallel, or clobber real data | Use `tmp_path` |
| Not checking `response.status_code` | A confusing `JSONDecodeError` on an error page | Check the status first, or call `raise_for_status()` |
| Building the index inside the search function | The tool is unusably slow | Build once, query many |
| Unbounded parallelism | Rate limits, blocked IPs, socket errors | Bound it with a semaphore |
| Writing logic and `print` in the same function | Untestable code, noisy output | Return data; let the CLI print it |
| Catching `except Exception` and ignoring it | A silent bug that shows up three days later | Catch the specific exception, or log it |
| Forgetting `if __name__ == "__main__":` | The whole module runs on import | Guard your entry point |
| Skipping the "Done means" checklist | A project that is 80% finished and feels finished | Finish the checklist before moving on |

---

## 🔗 Resources

- [Python Tutorial: Data Structures](https://docs.python.org/3/tutorial/datastructures.html) — the
  official guide to lists, tuples, dicts and sets, with the right level of detail for these
  projects.
- [argparse in the standard library](https://docs.python.org/3/library/argparse.html) — the full
  reference for building command-line tools, including subcommands and custom types.
- [csv in the standard library](https://docs.python.org/3/library/csv.html) — everything you need
  to read and write CSV correctly, including the `newline=""` rule.
- [json in the standard library](https://docs.python.org/3/library/json.html) — encoding, decoding
  and the `default=` hook for non-standard types.
- [pathlib in the standard library](https://docs.python.org/3/library/pathlib.html) — the modern
  way to work with paths.
- [secrets in the standard library](https://docs.python.org/3/library/secrets.html) — generating
  cryptographically secure tokens and passwords.
- [asyncio in the standard library](https://docs.python.org/3/library/asyncio.html) — tasks,
  `gather`, timeouts and structured concurrency.
- [pytest documentation](https://docs.pytest.org/en/stable/) — fixtures, parametrisation and the
  mocking tools, in one good reference.
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html) — the standard library's
  mocking, for when you need to fake an API.
- [The Hitchhiker's Guide: Project Structure](https://docs.python-guide.org/writing/structure/) —
  how to lay out a Python project so other people (and future you) can navigate it.
- [Exercism — Python track](https://exercism.org/tracks/python) — more exercises, with human
  feedback, when you want to keep going after these eight.
- [Codewars](https://codewars.com/) — short daily challenges for keeping your fingers warm.
- [Advent of Code](https://adventofcode.com/) — a December puzzle series that will make you think
  like a programmer.

---

## ➡️ Next

- [**Resources**](resources.md) — the full curated link list for this step.
- **Then:** [DEVELOPER FOUNDATIONS](../DEVELOPER%20FOUNDATIONS/guide.md) — Git, GitHub, Linux,
  FastAPI and system design. It is time to put your code under version control and start
  collaborating.

**← Previous:** [17 — Python for AI and data](17-python-for-ai-and-data.md)
