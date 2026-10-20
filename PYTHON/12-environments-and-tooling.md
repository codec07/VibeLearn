# Environments and Tooling

So far you have been writing Python in whatever environment your computer happened to give
you. That works until the day it does not: you install a package for one project, and
suddenly a completely different project stops working. This file is about the set of
tools that professional Python teams use so that every project — and every teammate —
gets exactly the same code, the same packages, and the same checks. It covers virtual
environments, `pip`, `pyproject.toml`, the fast new tool `uv`, the linter `ruff`, the
type checker `mypy`, `pre-commit`, and the two files you will see in almost every modern
repository: `.gitignore` and `.env`.

> **⏱️ Time:** ~30 minutes
> **📚 Prereqs:** [11 — Type hints and modern Python](11-type-hints-and-modern-python.md)
> **🎯 By the end you can:** Set up a complete, reproducible Python project with an isolated
> environment, a `pyproject.toml`, pinned dependencies, automatic formatting, type checking and
> pre-commit hooks — the exact setup an AI/ML team expects to see in a pull request.

---

## Why this matters for AI engineering

Every serious AI project pulls in dozens of libraries: an LLM SDK, a vector database client,
a web framework, a tokenizer, a test runner, and usually a heavyweight one like PyTorch or
`transformers`. These libraries fight each other constantly — one wants `pydantic` 1.x, another
wants 2.x; one needs `numpy` 1.24, another needs 2.x. When two projects share one global
install of Python packages, one of them always breaks.

Environment and tooling files are the fix, and in an AI codebase they show up on line one of
every pull request. When you join a team that ships LLM features, the reviewer of your PR will
look for exactly the same files you are about to write: `pyproject.toml`, a lock file, a
`.gitignore`, a `.env.example`, linting, type checking and a test suite that runs on every
commit.

---

## 1. The problem environments solve

Here is the situation, concretely.

You are working on **Project A**, a document summariser. It needs `langchain 0.1`, which needs
`pydantic < 3`. You install it:

```bash
python -m pip install langchain
```

Two weeks later you start **Project B**, a structured-output service. The latest `langchain`
requires `pydantic >= 3` (hypothetically). You install it into the *same* Python installation:

```bash
python -m pip install langchain --upgrade
```

Now `pydantic` was upgraded globally. Project A now crashes on import, on a machine you are not
even working on. And to make it worse, Project A worked perfectly yesterday, and you did not
change any of its code.

The root cause is that "the Python installation" is a **single shared folder of packages**. A
*virtual environment* fixes this by giving each project its own private copy of that folder:

```text
Your computer
└── C:\Python313\              <- the base Python (never install project packages here)
    ├── my_project_a/
    │   └── .venv/             <- Project A's private packages
    │       └── Lib/site-packages/
    │           ├── pydantic/  <- version 2.8
    │           └── langchain/
    └── my_project_b/
        └── .venv/             <- Project B's private packages
            └── Lib/site-packages/
                ├── pydantic/  <- version 3.1
                └── langchain/
```

A **virtual environment** is a folder that contains its own copy of the Python *interpreter
shim* and its own `site-packages` directory. When you "activate" it, your shell is pointed at
that private copy, so `python` and `pip` resolve to it instead of the system one.

Two rules follow from this and they are the whole discipline:

1. Never install project packages into the base Python installation.
2. One virtual environment per project.

---

## 2. Virtual environments with `venv`

`venv` is in the Python standard library. There is nothing to install.

```bash
cd my-project
python -m venv .venv
```

That creates a folder called `.venv` in your project. The leading dot is a convention: it hides
the folder in `ls` output on macOS/Linux and marks it as "internal" to the project.

### Activating the environment

Activation is what points your terminal at the private copy of Python.

```bash
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# Windows (Command Prompt / cmd.exe)
.venv\Scripts\activate.bat

# macOS and Linux
source .venv/bin/activate
```

Your prompt changes to show the environment name, and `python` now resolves to the private one:

```text
(my-project) C:\Users\you\my-project> python --version
Python 3.13.1
```

### Confirming you are really in the environment

Do not trust the prompt. Ask the interpreter directly:

```bash
# Windows
where python

# macOS / Linux
which python
```

Both print the *full path* of the interpreter being used. If it contains `.venv`, you are
inside the environment. You can also ask Python itself:

```python
import sys

print(sys.executable)          # the full path of the running interpreter
print(sys.prefix)              # .../my-project/.venv
print(sys.base_prefix)         # .../Python313  <- the real Python

in_venv = sys.prefix != sys.base_prefix
print(f"Running inside a virtual environment: {in_venv}")
```

```text
C:\Users\you\my-project\.venv\Scripts\python.exe
C:\Users\you\my-project\.venv
C:\Python313
Running inside a virtual environment: True
```

### The Windows PowerShell execution-policy error

This is the single most common thing that goes wrong on Windows, and it looks alarming:

```text
.\.venv\Scripts\Activate.ps1
File C:\Users\you\my-project\.venv\Scripts\Activate.ps1 cannot be loaded because running
scripts is disabled on this system. For more information, see about_Execution_Policies at
https://go.microsoft.com/fwlink/?LinkID=135170.
    + CategoryInfo          : SecurityError: (:) [], PSSecurityException
    + FullyQualifiedErrorId : UnauthorizedAccess
```

