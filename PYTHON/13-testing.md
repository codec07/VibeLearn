# Testing

Writing code and being *sure* it works are two different jobs. You can read your program
twice and still not know whether it handles an empty list, a missing file or a typo in a
dictionary key. A **test** is a small piece of code that checks one behaviour of your
program and fails loudly when that behaviour breaks. This file is about writing those
tests: what to test, how to write them with `pytest`, how to fake the outside world so
your tests run in milliseconds, and how to write the test *before* the code so the code
has to earn its place.

> **⏱️ Time:** ~30 minutes
> **📚 Prereqs:** [12 — Environments and tooling](12-environments-and-tooling.md)
> **🎯 By the end you can:** Write a `pytest` suite for a Python project — including fixtures,
> parameterised tests, mocks of an external API, and a coverage report — and use
> test-driven development to drive your implementation.

---

## Why this matters for AI engineering

An LLM application has a lot of code that is not about the model: prompt templates, input
validation, retry logic, token counting, caching, streaming parsers, cost calculations. All
of it is easy to break and hard to check by hand, because the "correct" answer often
depends on a paid API call you do not want to make on every save.

Tests let you check that logic without calling the API at all. When a prompt template
changes, you can prove that the token counter, the truncation logic and the cost estimate
still behave — in a second, for free, on every commit. In an AI team, the test suite is
also the safety net under a system whose output is not deterministic: you cannot assert
"the model said exactly this", so you assert "the parser extracted these fields" and "the
retry logic gives up after three attempts".

---

## 1. Why tests exist

Four reasons, in order of how often they matter:

1. **They catch regressions.** You refactor a function at 5pm on Friday. A test that
   covered the old behaviour tells you at 5:01pm that you broke something. Without it,
   the customer tells you on Monday.
2. **They let you refactor safely.** "Refactoring" means changing *how* the code works
   while keeping *what* it does the same. Tests are the definition of "the same".
3. **They document behaviour.** A well-named test is executable documentation. New
   teammates read `test_discount_over_100_percent_raises` and immediately know that
   behaviour is intentional.
4. **They let a computer check your work ten thousand times.** You cannot manually re-run
   a CLI fifty times before each commit. A test can.

A test that is never run is worthless. A test that fails at random is worse than
worthless — it trains you to ignore red output, which is exactly the habit that lets real
bugs through. Tests must be **fast** and **deterministic**: same result every time, on
every machine.

---

## 2. The testing pyramid

Three kinds of test, arranged by how many you write and how much they cost:

```text
                 /\
                /  \        End-to-end (E2E) tests
               / E2E\       - a handful
              /______\      - slow: seconds to minutes
             /        \     - exercise the whole system
            /Integration\    - a few dozen
           /____________\   - medium: milliseconds to seconds
          /              \
         /   Unit tests   \  - hundreds
        /__________________\ - fast: milliseconds
                                - test one function in isolation
```

| Kind | What it does | Speed | How many |
|---|---|---|---|
| **Unit test** | Tests one function or class with fake inputs and outputs | milliseconds | hundreds |
| **Integration test** | Tests several real components together (your code + a real database or file) | seconds | dozens |
| **End-to-end test** | Tests the whole system the way a user does, through the real interface | minutes | a handful |

The pyramid is a guideline, not a law. The important rule is: **write the bulk of your
tests at the bottom.** A unit test is cheap to write, cheap to run and pinpoints the
exact broken line. An end-to-end test is expensive to write, expensive to run, and when it
fails you have no idea whether the bug is in parsing, in the API, or in the database.

---

## 3. `pytest` versus `unittest`

Python's standard library ships `unittest`, a framework that dates from 2001. `pytest` is
the third-party package the whole industry has standardised on since around 2015.

The same test in both:

```python
# unittest style
import unittest

from calculator import apply_discount


class TestApplyDiscount(unittest.TestCase):
    def test_ten_percent_discount(self):
        self.assertEqual(apply_discount(100.0, 10.0), 90.0)
```

```python
# pytest style
from calculator import apply_discount


def test_ten_percent_discount():
    assert apply_discount(100.0, 10.0) == 90.0
```

`pytest` wins for four reasons:

- **No boilerplate.** No class, no `self`, no `TestCase` import. A test is a function
  whose name starts with `test_`.
- **Better failure output.** When an assertion fails, `pytest` shows you the two values
  that differed, the line number, and the values of local variables in scope. `unittest`
  shows a stack trace.
- **Plain `assert`.** No need to remember which of the 15 `assertX` methods to use.
- **Plugins.** Hundreds of them: `pytest-cov` for coverage, `pytest-asyncio` for async
  tests, `pytest-mock`, `pytest-randomly`, `pytest-xdist` for running in parallel.

The one thing `unittest` still has going for it is that it is in the standard library, so
it is always available. But for new projects, `pytest` is the default choice.

---

## 4. Installing and running `pytest`

```bash
python -m pip install pytest
```

Or, if you followed [12 — Environments and tooling](12-environments-and-tooling.md):

```bash
uv add --dev pytest
```

Running it in a folder with a `tests/` directory:

```bash
python -m pytest
```

```text
============================= test session starts ==============================
collected 3 items

tests/test_calculator.py ..F                                      [ 66%]
tests/test_llm_client.py .                                         [100%]

=========================== short test summary info ============================
FAILED tests/test_calculator.py::test_apply_discount_rejects_bad_percent - ValueError: percent must be between 0 and 100
========================= 1 failed, 2 passed in 0.09s ==========================
```

The command line is where `pytest` really shines:

