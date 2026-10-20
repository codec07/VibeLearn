# Modules and Packages

Right now every program you have written has lived in a single file. That works until it does
not: a 2,000-line file is impossible to navigate, and you cannot reuse a function you wrote last
Tuesday without copying it everywhere. **Modules** let you split your code across files, **packages**
let you group those files into something installable, and `pip` lets you borrow code that other
people have already written. This file covers all three, plus the one-line guard
(`if __name__ == "__main__":`) that every real Python project uses.

> **⏱️ Time:** ~30 minutes
> **📚 Prereqs:** [07-comprehensions-and-iterators.md](07-comprehensions-and-iterators.md)
> **🎯 By the end you can:** split a program across multiple files, import from other files and
> from installed packages, manage dependencies with `pip` and virtual environments, and diagnose
> the `ModuleNotFoundError` that every beginner hits at least once.

---

## Why this matters for AI engineering

Every real AI project has more files than you can hold in your head. A typical RAG application
might have `ingest.py`, `embed.py`, `retrieve.py`, `llm.py`, `config.py` and a `tests/` folder.
Nobody writes that as one 4,000-line file.

Just as important, the AI stack is made of *packages*. `openai`, `anthropic`, `langchain`,
`pydantic`, `numpy`, `pandas` — every one of them is a package you install with `pip` and import
with one line. If you do not understand how importing works, you cannot debug the single most
common error in Python: `ModuleNotFoundError`.

And when you eventually build something others can use, you will package *your* code and publish
it to PyPI so that `pip install your-tool` works for the whole world. That path starts here.

---

## 1. What is a module, and what is a package?

- A **module** is simply a Python file with a `.py` extension. `utils.py` is a module.
- A **package** is a *directory* of modules that Python treats as one unit. `myapp/` containing
  `__init__.py`, `greeting.py` and `retrieval.py` is a package.

That is the whole definition. Everything else in this file is machinery for finding those files
on disk and running their code.

Python ships with a huge collection of modules called the **standard library** — `math`,
`random`, `datetime`, `json`, `os`, `pathlib`. Those are already installed and ready to use.

---

## 2. The four ways to import

```python
import math                       # the whole module
from math import sqrt            # one name from the module
import math as m                  # the whole module, under a shorter name
from math import sqrt as root    # one name, under a different name

print(math.floor(3.7))
print(sqrt(16))
print(m.floor(3.7))
print(root(16))
```

```text
3
4.0
3
4.0
```

| Form | What it brings in | Use it when |
|---|---|---|
| `import math` | the module itself | **almost always** |
| `from math import sqrt` | just `sqrt` | you want the short name, or the module is huge |
| `import math as m` | the module, renamed | `math` clashes with a local name |
| `from math import sqrt as root` | `root` | renaming for clarity |

### 2.1 Why `import module` is the better habit

Both styles work, but they are not equivalent, and the difference matters as your codebase grows.

```python
import math

print(math.sqrt(16))
```

```python
from math import sqrt

print(sqrt(16))
```

The first version is **namespaced**. `math.sqrt` says clearly where `sqrt` came from. The second
version drops `sqrt` into your namespace, where it can collide with another `sqrt` you imported
from somewhere else, or with a variable you define later.

A concrete version of that collision:

```python
import statistics

data = [1, 2, 3, 4, 5]
mean = statistics.mean(data)      # clear: statistics.mean
print("mean:", mean)
```

If you had written `from statistics import mean`, then `mean` would be a bare name, and a reader
could not tell whether it came from `statistics` or from your own code.

**Recommendation: prefer `import module` and call `module.function()`.** Use `from x import y`
when the name is unambiguous and you want the brevity, or when you are importing from *your own*
code and the module name adds noise.

---

## 3. `__name__` and the `if __name__ == "__main__":` guard

This is the single most important piece of Python syntax in this file, and it is only three
lines long.

Every Python module has a built-in variable called `__name__`. Its value depends on **how the
file was loaded**:

- If you ran the file directly (`python main.py`), `__name__` is `"__main__"`.
- If another file did `import main`, `__name__` is `"main"` — the module's own name.

So this guard:

```python
def main():
    print("main() ran")


if __name__ == "__main__":
    main()
```

```text
main() ran
```

means: *"only run `main()` when this file is the program being run, not when it is being
imported by someone else."*

### 3.1 A runnable two-file example

Create a folder with these two files.

```text
my_project/
├── main.py
└── utils.py
```

`utils.py`:

```python
# utils.py
"""Small helper functions used by main.py."""

GREETING = "hello"


def shout(text):
    """Return the text in upper case with an exclamation mark."""
    return f"{text.upper()}!"


def add(left, right):
    """Return the sum of two numbers."""
    return left + right


if __name__ == "__main__":
    # This runs only when you type:  python utils.py
    print("utils.py run directly")
    print(shout(GREETING))
```

`main.py`:

```python
# main.py
"""The entry point of the program."""
import utils


def main():
    print(utils.shout(utils.GREETING))
    print(utils.add(2, 3))


if __name__ == "__main__":
    main()
```

Now run it, from inside `my_project/`:

```bash
python main.py
```

```text
HELLO!
5
```

The same file, when it is *imported* instead of run, does not call `main()`:

```bash
python -c "import main"
```

```text
```

Nothing is printed. That is the guard doing its job.

### 3.2 Why the guard exists

Without it, importing a module would run all of its top-level code. That matters as soon as a
module does anything with side effects — opening a file, connecting to a database, starting a
server, or printing a banner.

The guard gives you a module that is safe to import *and* runnable on its own. It is the
difference between a library and a script, and every professional Python file uses it.

**Rule of thumb:** put your program logic in functions, and call them from inside the guard.

---

## 4. `sys.path` — why "ModuleNotFoundError" happens

When Python sees `import utils`, it has to find a file called `utils.py`. It searches a list of
folders called **`sys.path`**. The first entry is usually the folder containing the script you
are running.

```python
import sys
import site

print("sys.path holds", len(sys.path), "folders to search")
print("the first one is the folder of the script you are running")
print("site-packages is one of them:",
      any(entry.endswith("site-packages") for entry in sys.path))
```

```text
sys.path holds 9 folders to search
the first one is the folder of the script you are running
site-packages is one of them: True
```

(The exact number of entries varies between machines and installations, but the shape is always
the same. `site.getsitepackages()` prints the full path of the folder where `pip` installs
packages — on this machine, `C:\Python313\Lib\site-packages`.)

Two entries matter to you right now:

- **The script's own folder** (or the current folder) — this is why `import utils` works when
  `utils.py` sits next to `main.py`.
- **`site-packages`** — the folder where `pip` installs third-party packages.

### 4.1 The error and its fix

Here is the classic failure. A project like this:

```text
my_project/
├── config.py
└── app/
    └── run.py
```

`config.py` contains `PROJECT_NAME = "my-ai-project"`, and `app/run.py` contains:

```python
# app/run.py  -- this file FAILS to run from the project root, and that is the bug
import config

print(config.PROJECT_NAME)
```

Run it from the project root:

```bash
python app/run.py
```

```text
Traceback (most recent call last):
  File "app/run.py", line 1, in <module>
    import config
ModuleNotFoundError: No module named 'config'
```

Why? Python put `app/` on `sys.path` (the folder of the script being run), **not** the project
root where `config.py` actually lives. The folder you are standing in is only added
automatically in some cases, which is why this bug feels random.

### 4.2 The fix checklist

Work down this list in order:

1. **Check the file name and the import name.** They must match exactly, including case.
   `Config.py` is not `config.py` on Linux and macOS.
2. **Check the file extension.** `config.py`, not `config.py.txt`. Windows hides extensions by
   default, so a file called `config.py.txt` is a classic trap.