PowerShell refuses to run local scripts by default on many Windows installations. Two fixes:

**Fix A — allow scripts for your current user only (recommended).** Open PowerShell (not
elevated) and run:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

`RemoteSigned` means "run local scripts freely, but scripts downloaded from the internet must
be signed". That is a sensible middle ground and it affects only your user account.

**Fix B — bypass the policy for one command.** If you cannot change the policy (some managed
work machines), just call the interpreter directly and skip activation entirely:

```powershell
.\.venv\Scripts\python.exe -m pip install pytest
```

This works exactly the same, it just means you type the full path every time. Many people
simply set the environment variable `VIRTUAL_ENV` in their IDE instead.

### Turning the environment off

```bash
deactivate
```

The prompt loses its `(my-project)` prefix and `python` goes back to the system one. You can
always re-activate later with the same command.

### The VS Code workflow

Visual Studio Code can manage this for you, which removes the activation step entirely.

1. Open the project folder in VS Code.
2. Press `Ctrl+Shift+P` (macOS: `Cmd+Shift+P`) to open the command palette.
3. Type **Python: Select Interpreter** and press Enter.
4. Pick the entry that looks like `./.venv/Scripts/python.exe` (Windows) or
   `./.venv/bin/python` (macOS/Linux). If it is not listed, choose **Enter interpreter
   path** and point at the file manually.
5. VS Code now uses that interpreter for every "Run Python File" and terminal you open.

With this done, you never type `Activate.ps1` again — the terminal inside VS Code starts in
the environment automatically.

---

## 3. `pip` essentials

`pip` is the package installer. It downloads packages from PyPI (the Python Package Index) and
unpacks them into the `site-packages` folder of whichever interpreter it is attached to.

### Always use `python -m pip`

Compare these two commands:

```bash
pip install requests
python -m pip install requests
```

They are *usually* the same, but not always. Bare `pip` is whatever `pip.exe`/`pip` happens to
be first on your `PATH` — which might belong to a different Python, a different virtual
environment, or a different tool entirely. `python -m pip` guarantees that the package is
installed into *the same Python that is about to run your code*, because `-m` means "run this
module using this interpreter". Use `python -m pip` and the class of bug disappears.

### The commands you will actually use

| Command | What it does |
|---|---|
| `python -m pip install requests` | install a package (latest version) |
| `python -m pip install "requests==2.32.3"` | install one exact version |
| `python -m pip install -r requirements.txt` | install everything listed in a file |
| `python -m pip install -U requests` | upgrade to the newest version (`--upgrade`) |
| `python -m pip list` | show every installed package and its version |
| `python -m pip show requests` | show details about one package (version, location, requires) |
| `python -m pip uninstall requests` | remove a package (asks for confirmation) |
| `python -m pip freeze` | print the installed packages as a requirements file |
| `python -m pip check` | verify that no installed package has broken dependencies |
| `python -m pip download requests -d ./wheels` | download wheels without installing them |

`freeze` and `list` look similar but differ in purpose. `list` shows *everything*, including
packages pip itself installed as dependencies. `freeze` shows only the top-level packages you
asked for, in the exact format `requirements.txt` expects, and it deliberately omits packages
that were pulled in as dependencies.

`python -m pip check` is worth running after a messy install. It prints something like:

```text
No broken requirements found.
```

or, if a dependency conflict exists:

```text
langchain 0.1.0 has requirement pydantic<3,>=2, but you have pydantic 3.1.0 which is incompatible.
```

---

## 4. `pyproject.toml` — the modern project manifest

A **manifest** is a file that describes a project: its name, version, what it needs to run.
For many years that was `setup.py` (a Python script) and `setup.cfg` (INI format). Both are
now legacy. The single modern file is `pyproject.toml`, and `tomllib` is in the standard
library so Python can read it.

Here is a complete, annotated example:

```toml
# pyproject.toml

[build-system]
# How to build and install this project. Modern Python uses a build backend
# (setuptools) driven by a PEP 517 hook.
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "doc-summariser"           # the name on PyPI; lowercase, dashes
version = "0.1.0"                 # your own version number
description = "Summarise long documents with an LLM."
readme = "README.md"              # the long description shown on PyPI
requires-python = ">=3.12"        # which Python versions are supported
license = { text = "MIT" }        # or license = "MIT" (PEP 639 style)
authors = [
    { name = "Aarush", email = "you@example.com" },
]
keywords = ["llm", "summarisation", "nlp"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Programming Language :: Python :: 3.12",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
]

dependencies = [
    "httpx>=0.27,<1.0",           # required to run
    "pydantic>=2.7,<3.0",
]

[project.optional-dependencies]
# Optional extras, installed with: pip install -e ".[dev]"
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "ruff>=0.6",
    "mypy>=1.11",
]
ai = [
    "openai>=1.40",
    "tiktoken>=0.7",
]

[project.urls]
Homepage = "https://github.com/your-name/doc-summariser"
Repository = "https://github.com/your-name/doc-summariser"
Issues = "https://github.com/your-name/doc-summariser/issues"

[project.scripts]
# Creates a `docsum` command on your PATH once the package is installed.
docsum = "doc_summariser.cli:main"

[tool.setuptools.packages.find]
where = ["src"]                   # src/ layout (see section 9)
```

Two things to understand here:

- **The `[project]` table** is standardised by PEP 621. Every modern Python packaging tool
  (setuptools, Poetry, uv, Hatch, PDM) understands it.
- **The `[build-system]` table** declares which tool builds the project and which version of
  that tool is needed. `setuptools` is still the default, but you can swap in `hatchling`
  or `poetry-core` without changing anything else in the file.

### Read it from Python

`tomllib` is in the standard library from Python 3.11 onwards, so you can inspect your own
project metadata programmatically:

```python
import tomllib
from pathlib import Path

# This reads the pyproject.toml of the project you are sitting in.
# If you are not inside a project folder, a sample is written so you can follow along.
path = Path("pyproject.toml")
if not path.exists():
    path.write_text(
        '[project]\n'
        'name = "doc-summariser"\n'
        'version = "0.1.0"\n'
        'requires-python = ">=3.12"\n'
        'dependencies = ["httpx>=0.27,<1.0", "pydantic>=2.7,<3.0"]\n'
        '\n'
        '[project.optional-dependencies]\n'
        'dev = ["pytest>=8.0", "pytest-cov>=5.0", "ruff>=0.6", "mypy>=1.11"]\n',
        encoding="utf-8",
    )

config = tomllib.loads(path.read_text(encoding="utf-8"))
project = config["project"]

print(f"Name:        {project['name']}")
print(f"Version:     {project['version']}")
print(f"Python:      {project['requires-python']}")
print(f"Runtime deps: {project['dependencies']}")
print(f"Dev extras:  {project['optional-dependencies']['dev']}")
```

```text
Name:        doc-summariser
Version:     0.1.0
Python:      >=3.12
Runtime deps: ['httpx>=0.27,<1.0', 'pydantic>=2.7,<3.0']
Dev extras:  ['pytest>=8.0', 'pytest-cov>=5.0', 'ruff>=0.6', 'mypy>=1.11']
```

### Inspecting what is installed

`importlib.metadata` is the standard-library way to ask "what version of this package is
installed?" — the same information `pip list` shows, but from inside your program:

```python
from importlib.metadata import version, PackageNotFoundError

for name in ("httpx", "pytest", "definitely-not-a-real-package"):
    try:
        print(f"{name}: {version(name)}")
    except PackageNotFoundError:
        print(f"{name}: not installed")
```

```text
httpx: 0.28.1
pytest: 9.1.1
definitely-not-a-real-package: not installed
```

---

## 5. How to specify dependency versions

The version specifier is the part of the requirement string after the package name.

| Specifier | Means | Use it when |
|---|---|---|
| `httpx` | any version at all | almost never in a real project |
| `httpx>=0.27` | 0.27 or newer | a floor: you need a feature added in 0.27 |
| `httpx>0.27` | strictly newer than 0.27 | rarely — `<` and `>=` are clearer |
| `httpx!=0.28.0` | anything except that one version | you hit a bug in a single release |
| `httpx==0.28.1` | exactly this version | libraries, lock files, CI |
| `httpx~=0.27.2` | `>=0.27.2` and `==0.27.*` | applications: allow patches, block minors |

The `~=` operator is called **compatible release**. `~=0.27.2` means "at least 0.27.2, but
not 0.28.0" — it allows the patch and minor work within the same minor version. `~=0.27`
means "at least 0.27, but not 1.0".

### Pin or not pin?

This is the rule that confuses people most, and the answer depends on whether you are writing
an **application** or a **library**.

- **Applications** (a service, a script, a chatbot): do **not** pin exact versions in
  `pyproject.toml`. Write ranges like `httpx>=0.27,<1.0`. Pinning `httpx==0.28.1` means your
  project silently stops installing the day a security fix lands in 0.28.2 — and when a new
  teammate clones the repo they get a different environment from yours. Ranges let pip pick a
  working combination; the **lock file** provides the reproducibility.

- **Libraries** (something other people will import): you should pin tightly, or at least
  pin a floor and a ceiling. A library that says `httpx>=0.27` with no upper bound can be
  broken by a future `httpx 1.0`. Use `httpx>=0.27,<1.0` so your users get a compatible
  range and your test matrix covers it.

The reasoning: pinning in the manifest says "this is what I develop against". Reproducibility
comes from the lock file, which pins *everything transitively* at the moment you install.

---

## 6. Lock files — reproducibility

A **lock file** is an auto-generated file that records the *exact* version of every package in
your dependency tree, including the ones you never asked for.

```text
pyproject.toml     "I need httpx>=0.27,<1.0 and pydantic>=2.7,<3.0"   <- you write this
lock file          "httpx 0.28.1, h11 0.16.0, httpcore 1.0.9, pydantic 2.9.2, ..."  <- tool writes this
```

With a lock file, `pip install .` (or `uv sync`) gives every developer and every CI run the
*identical* environment. That is what "reproducible build" means in practice.

The three common tools:

| Tool | Lock file | Notes |
|---|---|---|
| `uv` | `uv.lock` | fastest; also manages Python versions and venvs |
| `Poetry` | `poetry.lock` | mature, its own installer |
| `pip-tools` | `requirements.txt` (pinned) | keeps the classic workflow; `pip-compile` |

A pip-tools workflow looks like this:

```bash
# requirements.in holds your loose ranges; requirements.txt is generated and pinned
python -m pip install pip-tools
pip-compile requirements.in          # -> requirements.txt with exact versions
pip-sync requirements.txt            # make the venv match it exactly
```