| Command | What it does |
|---|---|
| `pytest` | run every test it can find |
| `pytest -v` | one line per test, with the test name |
| `pytest -vv` | one line per test *plus* the captured output of each |
| `pytest tests/test_calculator.py` | run one file |
| `pytest tests/test_calculator.py::test_apply_discount` | run one test by name |
| `pytest -k "discount"` | run tests whose name contains "discount" |
| `pytest -x` | stop at the first failure (fast feedback on a broken repo) |
| `pytest -m "slow"` | run only tests marked `slow` |
| `pytest -m "not slow"` | run everything except the slow tests |
| `pytest --lf` | re-run only the tests that failed last time |
| `pytest --tb=short` | show a compact traceback instead of the full one |
| `pytest --tb=long` | show the full traceback with local variables |
| `pytest -x -q` | quiet: one character per test, stop at first failure |
| `pytest -p no:randomly` | disable the `pytest-randomly` plugin if you installed it |

`--lf` ("last failed") is the command you will use most while working. It remembers which
tests failed and runs only those, so your fix-test loop takes one second instead of ten.

Configure `pytest` in your `pyproject.toml` so everybody on the team gets the same
behaviour:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]            # only look inside tests/ when run with no arguments
python_files = ["test_*.py"]     # the default file naming pattern
addopts = "-ra --strict-markers"  # -ra prints a summary of skipped/xfailed tests
markers = [
    "slow: tests that take more than a second",
    "integration: tests that talk to a real external service",
]
```

---

## 5. Your first test

Here is the module we will test. Save it as `calculator.py`:

```python
# calculator.py
"""A tiny pricing module used by the tests in this file."""


def apply_discount(price: float, percent: float) -> float:
    """Return the price after a percentage discount, rounded to cents."""
    if not 0 <= percent <= 100:
        raise ValueError("percent must be between 0 and 100")
    return round(price * (1 - percent / 100), 2)


def shipping_cost(weight_kg: float, express: bool = False) -> float:
    """Return the shipping cost in dollars for a parcel of the given weight."""
    base = 4.99
    per_kg = 1.50
    cost = base + weight_kg * per_kg
    return round(cost * 1.75, 2) if express else round(cost, 2)


if __name__ == "__main__":
    print(apply_discount(100.0, 10.0))
    print(shipping_cost(2.0))
```

```text
90.0
7.99
```

And here is the test. Save it as `tests/test_calculator.py`:

```python
# tests/test_calculator.py
"""Tests for the calculator module."""

from calculator import apply_discount, shipping_cost


def test_apply_discount_ten_percent():
    assert apply_discount(100.0, 10.0) == 90.0


def test_apply_discount_no_discount():
    assert apply_discount(50.0, 0.0) == 50.0


def test_shipping_cost_regular():
    assert shipping_cost(2.0) == 7.99


def test_shipping_cost_express():
    assert shipping_cost(2.0, express=True) == 13.98
```

```text
============================= test session starts ==============================
collected 4 items

tests/test_calculator.py ....                                       [100%]

============================== 4 passed in 0.05s ==============================
```

Three rules for naming:

- The **file** must be called `test_*.py` (or `*_test.py`) so `pytest` finds it.
- The **function** must start with `test_` so `pytest` collects it.
- The **module** must be importable — that is why `pytest` adds the root folder of your
  test file to `sys.path` automatically, and why `from calculator import ...` works
  without installing anything.

### The `python -O` gotcha

`assert` is a Python *statement*, and the interpreter can be told to remove all of them.
That is what the `-O` flag (from "optimise") does: it compiles your file with all
`assert` statements stripped out.

That is fine inside tests, because `pytest` rewrites assertions before running them. But it
is a real trap if you use `assert` to validate input in *application* code — with `-O`,
your validation silently disappears:

```python
import subprocess
import sys
import tempfile
from pathlib import Path

SOURCE = '''\
def check_age(age):
    assert age > 0, "age must be positive"
    return "ok"


print(check_age(-1))
'''

with tempfile.TemporaryDirectory() as tmp:
    script = Path(tmp) / "assert_demo.py"
    script.write_text(SOURCE, encoding="utf-8")

    print("--- python assert_demo.py ---")
    normal = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
    print((normal.stderr or normal.stdout).strip().splitlines()[-1])

    print("--- python -O assert_demo.py ---")
    optimised = subprocess.run([sys.executable, "-O", str(script)], capture_output=True, text=True)
    print(optimised.stdout.strip())
```

```text
--- python assert_demo.py ---
AssertionError: age must be positive
--- python -O assert_demo.py ---
ok
```

**Rule:** use `assert` in tests, and use explicit `raise ValueError(...)` in application
code. Never rely on `assert` to validate user input.

---

## 6. Arrange–Act–Assert

Every good test has three phases, and it helps to put them on separate lines with blank
lines between them, so a failing test tells you which phase broke.

```python
from calculator import apply_discount


def test_apply_discount_for_a_yearly_plan():
    # Arrange: set up the inputs
    price = 1200.0
    percent = 25.0

    # Act: do the thing under test
    result = apply_discount(price, percent)

    # Assert: check the outcome
    assert result == 900.0
```

* **Arrange** — build the inputs.
* **Act** — call the one function under test. Exactly one call, ideally.
* **Assert** — check the result.

If a test has several `Act` steps, it is probably testing several things and should be
split.

---

## 7. Testing that something raises

Error handling is the part of code most likely to be wrong and least likely to be tested.
`pytest.raises` is a **context manager**: it expects an exception of a given type inside
the block, and fails if none is raised.

```python
import pytest

from calculator import apply_discount


def test_apply_discount_rejects_percent_over_100():
    with pytest.raises(ValueError):
        apply_discount(100.0, 150.0)


def test_apply_discount_rejects_negative_percent():
    with pytest.raises(ValueError, match="between 0 and 100"):
        apply_discount(100.0, -10.0)
```

The `match=` argument is a **regular expression** searched inside the exception's string
form. It is the difference between "the right kind of error was raised" and "the right
kind of error was raised *for the right reason*". Always prefer a specific message check
over a bare `pytest.raises(ValueError)`.

You can also capture the exception if you need to inspect it:

```python
import pytest