3. **Check where the file is**, relative to the folder Python is searching (`sys.path`).
4. **Run from the project root** so the root is on the path.
5. **Set `PYTHONPATH`** to point at the folder that contains the module:

   ```bash
   # Windows (PowerShell)
   $env:PYTHONPATH = "C:\Users\Aarush\my_project"
   python app\run.py

   # macOS / Linux
   PYTHONPATH=/Users/aarush/my_project python app/run.py
   ```

6. **Install your project as a package** — the permanent fix. See section 11.

With `PYTHONPATH` set correctly, the same command works:

```text
my-ai-project
```

---

## 5. Creating your own modules

The folder structure above is the simplest possible layout, and it is fine for a small script.
For anything larger, use a clear separation:

```text
my_project/
├── README.md
├── requirements.txt
├── src/
│   └── myapp/
│       ├── __init__.py
│       ├── greeting.py
│       └── retrieval.py
├── tests/
│   └── test_greeting.py
└── scripts/
    └── demo.py
```

The convention — `src/` layout, tests in their own folder, scripts separate from library code —
keeps the importable code separate from the code that *runs* things. You will meet it again in
[12-environments-and-tooling.md](12-environments-and-tooling.md).

---

## 6. Packages and `__init__.py`

A package is a directory. For Python to treat it as a package, it normally contains a file
called `__init__.py`. That file can be empty, or it can hold the package's public API.

```text
myapp/
├── __init__.py
├── greeting.py
└── __main__.py
```

`myapp/__init__.py`:

```python
# myapp/__init__.py
"""myapp - a tiny example package."""
VERSION = "1.0.0"
```

`myapp/greeting.py`:

```python
# myapp/greeting.py
"""The greeting tool inside the myapp package."""
from myapp import VERSION


def greet(name):
    """Return a greeting for someone."""
    return f"Hello {name}, this is myapp {VERSION}"


if __name__ == "__main__":
    print(greet("Aarush"))
```

`myapp/__main__.py`:

```python
# myapp/__main__.py
"""Entry point:  python -m myapp"""
from myapp.greeting import greet


def main():
    print(greet("Aarush"))


if __name__ == "__main__":
    main()
```

Now, from the folder that contains `myapp/`:

```bash
python -m myapp.greeting
```

```text
Hello Aarush, this is myapp 1.0.0
```

```bash
python -m myapp
```

```text
Hello Aarush, this is myapp 1.0.0
```

```bash
python -c "from myapp.greeting import greet; print(greet('Meera'))"
```

```text
Hello Meera, this is myapp 1.0.0
```

### 6.1 What `__init__.py` actually does

- It tells Python "this directory is a package". (Since Python 3.3, namespace packages mean
  modern Python can often work without it, but you should still create it — most tools and
  linters expect it, and it removes ambiguity.)
- Anything you put in it becomes available as `myapp.something`. Above, `VERSION` is reachable
  as `myapp.VERSION`.
- It is the place to re-export the names you want people to use, so that
  `from myapp import greet` works even though `greet` lives in `myapp.greeting`.

### 6.2 `python -m package.module` is the right way to run

The `-m` flag means "run this module **as a program**". It does two useful things: it puts the
*current folder* on the import path (so your package is found), and it sets `__name__` to
`"__main__"` so your guard fires.

Compare:

| Command | What happens |
|---|---|
| `python myapp/greeting.py` | script's folder on the path; `from myapp import VERSION` may fail |
| `python -m myapp.greeting` | current folder on the path; the guard fires |
| `python myapp` | runs `myapp/__main__.py` |

Prefer `python -m package.module` for anything inside a package.

---

## 7. `pip` — installing other people's code

**`pip`** is Python's package installer. It downloads packages from **PyPI** (the Python Package
Index) and installs them into **site-packages**, the folder on `sys.path` where Python looks for
importable third-party code.

```bash
python -m pip install requests      # install
python -m pip list                  # everything installed
python -m pip show requests         # details about one package
python -m pip install --upgrade requests
python -m pip uninstall requests
```

### 7.1 Always use `python -m pip`, not bare `pip`