---

## 7. `uv` — the modern tool

`uv` is a very fast, Rust-written replacement for `pip`, `venv` and `pyenv` in one binary. It
is the tool new Python teams are standardising on in 2025 and 2026, and it is worth learning
even if you keep using `pip` day to day.

Three commands cover ninety percent of what you need:

```bash
# 1. Create a project: venv + pyproject.toml + lock file, all at once
uv init my-project
cd my-project

# 2. Add dependencies (it edits pyproject.toml AND updates the lock file)
uv add httpx pydantic
uv add --dev pytest ruff mypy

# 3. Sync the environment to match the lock file exactly
uv sync
```

That is it. `uv init` creates the `src/` layout, a `.gitignore`, and a `pyproject.toml` with
the right `[build-system]`. `uv add` writes the dependency into `pyproject.toml` with a
sensible version range. `uv sync` installs exactly what the lock file says, in seconds rather
than tens of seconds.

Other useful commands:

```bash
uv run pytest                 # run a command inside the synced environment
uv run python -m mypackage    # run your code with the right interpreter
uv python install 3.12        # install a specific Python version (no python.org needed)
uv lock --upgrade-package httpx   # deliberately move one dependency forward
```

Because `uv` is written in Rust, resolving and installing is usually 10-100x faster than
`pip`. On a machine where `pip install` takes 40 seconds, `uv sync` typically takes 2.

---

## 8. `pipx` — installing command line tools

`pipx` installs **command line applications** into their own isolated virtual environment,
while leaving your main environment (and your project's environment) untouched.

```bash
pipx install ruff        # installs the `ruff` command
pipx install httpie     # installs the `http` command
pipx list               # show everything installed this way
pipx upgrade ruff       # upgrade it
```

Why not `pip install ruff`? Because a linter or a formatter often needs a specific version of
a dependency, and installing it globally can break other tools. `pipx` gives each CLI tool
its own private environment.

`pipx install` and `uv tool install` do the same job; `uv tool install ruff` is the faster
route if you already use `uv`.

---

## 9. `ruff` — the modern linter and formatter

`ruff` is a single fast binary that replaces three older tools at once:

| Old tool | What it did | Ruff equivalent |
|---|---|---|
| `flake8` | linting (find bugs, style) | `ruff check` |
| `black` | code formatting | `ruff format` |
| `isort` | sorting imports | `ruff check --select I --fix` |

It is written in Rust and is typically 10-100x faster than the tools it replaces.

```bash
python -m pip install ruff      # or: uv add --dev ruff
```

### The four commands

```bash
ruff check .                  # lint the whole project, report problems
ruff check --fix .            # lint and auto-fix what can be fixed safely
ruff format .                 # format every file the way black would
ruff format --check .         # check formatting without changing files (used in CI)
```

### Configuration

Ruff is configured inside `pyproject.toml`, under a `[tool.ruff]` table:

```toml
[tool.ruff]
line-length = 88
target-version = "py312"
extend-exclude = ["data", ".venv"]

[tool.ruff.lint]
# E/W = pycodestyle errors, F = pyflakes, I = isort, UP = pyupgrade, B = bugbear
select = ["E", "F", "I", "UP", "B", "SIM"]
ignore = ["E501"]             # E501 is line-too-long; ruff's formatter handles that

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["S101"]         # allow assert in tests even with the S (bandit) rules

[tool.ruff.lint.isort]
known-first-party = ["doc_summariser"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

Then in CI you run:

```bash
ruff check . && ruff format --check .
```

Two commands, and a reviewer knows your code matches the house style without reading it.

---

## 10. `black` and `isort` — still fine, but superseded

`black` (by the same author as `ruff`) was the formatter that made "format your code
automatically" mainstream. It is still widely used and still works:

```bash
python -m pip install black
black .
```

But it does not lint, it does not sort imports, and it is much slower than `ruff format`.
`isort` sorts your imports; `ruff` does that too, with the `I` rules enabled.

Practical advice for a beginner in 2026: learn `ruff` first, and treat `black` as something
you may meet in an older repository. You do not need to unlearn anything.

---

## 11. `mypy` — static type checking

`mypy` is a **static type checker**: it reads your source code without running it and reports
places where the types cannot possibly line up. You met annotations in
[11 — Type hints and modern Python](11-type-hints-and-modern-python.md); `mypy` is the tool
that acts on them.

```bash
python -m pip install mypy
```

Configure it in `pyproject.toml`:

```toml
[tool.mypy]
python_version = "3.12"
strict = true                  # turns on the full set of strict checks
warn_unused_ignores = true     # "# type: ignore" that is not needed is an error
warn_return_any = true
show_error_codes = true
```

`strict = true` enables the important ones, including `disallow_untyped_defs` (every function
needs annotations) and `disallow_any_generics` (list is fine, `list[Any]` must be written out).

Run it:

```bash
mypy src/            # check a package
mypy .               # check everything
mypy --strict app.py # strict mode for a single file, without config
```

A typical report looks like this:

```text
src/doc_summariser/client.py:42: error: Argument 1 to "summarise" has incompatible type "list[str]"; expected "Sequence[str]"  [arg-type]
Found 1 error in 1 file (checked 12 source files)
```

---

## 12. `pre-commit` — checks on every commit

**`pre-commit` is a framework for running checks automatically before each git commit.** It is
the single highest-value piece of tooling in this file, because it means *you cannot
accidentally commit broken code*.

Typical checks: trailing whitespace, a missing newline at end of file, `ruff check`,
`ruff format --check`, `mypy`, and a check that you did not commit secrets or huge files.

Install it and hook it into git:

```bash
python -m pip install pre-commit
pre-commit install     # writes a small script into .git/hooks/
```

Now define which checks to run in `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-toml
      - id: check-added-large-files
      - id: detect-private-key

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.4
    hooks:
      - id: ruff-check
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.13.0
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]
```

The `rev` is a pinned tag — the exact version of the hook to use. `pre-commit` caches these
environments, so the first run is slow and later runs are fast.

Now, every time you run `git commit`, `pre-commit` runs the hooks. If `ruff` reformats a
file, the commit **fails** and tells you to `git add` the reformatted file and commit again.
That tiny friction is what keeps a shared codebase consistent.

```bash
pre-commit run --all-files   # run every hook over the whole repo right now
pre-commit autoupdate        # bump the rev numbers to newer versions
```

---

## 13. `.gitignore` for Python

**`.gitignore` lists files git should never track.** Git still remembers files it has already
committed until you remove them from the index, so this file matters most at the start of a
project.

Here is the standard Python `.gitignore` you can copy:

```gitignore
# Virtual environments
.venv/
venv/
env/