from calculator import apply_discount


def test_apply_discount_error_message():
    with pytest.raises(ValueError) as error_info:
        apply_discount(100.0, 150.0)

    assert "percent" in str(error_info.value)
```

---

## 8. Fixtures — preparing data once, reusing it safely

A **fixture** is a function that sets up something a test needs and (optionally) cleans it
up afterwards. `pytest` finds it, runs it, and passes the result into your test as an
argument.

```python
# tests/test_fixtures_demo.py
import pytest

from calculator import apply_discount


@pytest.fixture
def catalogue():
    """Function scope (the default): a brand new list for every single test."""
    return [
        {"name": "Pro plan", "price": 29.0},
        {"name": "Team plan", "price": 99.0},
    ]


@pytest.fixture(scope="module")
def tax_rate():
    """Module scope: computed once, shared by every test in this file."""
    return 0.2


@pytest.fixture
def temp_customer(tmp_path):
    """Yield fixture: set up before the test, clean up after it."""
    customer_file = tmp_path / "customer.txt"
    customer_file.write_text("Ada Lovelace\n", encoding="utf-8")
    yield customer_file          # <- the test runs here
    customer_file.unlink()       # <- teardown runs here, even if the test failed


def test_catalogue_has_two_plans(catalogue):
    assert len(catalogue) == 2


def test_discount_applies_to_every_plan(catalogue, tax_rate):
    discounted = [apply_discount(plan["price"], 10.0) for plan in catalogue]
    assert discounted == [26.1, 89.1]


def test_temp_customer_file_exists(temp_customer):
    assert temp_customer.exists()
    assert "Ada" in temp_customer.read_text(encoding="utf-8")
```

### The four scopes

| Scope | How long it lives | When to use it |
|---|---|---|
| `function` (default) | one instance per test function | almost everything |
| `class` | one instance per test class | rare; useful with `unittest`-style classes |
| `module` | one instance per test file | expensive setup you do not want to repeat |
| `session` | one instance for the whole test run | a database container, a very costly resource |

A `function`-scoped fixture that returns a mutable object (a list, a dict) is rebuilt for
every test, so one test cannot accidentally change what another test sees. A
`module`- or `session`-scoped fixture returns the *same* object every time, so you must
not mutate it inside a test.

### `yield` fixtures — setup and teardown

A fixture that uses `yield` runs its code *before* the `yield` as setup, and the code
*after* the `yield` as teardown. Teardown runs even if the test fails, so this is the
right way to close a file, stop a server or delete a temporary directory.

### `autouse=True`

```python
import pytest


@pytest.fixture(autouse=True)
def reset_settings():
    """Runs before and after every test in this file, without being requested."""
    settings = {"model": "gpt-4o-mini"}
    yield settings
    settings["model"] = None
```

An `autouse` fixture applies automatically to every test in its scope — useful for
"before each test, do X" setup that you do not want to repeat in every test signature.

---

## 9. `conftest.py` — shared fixtures for a whole folder

**`conftest.py` is a special file that `pytest` loads automatically.** Anything defined in
it (fixtures, hooks, markers) is available to every test file in that folder and in every
sub-folder.

```text
my-project/
├── calculator.py
├── tests/
│   ├── conftest.py        <- fixtures shared by every test below this folder
│   ├── test_calculator.py
│   └── unit/
│       ├── conftest.py    <- fixtures for the unit tests only
│       └── test_pricing.py
```

`tests/conftest.py`:

```python
"""Fixtures available to every test in the tests/ folder."""

import pytest

from calculator import apply_discount


@pytest.fixture
def base_price():
    return 100.0


@pytest.fixture
def discounted_price(base_price):
    """A fixture may depend on another fixture."""
    return apply_discount(base_price, 20.0)
```

`tests/test_calculator.py` uses them without importing anything:

```python
from calculator import apply_discount


def test_discounted_price_fixture(discounted_price):
    assert discounted_price == 80.0


def test_base_price_fixture(base_price):
    assert base_price == 100.0
```

You never import from `conftest.py`. `pytest` injects it.

---

## 10. `tmp_path` and `monkeypatch` — the two fixtures you will use daily

### `tmp_path` — a temporary folder per test

`tmp_path` is a `pathlib.Path` pointing at a fresh, empty temporary directory that exists
only for the duration of the test. `pytest` deletes it afterwards. Your tests never touch
your real files and never collide with each other.

```python
# tests/test_files.py
from pathlib import Path

from calculator import apply_discount


def test_write_report_creates_file(tmp_path):
    report = tmp_path / "report.txt"
    report.write_text("Total: 90.00\n", encoding="utf-8")

    assert report.exists()
    assert report.read_text(encoding="utf-8") == "Total: 90.00\n"


def test_tmp_path_is_a_fresh_empty_directory(tmp_path):
    assert tmp_path.is_dir()
    assert list(tmp_path.iterdir()) == []


def test_save_invoice(tmp_path):
    invoice = tmp_path / "invoices"
    invoice.mkdir()
    (invoice / "2026-01.txt").write_text("100.00", encoding="utf-8")

    files = sorted(p.name for p in invoice.iterdir())
    assert files == ["2026-01.txt"]
```

### `monkeypatch` — change things temporarily and have them changed back

`monkeypatch` lets you change a module attribute, an environment variable or the current
working directory for the duration of one test, and it restores everything afterwards.

```python
# tests/test_monkeypatch_demo.py
import os

import calculator
from calculator import shipping_cost


def test_monkeypatch_changes_an_attribute(monkeypatch):
    monkeypatch.setattr(calculator, "shipping_cost", lambda weight, express=False: 0.0)

    # calling through the module uses the patched attribute
    assert calculator.shipping_cost(5.0) == 0.0

    # the name imported at the top of this file still points at the original
    assert shipping_cost(5.0) == 12.49