This is a small habit with a big payoff.

```bash
python -m pip install requests
```

versus

```bash
pip install requests
```

They usually do the same thing — but bare `pip` might belong to a *different* Python
installation than the `python` you are running. That mismatch produces the classic
"ModuleNotFoundError: No module named 'requests'" even though you can see the package listed by
`pip list`. Using `python -m pip` guarantees the package lands in the same Python that will
import it.

### 7.2 Checking what you have

```bash
python -m pip show requests
```

```text
Name: requests
Version: 2.32.3
Summary: Python HTTP for Humans.
Home-page: https://requests.readthedocs.io
Author: Kenneth Reitz
Author-email: me@kennethreitz.org
License: Apache-2.0
Location: C:\Python313\Lib\site-packages
Requires: certifi, charset-normalizer, idna, urllib3
Required-by: cookiecutter, google-api-core, google-genai, jupyterlab_server, wikipedia
```

`Location` tells you exactly where the package was installed. `Requires` tells you what it needs
in turn — those are **transitive dependencies**, and they are why you should pin versions.
(`Required-by` lists the packages that need *this* one; it will be different on your machine.)

---

## 8. `requirements.txt`

A `requirements.txt` file lists the packages your project needs, one per line, with versions.

```text
# requirements.txt
requests==2.32.3
python-dotenv==1.0.1
tiktoken==0.7.0
```

Generate one from your current environment:

```bash
python -m pip freeze > requirements.txt
```

Install from one:

```bash
python -m pip install -r requirements.txt
```

### 8.1 The known weakness

`pip freeze` lists **every** package in your environment, including the transitive ones that you
never installed by hand. If `tiktoken` pulled in `regex`, then `regex` is in your
`requirements.txt` too — and it was never really *your* dependency.

The result is a file that is:
- **Brittle** — it pins packages you do not control, so a new release of someone else's
  dependency can break your install.
- **Noisy** — hard to tell which lines are the ones you actually chose.

The modern fix is `pyproject.toml`, described next, which lets you declare only your *direct*
dependencies and let the resolver work out the rest.

---

## 9. `pyproject.toml` — the modern way

A `pyproject.toml` file is the standard place to describe a Python project: its metadata, its
dependencies, and its tooling configuration. It lives at the root of your project.

A minimal, working example:

```toml
# pyproject.toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "my-ai-tool"
version = "0.1.0"
description = "A tiny RAG helper built while learning Python."
requires-python = ">=3.12"
dependencies = [
    "requests>=2.32",
    "tiktoken>=0.7",
]

[project.scripts]
rag-demo = "myapp.greeting:main"
```

What each part does:

| Section | Purpose |
|---|---|
| `[build-system]` | which tool builds the package (`setuptools`, `hatchling`, `poetry-core`) |
| `[project]` | the package's name, version, description, Python requirement, dependencies |
| `[project.scripts]` | command-line entry points created by `pip install` |
| `[tool.*]` | configuration for tools like `ruff`, `mypy`, `pytest` |

You will not write this from scratch often — most projects use a template generator. But you must
be able to *read* it, because it is the first thing you look at when you clone a repository.

The full treatment — build backends, lock files, `uv`, `poetry`, publishing workflows — is in
[12-environments-and-tooling.md](12-environments-and-tooling.md).

---

## 10. Virtual environments — the fix for dependency conflicts

### 10.1 The problem

Imagine two projects on your laptop:

- Project A needs `openai==1.0.0`.
- Project B needs `openai==2.5.0` (a completely different API).

Packages are installed into one shared `site-packages` folder. Install both and they overwrite
each other. Now Project A is broken, and so is B. There is no way to have both.

### 10.2 The solution

A **virtual environment** is an isolated copy of Python's package folder, stored inside your
project. Each project gets its own, so their dependencies never meet.

```text
my_project/
├── .venv/          <- created by the commands below
├── main.py
├── utils.py
└── requirements.txt
```

Create one:

```bash
python -m venv .venv
```