# Bytecode and caches
__pycache__/
*.py[cod]
*$py.class
.mypy_cache/
.pytest_cache/
.ruff_cache/
.tox/
.nox/

# Packaging and build output
build/
dist/
*.egg-info/
.eggs/

# Environments and secrets
.env
.env.*
!.env.example

# Editors and OS noise
.vscode/
.idea/
.DS_Store
Thumbs.db

# Coverage and test output
.coverage
.coverage.*
htmlcov/
coverage.xml
```

Note the two lines that are easy to get wrong:

```gitignore
.env
!.env.example
```

The first ignores every `.env` file (your real secrets). The second says "…except
`.env.example`", which is the *template* file that is safe to commit because it contains no
real values.

---

## 14. `.env` files and `python-dotenv`

A **secret** is a value that must never be committed or printed: an API key, a database
password, a webhook signing secret. A **config value** is a setting that is not secret: the
log level, the model name, a timeout, the port number.

| | Secret | Config value |
|---|---|---|
| Example | `OPENAI_API_KEY=sk-abc123...` | `LOG_LEVEL=info` |
| Where it lives | `.env` (gitignored) + a secret manager | `.env` or your own config file |
| In the repo | never | sometimes, if it is not sensitive |
| In code | read from the environment | read from the environment or a config object |

The rule of thumb: **if leaking it would cost money, access or trust, it is a secret.**

### The `.env` file

```bash
# .env  (gitignored - never commit this)
OPENAI_API_KEY=sk-proj-abc123def456
DATABASE_URL=postgresql://localhost:5432/app
LOG_LEVEL=info
```

```bash
# .env.example  (committed - this is the template)
OPENAI_API_KEY=sk-proj-your-key-here
DATABASE_URL=postgresql://localhost:5432/app
LOG_LEVEL=info
```

New teammates copy `.env.example` to `.env` and fill in their own secrets.

### Reading them in Python

The `python-dotenv` package loads `.env` into your process's environment variables:

```bash
python -m pip install python-dotenv
```

```python
from dotenv import load_dotenv
import os

load_dotenv()  # reads .env from the current directory; no error if it is missing

api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    # In a real CLI you would use: raise SystemExit("OPENAI_API_KEY is not set.")
    print("OPENAI_API_KEY is not set - copy .env.example to .env and fill it in.")
else:
    print(f"Key starts with: {api_key[:7]}...")

print(f"Log level: {os.environ.get('LOG_LEVEL', 'info')}")
```

```text
OPENAI_API_KEY is not set - copy .env.example to .env and fill it in.
Log level: info
```

With a real `.env` present, the first line becomes:

```text
Key starts with: sk-proj-...
Log level: info
```

In production you do not use a `.env` file at all — you set real environment variables in
your deployment platform (Heroku, Fly.io, Kubernetes, AWS). The code is identical because it
only ever calls `os.environ.get(...)`.

---

## 15. A realistic modern Python project skeleton

Here is what a well-organised Python repository looks like in 2026 — the *src layout*, where
your importable code lives inside `src/` so it can never accidentally import from the working
directory:

```text
doc-summariser/
├── .github/
│   └── workflows/
│       └── ci.yml              # runs pytest + ruff + mypy on every push
├── src/
│   └── doc_summariser/
│       ├── __init__.py
│       ├── cli.py              # the command line entry point
│       ├── client.py           # talks to the LLM API
│       ├── config.py           # reads settings from the environment
│       └── summariser.py       # the actual business logic
├── tests/
│   ├── conftest.py             # shared fixtures
│   ├── test_client.py
│   └── test_summariser.py
├── .env.example                # template of config, no secrets
├── .gitignore
├── .pre-commit-config.yaml
├── README.md
├── pyproject.toml              # name, version, dependencies, tool config
└── uv.lock                     # exact versions of everything
```

Why `src/`? Because with `src/` layout, `import doc_summariser` only works if the package is
*installed* (which is what `pip install -e .` does). Without it, Python happily imports the
folder sitting in your current directory, and your tests pass locally but fail in CI where
nothing is installed. The `src/` layout removes that whole class of confusion.

---

## 16. My first modern Python project — eight steps

Let us build that skeleton from nothing. Assume a fresh terminal in an empty folder.

**Step 1 — Create the folder and the virtual environment.**

```bash
mkdir doc-summariser
cd doc-summariser
python -m venv .venv
```

Activate it (`.\.venv\Scripts\Activate.ps1` on Windows, `source .venv/bin/activate` on
macOS/Linux).

**Step 2 — Create the source layout.**

```bash
mkdir src\doc_summariser
mkdir tests
mkdir .github\workflows
```

Windows PowerShell needs `mkdir src\doc_summariser` as a single argument or
`mkdir src/doc_summariser` — either works in PowerShell 7.

**Step 3 — Write `pyproject.toml`.**

Copy the annotated example from section 4 and adjust the name, description and dependencies.
Minimum viable version:

```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "doc-summariser"
version = "0.1.0"
description = "Summarise long documents with an LLM."
requires-python = ">=3.12"
dependencies = ["httpx>=0.27,<1.0"]