def test_monkeypatch_sets_an_environment_variable(monkeypatch):
    monkeypatch.setenv("APP_ENV", "testing")
    assert os.environ["APP_ENV"] == "testing"


def test_monkeypatch_deletes_an_environment_variable(monkeypatch):
    monkeypatch.setenv("TEMP_FLAG", "1")
    monkeypatch.delenv("TEMP_FLAG")
    assert "TEMP_FLAG" not in os.environ


def test_monkeypatch_changes_the_working_directory(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    assert os.getcwd() == str(tmp_path)
```

`monkeypatch.setattr` is the lighter alternative to `unittest.mock.patch` and is the right
tool when you just need to swap one function for a test.

---

## 11. Parametrisation — one test, many cases

When you have the same assertion over a table of inputs, write the test once and let
`pytest` run it for every row. `@pytest.mark.parametrize` takes the *names* of the
arguments and a list of value tuples.

```python
# tests/test_parametrised.py
import pytest

from calculator import apply_discount, shipping_cost


@pytest.mark.parametrize(
    ("price", "percent", "expected"),
    [
        (100.0, 0.0, 100.0),
        (100.0, 10.0, 90.0),
        (100.0, 25.0, 75.0),
        (99.99, 50.0, 49.99),
        (10.0, 100.0, 0.0),
    ],
)
def test_apply_discount(price, percent, expected):
    assert apply_discount(price, percent) == expected


@pytest.mark.parametrize(
    ("weight", "express", "expected"),
    [(0.0, False, 4.99), (2.0, False, 7.99), (2.0, True, 13.98)],
)
def test_shipping_cost(weight, express, expected):
    assert shipping_cost(weight, express) == expected


@pytest.mark.parametrize("percent", [-1, 101, 1000])
def test_apply_discount_rejects_bad_percent(percent):
    with pytest.raises(ValueError):
        apply_discount(100.0, percent)
```

```text
============================= test session starts ==============================
collected 11 items

tests/test_parametrised.py ...........                                   [100%]

============================= 11 passed in 0.03s ==============================
```

Each row becomes its own test case with its own name, so when one fails you know exactly
which input broke it.

---

## 12. Markers — labelling tests

A **marker** is a label you put on a test. `pytest` uses markers to select subsets of your
suite.

```python
# tests/test_marked.py
import sys

import pytest

from calculator import shipping_cost


@pytest.mark.slow
def test_slow_thing():
    assert shipping_cost(3.0) == 9.49


@pytest.mark.integration
def test_integration_thing():
    assert shipping_cost(1.0) == 6.49


@pytest.mark.skipif(sys.platform == "win32", reason="this test only works on POSIX")
def test_posix_only():
    assert shipping_cost(1.0) == 6.49


@pytest.mark.skip("known bug: rounding differs on macOS")
def test_known_bug():
    assert shipping_cost(1.0) == 6.49
```

Custom markers **must be registered**, otherwise `pytest` warns about unknown markers
(adding `strict = true` or `--strict-markers` turns that warning into an error). Register
them in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
markers = [
    "slow: tests that take more than a second",
    "integration: tests that talk to a real external service",
]
```

Then:

```bash
pytest -m "not slow"        # skip the slow ones
pytest -m "integration"     # only the integration ones
```

Skipping a test is not the same as deleting it. A skipped test with a reason is a
documented "not covered yet".

---

## 13. Mocking — testing code that talks to the outside world

A **mock** is a fake object that stands in for a real one, records how it was used, and
lets you control what it returns. `unittest.mock` is in the standard library, so no extra
install is needed.

Here is the module we want to test. It pretends to call an LLM:

```python
# llm_client.py
"""A tiny stand-in for an LLM API client."""

import logging
from typing import Protocol

logger = logging.getLogger(__name__)


class LLMClient(Protocol):
    """The shape any LLM client must have."""

    def complete(self, prompt: str) -> str:
        """Return the model's reply to a prompt."""
        ...


class EchoClient:
    """A fake client that returns a canned reply and records the prompts."""

    def __init__(self) -> None:
        self.prompts: list[str] = []

    def complete(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return f"Canned summary of {len(prompt)} characters."


def summarise(client: LLMClient, text: str, max_words: int = 40) -> str:
    """Ask the client for a summary and return it as one clean line."""
    if not text.strip():
        raise ValueError("text must not be empty")
    if len(text.split()) < 10:
        logger.warning(
            "Text is short (%d words); the summary may be trivial.", len(text.split())
        )
    prompt = f"Summarise the following in at most {max_words} words:\n{text}"
    reply = client.complete(prompt)
    return " ".join(reply.split())


if __name__ == "__main__":
    document = "This is a long document about the history of the printing press."
    print(summarise(EchoClient(), document))
```

```text
Canned summary of 109 characters.
```

Note the `Protocol` class: it says "anything with a `complete(prompt) -> str` method can be
used here" without writing a class hierarchy. That is what lets you drop a `MagicMock` in
without changing a line of production code.

Now the tests. Save as `tests/test_llm_client.py`:

```python
"""Tests for the LLM client using unittest.mock."""

from unittest.mock import MagicMock, patch

import pytest

from llm_client import EchoClient, summarise


def test_summarise_collapses_whitespace():
    fake_client = MagicMock()
    fake_client.complete.return_value = "  A short   summary.  "

    result = summarise(fake_client, "Some reasonably long document text.")

    assert result == "A short summary."


def test_summarise_passes_the_document_to_the_client():
    fake_client = MagicMock()
    fake_client.complete.return_value = "summary"

    summarise(fake_client, "The quick brown fox jumps over the lazy dog.", max_words=10)

    fake_client.complete.assert_called_once()
    prompt = fake_client.complete.call_args.args[0]
    assert "at most 10 words" in prompt
    assert "quick brown fox" in prompt


def test_summarise_raises_on_empty_text():
    with pytest.raises(ValueError, match="must not be empty"):
        summarise(EchoClient(), "   ")


def test_summarise_with_patch_as_a_context_manager():
    with patch("llm_client.EchoClient.complete", return_value="  spaced   out  ") as mock_call:
        result = summarise(EchoClient(), "Some reasonably long document text.")

    assert result == "spaced out"
    mock_call.assert_called_once()


@patch("llm_client.EchoClient.complete", return_value="decorated reply")
def test_summarise_with_patch_as_a_decorator(mock_call):
    assert summarise(EchoClient(), "Some reasonably long document text.") == "decorated reply"
    mock_call.assert_called_once()


def test_side_effect_raises_an_exception():
    with patch("llm_client.EchoClient.complete", side_effect=RuntimeError("API down")):
        with pytest.raises(RuntimeError, match="API down"):
            summarise(EchoClient(), "Some reasonably long document text.")


def test_side_effect_list_returns_values_in_order():
    with patch("llm_client.EchoClient.complete", side_effect=["first reply", "second reply"]):
        assert summarise(EchoClient(), "Some reasonably long document text.") == "first reply"
        assert summarise(EchoClient(), "Some reasonably long document text.") == "second reply"


def test_side_effect_function_can_fail_then_recover():
    calls = []

    def flaky(prompt: str) -> str:
        calls.append(prompt)
        if len(calls) < 2:
            raise RuntimeError("API unavailable")
        return "recovered"

    with patch("llm_client.EchoClient.complete", side_effect=flaky):
        with pytest.raises(RuntimeError):
            summarise(EchoClient(), "Some reasonably long document text.")

    assert len(calls) == 1
```

Here is what each piece does.

### `MagicMock`

```python
from unittest.mock import MagicMock

fake_client = MagicMock()
fake_client.complete.return_value = "  A short   summary.  "

print(repr(fake_client.complete("summarise this")))
print(fake_client.complete.call_args)
```

```text
'  A short   summary.  '
call('summarise this')
```

A `MagicMock` accepts any attribute access and any call. `fake_client.complete(...)` does
not run anything — it returns `fake_client.complete.return_value`, which you set
explicitly. `MagicMock` also records every call, which is how you assert on it.

`Mock` is the same idea without the magic methods (`len()`, `with`, iteration). Use
`MagicMock` unless you specifically want a plain `Mock`.

### `patch` as a context manager

```python
from unittest.mock import patch

from llm_client import EchoClient, summarise

with patch("llm_client.EchoClient.complete", return_value="spaced out") as mock_call:
    print(summarise(EchoClient(), "Some reasonably long document text."))

print(mock_call.call_args)
```

`patch` temporarily replaces the named attribute and restores the original when the block
ends. The target is a **string path**: `module_name.attribute_name`. That matters —
patching `"llm_client.EchoClient.complete"` replaces the method *in the module under
test*, which is what you want. Patching `"test_llm_client.EchoClient.complete"` would
create a new attribute on the test module and change nothing.

### `patch` as a decorator

```python
from unittest.mock import patch

from llm_client import EchoClient, summarise


@patch("llm_client.EchoClient.complete", return_value="decorated reply")
def patched_test(mock_call):
    print(summarise(EchoClient(), "Some reasonably long document text."))
    print(mock_call.call_count)


patched_test()
```

The patched mock is passed into the test as an extra argument. Same mechanism, less
indentation.

### `side_effect`

`side_effect` controls what happens *instead of* returning a value:

- an **exception instance** — it is raised: `side_effect=RuntimeError("API down")`.
- an **exception class** — it is raised with no message.
- a **list** — each call returns the next item: `side_effect=["a", "b"]`.
- a **function** — the function is called with the same arguments, and its return value is
  used. This is how you simulate "fails twice, then succeeds".

### Asserting on calls

```python
from unittest.mock import MagicMock

mock_call = MagicMock()
mock_call("hello", max_words=10)

mock_call.assert_called_once()                              # called exactly once
mock_call.assert_called()                                   # called at least once
mock_call.assert_called_with("hello", max_words=10)         # called with these exact args
mock_call.assert_called_once_with("hello", max_words=10)    # exactly once, with these args

unused_mock = MagicMock()
unused_mock.assert_not_called()                             # never called

args, kwargs = mock_call.call_args             # the arguments of the last call
print(args)                                    # ('hello',)
print(kwargs)                                  # {'max_words': 10}
```

### The lighter alternative: `monkeypatch.setattr`

```python
from llm_client import EchoClient, summarise


def test_summarise_with_monkeypatch(monkeypatch):
    monkeypatch.setattr(EchoClient, "complete", lambda self, prompt: "monkey patched")
    assert summarise(EchoClient(), "Some reasonably long document text.") == "monkey patched"
```

No import of `patch`, no context manager, no mock object. `monkeypatch` is the better tool
when you only need to swap one function. Reach for `unittest.mock` when you need to assert
on *how* the dependency was called.

---

## 14. `caplog` — asserting on log output

`caplog` captures what your code logged during a test, so you can assert that a warning
was emitted.

```python
# tests/test_logging.py
import logging

from llm_client import EchoClient, summarise


def test_short_text_logs_a_warning(caplog):
    with caplog.at_level(logging.WARNING, logger="llm_client"):
        summarise(EchoClient(), "Only three words")

    assert "Text is short" in caplog.text
    assert "3 words" in caplog.text


def test_long_text_logs_nothing(caplog):
    with caplog.at_level(logging.WARNING, logger="llm_client"):
        summarise(EchoClient(), "This document has plenty of words in it, so no warning.")

    assert caplog.text == ""
```

`caplog.text` is the whole log as one string; `caplog.records` is the list of individual
`LogRecord` objects if you want to check the level or the logger name.

---

## 15. Coverage — how much of your code the tests touched

**Coverage** is the percentage of your source lines that were executed by your test suite.
If a line never runs, it is never tested — whatever you think about it.

```bash
python -m pip install pytest-cov
pytest --cov=calculator --cov-report=term-missing
```

```text
=============================== tests coverage ================================
_______________ coverage: platform win32, python 3.13.1-final-0 _______________

Name                                                                  Stmts   Miss  Cover   Missing
---------------------------------------------------------------------------------------------------
calculator.py                                                           12      3    75%   7, 20-21
---------------------------------------------------------------------------------------------------
TOTAL                                                                    12      3    75%
4 passed in 0.82s
```

The `Missing` column lists the line numbers that were never executed. Line 7 is the
`raise ValueError(...)` inside `apply_discount` — no test triggers the error path yet.
Lines 20-21 are the `if __name__ == "__main__":` block, which is never covered by a test
suite and is usually excluded.

### What coverage does and does not tell you

Coverage **does** tell you:

- Which lines have never been executed. Those are the lines most likely to be broken,
  because nobody has ever run them.
- Whether your test suite is doing anything at all (0% coverage means it is not).

Coverage **does not** tell you:

- Whether the assertions are correct. You can execute every line of a function and still
  assert nothing meaningful. 100% coverage with one `assert True` is worthless.
- Whether the behaviour is right. Coverage measures execution, not correctness.
- Whether the *edge cases* are covered. The happy path can be 100% covered and the error
  path 0% covered.

Treat coverage as a **floor, not a goal**. A reasonable target for application code is
80-90% with the important branches (error handling, edge cases) explicitly covered. A
100% coverage number on a project that asserts nothing is a warning sign, not an
achievement.

---

## 16. Test-driven development: red, green, refactor

**TDD** is a discipline: you write a failing test first, then write the smallest code that
makes it pass, then clean it up while keeping it green.

```text
        ┌──────────────────────────────────────────────┐
        │                                              │
        ▼                                              │
   ┌─────────┐   write a failing test    ┌──────────┐  │
   │   RED   │ ─────────────────────────▶ │  GREEN   │  │
   │  (fail) │                            │ (pass)   │  │
   └─────────┘                            └──────────┘  │
        ▲                                     │        │
        │  the test still fails              │        │
        │  (new insight)                     ▼        │
        │                              ┌──────────┐    │
        └──────────────────────────────│ REFACTOR │────┘
                                       │ (clean)  │
                                       └──────────┘
```

### A worked example

**Red.** Write the test first, in a brand-new module called `tdd_calculator.py`. It fails
immediately, because that module does not exist yet:

```python
# tests/test_tdd.py
from tdd_calculator import apply_discount


def test_apply_discount_ten_percent():
    assert apply_discount(100.0, 10.0) == 90.0
```

```text
E   ModuleNotFoundError: No module named 'tdd_calculator'
```

**Green.** Write the smallest code that passes:

```python
# tdd_calculator.py
def apply_discount(price: float, percent: float) -> float:
    return round(price * (1 - percent / 100), 2)
```

```text
tests/test_tdd.py .                                                  [100%]
1 passed
```

**Refactor.** Now add the requirement you know is coming — rejecting invalid input —
and let the test drive it. First the test (red):

```python
# tests/test_tdd.py
import pytest

from tdd_calculator import apply_discount


def test_apply_discount_ten_percent():
    assert apply_discount(100.0, 10.0) == 90.0


def test_apply_discount_rejects_percent_over_100():
    with pytest.raises(ValueError, match="between 0 and 100"):
        apply_discount(100.0, 150.0)
```

```text
E   Failed: DID NOT RAISE <class 'ValueError'>
```

Then the implementation (green):

```python
# tdd_calculator.py
def apply_discount(price: float, percent: float) -> float:
    if not 0 <= percent <= 100:
        raise ValueError("percent must be between 0 and 100")
    return round(price * (1 - percent / 100), 2)
```

```text
tests/test_tdd.py ..                                                 [100%]
2 passed
```

TDD feels slower at the start and much faster afterwards, because you never write a large
amount of code without knowing it works, and the test suite is a by-product of the work
rather than something you bolt on at the end.

---

## 17. What to test and what not to test

### Do not test

- **Private implementation details.** A function named `_calculate_score` is an internal
  detail. If you test it directly, every refactor breaks the test suite and you stop
  refactoring.
- **Trivial getters and setters.** `assert obj.x == 5` after `obj.x = 5` tests the
  language, not your code.
- **Third-party code.** Do not test that `httpx` can make an HTTP request. Test *your*
  code that uses `httpx`.
- **The framework itself.** `pytest` testing `pytest` is not your job.

### Do test

- **Business rules.** "A discount above 100% is invalid." "Express shipping costs
  1.75x." These are the rules that change and that your team argues about.
- **Edge cases.** Zero, one, a very large number, negative numbers, empty strings,
  `None`, unicode, a string with emoji in it.
- **Error paths.** The `except` branches are usually the least-tested code in a project
  and the most likely to contain bugs.
- **The public API.** The functions and classes your callers actually use.

### The five test doubles

| Double | What it is | Use it for |
|---|---|---|
| **Dummy** | An object that does nothing, just fills a parameter | Passing around to satisfy a signature |
| **Stub** | Returns canned answers so the caller can proceed | Replacing a slow dependency (a database, a web API) |
| **Spy** | A stub that also records how it was called | Asserting "the API was called with this prompt" |
| **Mock** | A spy with pre-programmed return values and `side_effect` | Verifying calls and return values |
| **Fake** | A working, simplified implementation | Replacing something expensive but simple (an in-memory database) |

`MagicMock` covers the stub/spy/mock roles. `monkeypatch` with a lambda covers the stub
role. A fake is something you write yourself — for example, a tiny in-memory list
standing in for a real database in your tests.

---

## 18. Closing the loop: `pytest` + `pre-commit`

You set up `pre-commit` in [12 — Environments and tooling](12-environments-and-tooling.md).
Now add the test run to it, so you cannot commit code that fails its own tests:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.4
    hooks:
      - id: ruff-check
        args: [--fix]
      - id: ruff-format

  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: python -m pytest -q
        language: system
        pass_filenames: false
        types: [python]
```

```text
Trim Trailing Whitespace.........................Passed
Fix End of Files.................................Passed
ruff check........................................Passed
ruff format......................................Passed
pytest...........................................Passed
```

And in CI, run the same three commands in the same order — fast checks first:

```yaml
- name: Lint
  run: ruff check .
- name: Type check
  run: mypy src/
- name: Test
  run: pytest --cov=src --cov-report=term-missing
```

Your project now has the complete loop: format, lint, type check, test — locally on every
commit and again on every push.

---

## 🧪 Try it yourself

**Exercise 1 — Test the things that break.**
Write `tests/test_calculator_extra.py` with tests for: a discount of exactly 100%
(price becomes 0), a negative price, a weight of zero, and express shipping with a
fractional weight. Use `pytest.raises` for the error cases and `pytest.mark.parametrize`
for the shipping table.

<details>
<summary>Hint</summary>

Negative prices are *allowed* by `apply_discount` — it only validates the percent. So test
that a negative price produces a negative result rather than an exception. Then add a
`pytest.raises` test for `percent` being negative.
</details>

<details>
<summary>Solution</summary>

```python
import pytest

from calculator import apply_discount, shipping_cost


def test_full_discount_makes_the_price_zero():
    assert apply_discount(42.0, 100.0) == 0.0


def test_negative_price_is_allowed_and_stays_negative():
    assert apply_discount(-50.0, 10.0) == -45.0


def test_negative_percent_raises():
    with pytest.raises(ValueError, match="between 0 and 100"):
        apply_discount(50.0, -1.0)


@pytest.mark.parametrize(
    ("weight", "express", "expected"),
    [(0.0, True, 8.73), (0.5, False, 5.74), (0.5, True, 10.04)],
)
def test_shipping_cost_table(weight, express, expected):
    assert shipping_cost(weight, express) == expected
```

```text
6 passed in 0.36s
```
</details>

**Exercise 2 — Build a fixture in `conftest.py`.**
Create `tests/conftest.py` with a `priced_item` fixture that returns a dict
`{"name": "Widget", "price": 20.0}`, and a `discounted_item` fixture that depends on it
and applies a 25% discount. Write one test that uses each.

<details>
<summary>Hint</summary>

A fixture can take another fixture as an argument. Put both fixtures in
`tests/conftest.py` and just use them as parameters in the test — no import needed.
</details>

<details>
<summary>Solution</summary>

`tests/conftest.py`:

```python
import pytest

from calculator import apply_discount


@pytest.fixture
def priced_item():
    return {"name": "Widget", "price": 20.0}


@pytest.fixture
def discounted_item(priced_item):
    priced_item["discounted_price"] = apply_discount(priced_item["price"], 25.0)
    return priced_item
```

`tests/test_fixtures.py`:

```python
def test_priced_item(priced_item):
    assert priced_item["name"] == "Widget"
    assert priced_item["price"] == 20.0


def test_discounted_item(discounted_item):
    assert discounted_item["discounted_price"] == 15.0
```

```text
2 passed in 0.03s
```
</details>

**Exercise 3 — Write a test that does not touch the network.**
The function `summarise` in `llm_client.py` calls `client.complete(prompt)`. Write a test
that proves the correct prompt was built, without calling a real API. Then write a second
test that proves a `RuntimeError` from the model propagates to the caller.

<details>
<summary>Hint</summary>

`unittest.mock.patch` with `side_effect=RuntimeError("boom")` will make the patched call
raise. Combine it with `pytest.raises`. The patch target is the string path
`"llm_client.EchoClient.complete"`.
</details>

<details>
<summary>Solution</summary>

```python
from unittest.mock import patch

import pytest

from llm_client import EchoClient, summarise


def test_prompt_contains_the_document():
    with patch("llm_client.EchoClient.complete", return_value="a summary") as mock_call:
        summarise(EchoClient(), "The industrial revolution changed everything.", max_words=12)

    prompt = mock_call.call_args.args[0]
    assert "industrial revolution" in prompt
    assert "at most 12 words" in prompt


def test_api_error_propagates():
    with patch("llm_client.EchoClient.complete", side_effect=RuntimeError("boom")):
        with pytest.raises(RuntimeError, match="boom"):
            summarise(EchoClient(), "The industrial revolution changed everything.")
```

```text
2 passed in 0.03s
```
</details>

**Exercise 4 — Measure coverage and find an untested branch.**
Run `pytest --cov=calculator --cov-report=term-missing`. Find the lines marked as missing,
add one test that covers them, and re-run. Aim for 100% *and* make sure the new test
actually asserts something meaningful.

<details>
<summary>Hint</summary>

The `if __name__ == "__main__":` block at the bottom of `calculator.py` is never covered
by the test suite — that is normal and usually ignored. Use `--cov-report=term-missing`
to see the exact line numbers.
</details>

<details>
<summary>Solution</summary>

```bash
pytest --cov=calculator --cov-report=term-missing
```

```text
Name                                                                  Stmts   Miss  Cover   Missing
---------------------------------------------------------------------------------------------------
calculator.py                                                           12      3    75%   7, 20-21
---------------------------------------------------------------------------------------------------
TOTAL                                                                    12      3    75%
```

Line 7 is the `ValueError` branch — add a `pytest.raises` test to cover it. Lines 20-21
are the `__main__` block, which is usually ignored. You can exclude it like this:

```toml
[tool.coverage.run]
omit = ["*/__main__.py", "*/tests/*"]
```

After adding the `pytest.raises` test, the meaningful code is fully covered.
</details>

---

## ✅ Checkpoint

**1. What are the three kinds of test, and which one should you write the most of?**

<details>
<summary>Answer</summary>

Unit tests (one function in isolation), integration tests (several real components
together) and end-to-end tests (the whole system). Write mostly unit tests: they are
fast, cheap and pinpoint failures.
</details>

**2. Why is `pytest` preferred over `unittest` for new projects?**

<details>
<summary>Answer</summary>

Tests are plain functions with plain `assert` (no class boilerplate), failure output shows
the differing values and local variables, and the plugin ecosystem (`pytest-cov`,
`pytest-asyncio`, `pytest-mock`) extends it easily.
</details>

**3. What does `pytest -x`, `pytest -k "discount"`, `pytest -m "slow"` and `pytest --lf` do?**

<details>
<summary>Answer</summary>

`-x` stops at the first failure, `-k` selects tests whose name matches a keyword, `-m`
selects tests by marker, and `--lf` re-runs only the tests that failed last time.
</details>

**4. What happens to `assert` statements when Python runs with `-O`, and why does it matter?**

<details>
<summary>Answer</summary>

They are removed from the compiled code entirely, so the check silently disappears. That is
why `assert` is only safe in test code (where `pytest` rewrites them) and why application
code must use explicit `raise ValueError(...)`.
</details>

**5. What is a fixture, and what does `scope="module"` change?**

<details>
<summary>Answer</summary>

A fixture is a setup function whose result `pytest` injects into your test. `scope="module"`
means it is created once per test *file* and shared by every test in it, instead of once
per test function.
</details>

**6. What is the difference between `tmp_path` and `monkeypatch`?**

<details>
<summary>Answer</summary>

`tmp_path` gives you a fresh temporary directory per test (auto-cleaned). `monkeypatch`
temporarily changes an attribute, an environment variable or the working directory and
restores the original afterwards.
</details>

**7. Why does `patch("llm_client.call_model")` matter more than `patch("call_model")`?**

<details>
<summary>Answer</summary>

The string must be the path to the attribute *as seen from the module that uses it*.
Patching the module path replaces the function where `summarise` looks it up; patching a
bare name would only affect the test module's own namespace and change nothing.
</details>

**8. What does 100% test coverage guarantee?**

<details>
<summary>Answer</summary>

Only that every line was executed at least once. It guarantees nothing about correctness,
about whether the assertions are meaningful, or about whether the important edge cases
are tested. Coverage is a floor, not a goal.
</details>

---

## 🐛 Common mistakes

| Mistake | What you see | Fix |
|---|---|---|
| Putting tests in the same folder as your source and naming them `calculator_test.py` | `pytest` says "no tests ran" | Name the file `test_*.py` or `*_test.py`, and set `testpaths = ["tests"]` |
| Using `assert` for input validation in application code | Works until someone runs with `-O`, then the check vanishes | Use `raise ValueError(...)` in application code; reserve `assert` for tests |
| Importing from `conftest.py` | `ImportError: cannot import name 'my_fixture'` | Never import from `conftest.py`; `pytest` injects the fixtures automatically |
| A `module`-scoped fixture returns a mutable list that a test mutates | A later test fails depending on test order | Return fresh data from `function`-scoped fixtures, or copy the data inside the test |
| Patching the wrong path: `patch("test_module.call_model")` | The real function still runs, and your assertion fails | Patch `"module_under_test.function_name"` — the path as the *caller* sees it |
| `pytest.raises(ValueError)` with no `match=` | The test passes for the wrong reason (a different `ValueError`) | Always add `match="some text"` so the test checks the message too |
| `assert` with no message inside a loop of 200 cases | A failure tells you nothing about which case broke | Use `@pytest.mark.parametrize` so each case gets its own named test |
| Asserting on a `MagicMock` attribute you never configured | `AssertionError: expected 'x' but got <MagicMock ...>` | Set `.return_value` or `.side_effect` explicitly, and assert on `call_args` |
| Relying on `time.sleep()` in tests to "let things happen" | Flaky tests: pass locally, fail in CI | Use `monkeypatch` on the clock, or test the logic, not the timing |
| Chasing 100% coverage and writing assertion-free tests to get there | Coverage goes up, bugs still ship | Cover branches, not lines; every test must assert something meaningful |

---

## 🔗 Resources

- [pytest documentation](https://docs.pytest.org/en/stable/) — the official reference for
  every feature, fixture and marker.
- [pytest — Getting Started](https://docs.pytest.org/en/stable/getting-started.html) — the
  short, gentle introduction if the full docs feel heavy.
- [pytest fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html) — everything
  about scopes, `yield`, `autouse` and `request`.
- [pytest mocking](https://docs.pytest.org/en/stable/how-to/monkeypatch.html) — the
  official guide to `monkeypatch` and `unittest.mock` integration.
- [pytest-cov on PyPI](https://pypi.org/project/pytest-cov/) — the coverage plugin used in
  this file.
- [unittest.mock — Python documentation](https://docs.python.org/3/library/unittest.mock.html)
  — the complete reference for `MagicMock`, `patch`, `side_effect` and `call_args`.
- [Coverage.py documentation](https://coverage.readthedocs.io/en/latest/) — what coverage
  measures, and how to exclude lines you do not want counted.
- [The Test Pyramid](https://martinfowler.com/bliki/TestPyramid.html) — Martin Fowler on the
  unit/integration/end-to-end split, and why the shape matters.
- [Martin Fowler: Test Driven Development](https://martinfowler.com/bliki/TestDrivenDevelopment.html)
  — a clear introduction to the red-green-refactor loop.
- [pytest on GitHub](https://github.com/pytest-dev/pytest) — the source, the issue tracker
  and the full plugin list.

---

## ➡️ Next

- [14 — Standard library](14-standard-library.md) — you have built a tested, professional
  project; now meet the enormous toolbox that ships with Python itself, for free.

**← Previous:** [12 — Environments and tooling](12-environments-and-tooling.md)