Activate it:

```bash
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (Command Prompt)
.venv\Scripts\activate.bat

# macOS / Linux
source .venv/bin/activate
```

Once activated, your prompt shows the environment name, and `pip` installs into it:

```text
(my_project) PS C:\Users\Aarush\my_project>
```

Deactivate with:

```bash
deactivate
```

**The one rule:** create a virtual environment for every project, and never install packages
into your system Python.

```bash
# The full, correct workflow
python -m venv .venv
.venv\Scripts\Activate.ps1        # or: source .venv/bin/activate
python -m pip install -r requirements.txt
```

Editors like VS Code can activate the environment for you — you pick the interpreter from the
status bar. Full detail, including how to pin and lock dependencies, is in
[12-environments-and-tooling.md](12-environments-and-tooling.md).

---

## 11. Installing your own project

Once your project has a `pyproject.toml`, you can install it into your active environment in
**editable mode**:

```bash
python -m pip install -e .
```

The `-e` flag means *editable*: Python adds your project folder to the import path, so your
modules are importable **and** every change you make takes effect immediately — no reinstall.

This is what solves the `ModuleNotFoundError` from section 4 permanently: after
`pip install -e .`, `import myapp` works from anywhere, in any script, without `PYTHONPATH`
hacks.

---

## 12. Publishing to PyPI

If you want other people to `pip install` your code, you publish it to **PyPI**. The process is
four steps:

1. **Create a PyPI account** at [pypi.org](https://pypi.org) and an API token for it.
2. **Write `pyproject.toml`** with your package's name, version and dependencies (section 9).
3. **Build the distribution** with the `build` tool:

   ```bash
   python -m pip install build
   python -m build
   ```

   This creates a `dist/` folder containing a source archive and a wheel.
4. **Upload it** with `twine`:

   ```bash
   python -m pip install twine
   python -m twine upload dist/*
   ```

   `twine` (not plain `pip`) is used because it checks your package metadata before uploading,
   and it talks to the secure upload endpoint.

That is the whole overview. Package naming, versioning, changelogs and release automation are
professional topics you will meet later — for now, know that the path exists and that the first
publish is the hardest.

---

## 13. Troubleshooting

### 13.1 `ModuleNotFoundError` versus `ImportError`

`ModuleNotFoundError` is a subclass of `ImportError`, and it means: *the module itself could not
be found.* Fix it with the checklist in section 4.2.

Plain `ImportError` (without the `ModuleNotFound` prefix) usually means the module **was** found,
but something inside it failed — often a name it imports that does not exist:

```python
# broken_module.py
try:
    from typing import NotARealType     # does not exist
except ImportError as error:
    # split(" (") drops the file path Python adds to the message.
    print("ImportError:", str(error).split(" (")[0])
```

```text
ImportError: cannot import name 'NotARealType' from 'typing'
```

The distinction matters: the first is a *path* problem, the second is a *code* problem.

### 13.2 Circular imports

Two modules that import each other cause a confusing error. Here are two files, `mod_one.py`
and `mod_two.py`, that import each other:

```python
# mod_one.py
from mod_two import thing_two


def thing_one():
    return "one"
```

```python
# mod_two.py
from mod_one import thing_one


def thing_two():
    return "two"
```

Importing `mod_one` makes Python start importing `mod_two`, which tries to import `mod_one`
again — but `mod_one` is only half-loaded, so `thing_one` does not exist yet.

```text
  File "mod_one.py", line 1, in <module>
    from mod_two import thing_two
  File "mod_two.py", line 1, in <module>
    from mod_one import thing_one
ImportError: cannot import name 'thing_one' from 'mod_one' (consider renaming
'C:\\Users\\Aarush\\my_project\\mod_one.py' if it has the same name as a library you
intended to import)
```

The fix is to break the cycle: move the shared code into a third module that both import, or
move the import inside the function that needs it (an import inside a function body is only
executed when that function is called, which is usually late enough to avoid the cycle).

### 13.3 Shadowing a standard-library module — the nastiest trap

Your file's folder is on `sys.path`, and it comes *before* the standard library. So if you name a
file after a standard-library module, **your file wins**.

```python
# random.py  -- in your project folder
print("!! this is MY random.py, not the standard library one")

random = "not even a module"
```

```bash
python -c "import random; print(random)"
```

```text
!! this is MY random.py, not the standard library one
<module 'random' from 'C:\\Users\\Aarush\\my_project\\random.py'>
```

Standard-library modules that people shadow by accident include `random`, `json`, `time`,
`email`, `logging`, `code`, `typing`, `queue` and `test`. If `import json` suddenly gives you
something weird, check whether you have a `json.py` in the folder you are running from.

**Fix:** rename your file. `random_data.py` is fine; `random.py` is a landmine.

### 13.4 Other errors worth recognising

| Error | Meaning |
|---|---|
| `ModuleNotFoundError: No module named 'x'` | Python cannot find `x` — path or install problem |
| `ImportError: cannot import name 'y'` | `x` was found, but `y` is not in it |
| `AttributeError: module 'x' has no attribute 'y'` | You imported the module but used the wrong name |
| `IndentationError: expected an indented block` | A `def` or `if` with no body |
| `SyntaxError: invalid syntax` | Usually a missing colon or a wrong keyword |

---

## 🧪 Try it yourself

### Exercise 1 — Split a program in two

Create a folder with `math_helpers.py` and `app.py`:

`math_helpers.py`:

```python
# math_helpers.py
def average(numbers):
    """Return the mean of a list of numbers."""
    return sum(numbers) / len(numbers)


def median(numbers):
    """Return the middle value of a sorted list of numbers."""
    ordered = sorted(numbers)
    middle = len(ordered) // 2
    if len(ordered) % 2 == 1:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2
```

`app.py`:

```python
# app.py
from math_helpers import average, median

scores = [10, 20, 30, 40, 50]

print("average:", average(scores))
print("median:", median(scores))
```

Run `python app.py` from inside the folder. What is printed?

<details>
<summary>Hint</summary>

`average` divides the sum by the count. `median` sorts the list first.
</details>

<details>
<summary>Solution</summary>

```text
average: 30.0
median: 30
```

Because there are five scores, the median is the middle one — `ordered[2]`, which is `30`. The
average of `10, 20, 30, 40, 50` is `150 / 5 = 30.0` (a float, because `/` always produces one).
</details>

### Exercise 2 — Add the guard

Now edit `app.py` so that the `print` calls only happen when the file is run directly, and the
module still works when imported. Then test both:

```bash
python app.py
python -c "import app"
```

<details>
<summary>Hint</summary>

Wrap the printing in a `main()` function and call it from inside the guard.
</details>

<details>
<summary>Solution</summary>

```python
# app.py
from math_helpers import average, median

scores = [10, 20, 30, 40, 50]


def main():
    print("average:", average(scores))
    print("median:", median(scores))


if __name__ == "__main__":
    main()
```

```text
average: 30.0
median: 30
```

The second command prints nothing at all — importing `app` defines `main` but does not call it.
</details>

### Exercise 3 — Find the shadowing bug

You have a project folder containing `json.py`:

```python
# json.py
print("my own json module")
```

and `app.py`:

```python
import json

print(json.__name__)
```

What happens when you run `python app.py`, and why?

<details>
<summary>Hint</summary>

Your folder comes before the standard library on `sys.path`.
</details>

<details>
<summary>Solution</summary>

```text
my own json module
json
```

Your `json.py` shadows the standard library's `json` module, so `import json` loads *your* file.
The fix is to rename your file — `json_helpers.py` — and update the import.
</details>

### Exercise 4 — Build a package

Create this structure:

```text
toolbox/
├── __init__.py
└── strings.py
```

`toolbox/__init__.py`:

```python
VERSION = "0.1.0"
```

`toolbox/strings.py`:

```python
def title_case(text):
    """Return the text with every word capitalised."""
    return " ".join(word.capitalize() for word in text.split())


def word_count(text):
    """Return how many words the text contains."""
    return len(text.split())
```

Then run `python -c "from toolbox.strings import title_case; print(title_case('hello ai engineers'))"`.

<details>
<summary>Hint</summary>

`capitalize()` upper-cases the first letter and lower-cases the rest. `split()` with no argument
splits on any whitespace.
</details>

<details>
<summary>Solution</summary>

```text
Hello Ai Engineers
```

And `from toolbox.strings import word_count; print(word_count('hello ai engineers'))` gives:

```text
3
```

Note that `from toolbox.strings import title_case` had to reach *through* the package to get to
the module. That is the difference between a package and a loose collection of files: the
package name is the outer namespace, and the module name is the inner one.
</details>

### Exercise 5 — Diagnose the failure

You have:

```text
project/
├── helpers.py
└── src/
    └── runner.py
```

`helpers.py` contains `NAME = "project"` and `src/runner.py` contains:

```python
# src/runner.py [expected-failure] -- this file FAILS to run, and that is the whole point of the exercise
import helpers

print(helpers.NAME)
```

You run `python src/runner.py` from the `project/` folder and get
`ModuleNotFoundError: No module named 'helpers'`. Explain why, and give two different fixes.

<details>
<summary>Hint</summary>

`sys.path[0]` is the folder of the *script*, not the folder you are standing in.
</details>

<details>
<summary>Solution</summary>

Python adds `project/src/` to `sys.path` when you run `python src/runner.py`, because that is
where the script lives. `helpers.py` is in `project/`, one level up, so Python never looks
there.

Two fixes:

1. **Set `PYTHONPATH`** to the project folder:

   ```bash
   # Windows (PowerShell)
   $env:PYTHONPATH = "C:\Users\Aarush\project"
   python src\runner.py
   ```

2. **Install the project** with a `pyproject.toml` and `python -m pip install -e .`, which puts
   the project root on the import path permanently.

A third, worse option is to move `helpers.py` into `src/`, so it sits next to `runner.py` — but
that couples your library code to your script layout.
</details>

---

## ✅ Checkpoint

**1. What is the difference between a module and a package?**

<details>
<summary>Answer</summary>

A module is a single `.py` file. A package is a directory of modules that Python treats as one
importable unit, normally containing an `__init__.py`.
</details>

**2. What is the value of `__name__` when a file is run directly, and when it is imported?**

<details>
<summary>Answer</summary>

`"__main__"` when run directly (`python file.py`), and the module's own name when imported
(`"helpers"` for `import helpers`).
</details>

**3. Why do we use `if __name__ == "__main__":`?**

<details>
<summary>Answer</summary>

So the module's top-level code runs only when the file is executed as a program, and not when
it is imported by other code. Without it, importing a module would run all of its side effects.
</details>

**4. What is `sys.path`?**

<details>
<summary>Answer</summary>

The list of folders Python searches when you `import` something. It includes the script's own
folder and `site-packages` (where `pip` installs packages).
</details>

**5. What causes `ModuleNotFoundError`?**

<details>
<summary>Answer</summary>

Python searched every folder in `sys.path` and could not find the module — usually a wrong file
name, a wrong location, the wrong working directory, or simply not installing the package.
</details>

**6. Why prefer `python -m pip install X` over `pip install X`?**

<details>
<summary>Answer</summary>

`python -m pip` guarantees the package is installed into the same Python installation that will
import it, avoiding the mismatch between multiple Python installations on one machine.
</details>

**7. What does `pip freeze > requirements.txt` do, and what is wrong with it?**

<details>
<summary>Answer</summary>

It writes every installed package and its version to `requirements.txt`. The problem is that it
includes transitive dependencies you never chose, which makes the file brittle and noisy.
</details>

**8. What problem do virtual environments solve?**

<details>
<summary>Answer</summary>

They give each project its own isolated set of packages, so two projects can require different
versions of the same library without conflicting.
</details>

**9. What is the danger of naming your own file `random.py`?**

<details>
<summary>Answer</summary>

Your folder comes before the standard library on `sys.path`, so `import random` will load your
file instead of the standard library's — breaking any library that imports `random`.
</details>

---

## 🐛 Common mistakes

| Mistake | What you see | Fix |
|---|---|---|
| Running `python app/run.py` from the wrong folder | `ModuleNotFoundError: No module named 'config'` | Run from the project root, or set `PYTHONPATH`, or `pip install -e .` |
| Naming a file after a stdlib module (`random.py`, `json.py`) | `import random` gives your file; libraries break | Rename the file (`random_data.py`) |
| Forgetting `if __name__ == "__main__":` | Importing a module runs the whole program | Wrap the top-level code in a `main()` function and call it from the guard |
| Using bare `pip install` | Package installed to the wrong Python; `ModuleNotFoundError` anyway | Always use `python -m pip install` |
| A file saved as `utils.py.txt` | `ModuleNotFoundError` even though the file is there | Enable file extensions in Explorer; check the real name |
| Import name does not match the file name (`import Utilis`) | `ModuleNotFoundError` | Python is case-sensitive; match exactly |
| Importing a package before installing it | `ModuleNotFoundError` | `python -m pip install <package>` inside your virtual environment |
| Running `python myapp/greeting.py` | `ModuleNotFoundError: No module named 'myapp'` | Use `python -m myapp.greeting` from the folder containing `myapp/` |
| Two modules importing each other | `ImportError: partially initialized module` | Break the cycle: extract shared code, or move the import inside a function |
| Installing packages into the system Python | One project breaks another | Use a virtual environment per project |
| `from x import y` when the name is ambiguous | Hard-to-find name collisions later | Prefer `import x` and call `x.y()` |
| Editing an installed package in `site-packages` | Your changes vanish on reinstall | Use `pip install -e .` for your own code |

---

## 🔗 Resources

- [The Python Tutorial: Modules](https://docs.python.org/3/tutorial/modules.html) — the official
  introduction to modules, packages, and `__name__`.
- [The import system](https://docs.python.org/3/reference/import.html) — the language reference for
  how Python finds and loads modules.
- [Importing the right things](https://docs.python.org/3/reference/import.html#importing-the-right-things)
  — the rules that decide whether `import x` binds `x` or its contents.
- [Using Python on Windows](https://docs.python.org/3/using/windows.html) — where everything gets
  installed on Windows, and how `PYTHONPATH` works there.
- [venv — Creation of virtual environments](https://docs.python.org/3/library/venv.html) — the
  official documentation for `python -m venv`.
- [pip — The Python package installer](https://pip.pypa.io/en/latest/getting-started/) — pip's own
  documentation, covering `install -r` and `install -e`.
- [Installing Python Packages](https://packaging.python.org/en/latest/tutorials/installing-packages/)
  and [Managing Application Dependencies](https://packaging.python.org/en/latest/tutorials/managing-dependencies/)
  — the official Python Packaging User Guide on installing and pinning dependencies.
- [Writing a `pyproject.toml`](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)
  — the canonical guide to project metadata and dependencies.
- [Packaging Python Projects](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
  — the step-by-step guide to building and publishing your own package.
- [PyPI — the Python Package Index](https://pypi.org/) — where every third-party package lives.
- [PyPI: `build`](https://pypi.org/project/build/) and [PyPI: `twine`](https://pypi.org/project/twine/) —
  the two tools you need to publish a package.
- [Virtual environments: the guide](https://realpython.com/python-virtual-environments-a-primer/) —
  a community walkthrough of why and how to use `venv`.

---

## ➡️ Next

- [09 File I/O and errors](09-file-io-and-errors.md) — read and write files, handle exceptions
  properly, and stop your programs from crashing.

**← Previous:** [07 Comprehensions and iterators](07-comprehensions-and-iterators.md)