[project.optional-dependencies]
dev = ["pytest>=8.0", "ruff>=0.6", "mypy>=1.11"]

[tool.ruff]
line-length = 88
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]

[tool.mypy]
python_version = "3.12"
strict = true

[tool.pytest.ini_options]
testpaths = ["tests"]
```

**Step 4 — Write two small files and install the package in editable mode.**

```python
# src/doc_summariser/__init__.py
"""Doc summariser package."""

__version__ = "0.1.0"
```

```python
# src/doc_summariser/__main__.py
"""Let the package be run directly with: python -m doc_summariser"""
from doc_summariser import __version__

if __name__ == "__main__":
    print(f"doc-summariser {__version__}")
```

```bash
python -m pip install -e ".[dev]"
```

```text
$ python -m doc_summariser
doc-summariser 0.1.0
```

The `-e` flag means *editable*: changes to your source take effect immediately, without
reinstalling.

**Step 5 — Write one test.**

```python
# tests/test_version.py
from doc_summariser import __version__


def test_version_is_a_string():
    assert isinstance(__version__, str)
    assert __version__.count(".") == 2
```

**Step 6 — Run the test.**

```bash
python -m pytest
```

```text
============================= test session starts ==============================
collected 1 item

tests/test_version.py .                                          [100%]

============================== 1 passed in 0.12s ==============================
```

**Step 7 — Run the linter, the formatter and the type checker.**

```bash
ruff check .
ruff format .
mypy src/
```

**Step 8 — Wire up pre-commit and commit.**

```bash
pre-commit install
pre-commit run --all-files
git add .
git commit -m "Initial project skeleton"
```

If `pre-commit` changed any file, `git add .` and commit again. From now on, every commit is
automatically checked.

You now have the same shape of project that an AI/ML team ships: manifest, lock file,
linting, formatting, type checking, tests, and automated pre-commit hooks.

---

## 17. What an AI/ML team expects to see in a pull request

You will eventually contribute to a repository that serves models. When you open a PR, this is
the checklist a reviewer will run, almost word for word:

| Check | Where it lives | Why it matters for AI code |
|---|---|---|
| Dependencies declared and reproducible | `pyproject.toml` + `uv.lock` | two ML libraries rarely agree on versions |
| Secrets not committed | `.gitignore` + `.env.example` | an API key in git history is a real incident |
| Code is formatted | `ruff format` in pre-commit | diffs stay readable |
| Code has no obvious bugs | `ruff check` in pre-commit | catches unused imports, shadowed names |
| Types are declared and checked | `mypy` in pre-commit | an `int` where a `str` was expected is a runtime bug you can catch before running |
| Behaviour is verified | `pytest` in CI | proves the change did not break the prompt pipeline |
| CI runs on every push | `.github/workflows/ci.yml` | nobody merges untested code |

A CI workflow that ties those together is about twenty lines:

```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
        with:
          python-version: "3.12"
      - name: Install dependencies
        run: uv sync --all-extras
      - name: Lint
        run: uv run ruff check .
      - name: Format check
        run: uv run ruff format --check .
      - name: Type check
        run: uv run mypy src/
      - name: Test
        run: uv run pytest --cov=src --cov-report=term-missing
```

Note the order: fastest checks first. Linting takes under a second, type checking a few
seconds, tests last because they are the slowest. That ordering saves you minutes every day.

---

## 🧪 Try it yourself

**Exercise 1 — Prove the isolation.**
Create two folders, `alpha` and `beta`. Give each its own virtual environment and install a
different version of `packaging` in each. Then check, in each environment, which version is
visible. Goal: prove that installing in one does not affect the other.

<details>
<summary>Hint</summary>

`python -m venv .venv` in each folder, activate, then `python -m pip install packaging==23.2`
in one and `packaging==24.0` in the other. Run `python -c "import packaging; print(packaging.__version__)"`
in each.
</details>

<details>
<summary>Solution</summary>

```bash
# terminal 1
mkdir alpha && cd alpha && python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install packaging==23.2
python -c "import packaging; print(packaging.__version__)"   # 23.2

# terminal 2
mkdir beta && cd beta && python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install packaging==24.0
python -c "import packaging; print(packaging.__version__)"   # 24.0

# back in terminal 1 - still 23.2, because the two environments are separate
```
</details>

**Exercise 2 — Read your own manifest.**
Write a `pyproject.toml` with at least three dependencies, one optional extra and one
script entry point. Then write a Python script that loads it with `tomllib` and prints a
one-line summary: the package name, the number of runtime dependencies, and the names of the
extras.

<details>
<summary>Hint</summary>

`tomllib.loads(Path("pyproject.toml").read_text())` gives you a nested dictionary.
`config["project"]["dependencies"]` is a list, `config["project"]["optional-dependencies"]`
is a dict of lists.
</details>

<details>
<summary>Solution</summary>

```python
import tomllib
from pathlib import Path

path = Path("pyproject.toml")
if not path.exists():
    path.write_text(
        '[project]\n'
        'name = "doc-summariser"\n'
        'version = "0.1.0"\n'
        'requires-python = ">=3.12"\n'
        'dependencies = ["httpx>=0.27,<1.0"]\n'
        '\n'
        '[project.optional-dependencies]\n'
        'dev = ["pytest>=8.0"]\n'
        'ai = ["openai>=1.0"]\n',
        encoding="utf-8",
    )

config = tomllib.loads(path.read_text(encoding="utf-8"))
project = config["project"]

print(f"{project['name']} {project['version']}")
print(f"{len(project['dependencies'])} runtime dependencies")
print(f"extras: {', '.join(project.get('optional-dependencies', {}))}")
```

```text
doc-summariser 0.1.0
3 runtime dependencies
extras: dev
```
</details>

**Exercise 3 — Version specifier detective.**
For each specifier below, write down which versions of `1.2.3` are allowed:
`>=1.0`, `~=1.2.3`, `~=1.2`, `==1.2.3`, `!=1.2.3`, `>1.2.3,<2.0.0`.
Then check your answers with `pip install --dry-run` (pip's preview mode) or by reading
PEP 440.

<details>
<summary>Hint</summary>

`~=1.2.3` allows patch-level changes only (`1.2.9` yes, `1.3.0` no). `~=1.2` allows minor
and patch changes (`1.9.0` yes, `2.0.0` no).
</details>

<details>
<summary>Solution</summary>

```text
>=1.0      -> 1.2.3 allowed, and everything above
~=1.2.3    -> 1.2.3 allowed, 1.2.9 allowed, 1.3.0 NOT allowed
~=1.2      -> 1.2.3 allowed, 1.9.0 allowed, 2.0.0 NOT allowed
==1.2.3    -> only 1.2.3
!=1.2.3    -> everything except 1.2.3
>1.2.3,<2  -> 1.2.4 ... 1.99.99
```
</details>

**Exercise 4 — Build the skeleton.**
Create the full project skeleton from section 15 by hand: `src/doc_summariser/`, `tests/`,
`.github/workflows/`, `pyproject.toml`, `.gitignore`, `.env.example`, `.pre-commit-config.yaml`.
Then install it in editable mode, add one function and one test, and get `pytest`, `ruff
check` and `mypy` all passing at once.

<details>
<summary>Hint</summary>

Copy the `.gitignore` block from section 13 and the `pyproject.toml` from step 3 of section 16.
Run `ruff check .` first — it will probably tell you to sort your imports.
</details>

<details>
<summary>Solution</summary>

```bash
mkdir doc-summariser && cd doc-summariser
python -m venv .venv
.\.venv\Scripts\Activate.ps1
mkdir src\doc_summariser
mkdir tests
mkdir .github\workflows
```

`pyproject.toml` (abridged):

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "doc-summariser"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = []

[project.optional-dependencies]
dev = ["pytest>=8.0", "ruff>=0.6", "mypy>=1.11"]

[tool.ruff]
line-length = 88
target-version = "py312"

[tool.pytest.ini_options]
testpaths = ["tests"]
```

`src/doc_summariser/summariser.py`:

```python
# src/doc_summariser/summariser.py
"""Business logic for the summariser."""


def word_count(text: str) -> int:
    """Count whitespace-separated words in a string."""
    return len(text.split())


if __name__ == "__main__":
    print(word_count("hello brave new world"))
```

`tests/test_summariser.py`:

```python
# tests/test_summariser.py
from doc_summariser.summariser import word_count


def test_word_count():
    assert word_count("hello brave new world") == 4


def test_word_count_empty():
    assert word_count("") == 0
```

Then:

```bash
python -m pip install -e ".[dev]"
python -m pytest -v
ruff check . && ruff format . && mypy src/
```

Expected: 2 tests pass, ruff reports no problems, mypy reports no errors.
</details>

---

## ✅ Checkpoint

**1. Why do we use a virtual environment for every project?**

<details>
<summary>Answer</summary>

So that each project has its own isolated set of installed packages. Without it, installing a
package for one project silently changes the environment of every other project, and projects
end up fighting over dependency versions.
</details>

**2. What does `python -m pip install requests` do differently from `pip install requests`?**

<details>
<summary>Answer</summary>

`python -m pip` runs pip *as a module of the Python interpreter you just typed*, so the package
is installed into that interpreter's environment. Bare `pip` is whatever pip executable is
first on your PATH, which may belong to a different Python or a different virtual environment.
</details>

**3. What is the difference between an application and a library when it comes to pinning versions?**

<details>
<summary>Answer</summary>

An application should use ranges (`httpx>=0.27,<1.0`) and rely on a lock file for exact
reproducibility. A library should pin a narrow range so its users get compatible versions and
so the maintainer tests a bounded set of combinations.
</details>

**4. What does the `~=` operator mean? What does `~=0.27.2` allow?**

<details>
<summary>Answer</summary>

`~=` is the compatible-release operator. `~=0.27.2` means `>=0.27.2` and `<0.28.0`, so patch
releases are allowed but the next minor version is not.
</details>

**5. What is a lock file for, and what is its name for `uv` and `poetry`?**

<details>
<summary>Answer</summary>

It records the exact resolved version of every package in the dependency tree so that installs
are reproducible. `uv` uses `uv.lock`; `poetry` uses `poetry.lock`; `pip-tools` produces a
pinned `requirements.txt`.
</details>

**6. Which three older tools does `ruff` replace, and what is each ruff command equivalent to?**

<details>
<summary>Answer</summary>

`flake8` becomes `ruff check`, `black` becomes `ruff format`, and `isort` becomes
`ruff check --select I --fix` (the `I` rules are on by default in the recommended set).
</details>

**7. What does `pre-commit` do, and what single command enables it for a repository?**

<details>
<summary>Answer</summary>

It runs configured checks automatically before every git commit. `pre-commit install` writes
the hook into `.git/hooks/`; the checks themselves are declared in `.pre-commit-config.yaml`.
</details>

**8. Why is `.env` gitignored but `.env.example` is not?**

<details>
<summary>Answer</summary>

`.env` holds real secrets — API keys, database passwords — so it must never be committed.
`.env.example` holds the same keys with placeholder values, so it is safe to commit and tells
new teammates which variables they need to set.
</details>

---

## 🐛 Common mistakes

| Mistake | What you see | Fix |
|---|---|---|
| Installing packages into the base Python instead of the venv | `pip list` shows packages you never asked for; other projects break | Always `python -m venv .venv` and activate it before installing anything |
| Running `pip install x` instead of `python -m pip install x` | Package lands in a different interpreter than the one running your code | Use `python -m pip` everywhere |
| `Activate.ps1` fails with "running scripts is disabled on this system" | PowerShell security error on Windows | `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`, or call `.\.venv\Scripts\python.exe` directly |
| Forgetting to activate the venv, then "the package is not installed" | `ModuleNotFoundError` even though `pip list` shows it | Check `where python` / `which python`; the path must contain `.venv` |
| Pinning `==` versions in `pyproject.toml` for an application | Install breaks when a patch release appears, or teammates get different versions | Use ranges in the manifest; let the lock file pin exact versions |
| Committing `.env` | Secret ends up in git history permanently | Add `.env` to `.gitignore`, add `!.env.example`, and rotate any leaked key |
| Forgetting `.gitignore` entries for `__pycache__` | Hundreds of noise files in every commit | Use the standard `.gitignore` from section 13 from day one |
| Running `pytest` before `pip install -e .` | `ModuleNotFoundError: No module named 'mypackage'` in tests | Install the package in editable mode first |
| Mixing `black` and `ruff format` in one repo | Every file gets reformatted back and forth | Pick one formatter and delete the other from pre-commit |
| Believing `mypy` replaces tests | Types check, but behaviour is still wrong | `mypy` and `pytest` are different tools; you need both |

---

## 🔗 Resources

- [Python Packaging User Guide](https://packaging.python.org/) — the canonical guide to
  `pyproject.toml`, packaging, wheels and publishing; start here if packaging confuses you.
- [PEP 621 — Storing project metadata in pyproject.toml](https://peps.python.org/pep-0621/) —
  the specification that defines the `[project]` table.
- [pip documentation](https://pip.pypa.io/en/stable/) — the official reference for every
  `pip` command, including `--dry-run` and the resolver.
- [venv — Python documentation](https://docs.python.org/3/library/venv.html) — how virtual
  environments work and why activation is optional.
- [uv documentation](https://docs.astral.sh/uv/) — the modern tool for venvs, dependencies,
  lock files and Python version management.
- [ruff documentation](https://docs.astral.sh/ruff/) — configuration reference and the full
  list of lint rules.
- [mypy documentation](https://mypy.readthedocs.io/en/stable/) — configuration options and
  the strict-mode rule list.
- [pre-commit framework](https://pre-commit.com/) — hook configuration, `pre-commit install`,
  and the list of ready-made hooks.
- [uv on PyPI](https://pypi.org/project/uv/) — installation instructions for all platforms.
- [pipx on PyPI](https://pypi.org/project/pipx/) — the tool for installing isolated command
  line applications.
- [python-dotenv on PyPI](https://pypi.org/project/python-dotenv/) — reads `.env` files into
  environment variables.
- [The Twelve-Factor App: Config](https://12factor.net/config) — the classic essay on why
  config belongs in environment variables, not in code.

---

## ➡️ Next

- [13 — Testing](13-testing.md) — with your project set up and reproducible, it is time to
  make sure the code actually works: `pytest`, fixtures, mocking, coverage and TDD.

**← Previous:** [11 — Type hints and modern Python](11-type-hints-and-modern-python.md)
