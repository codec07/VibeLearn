# Python Resources

A curated, verified list of the best Python learning and reference material on the internet.

**Every link below was fetched and confirmed working.** Nothing is here because it ranks well in a
search — it is here because it is genuinely the best place to look for that specific thing. If a
resource stops being maintained, it gets removed at the next review.

Use this page as a **reference, not a curriculum**. Read [the course guide](guide.md) first; come
here when you need the deep version of something, or when you want to go further than this course
goes.

---

## Start here if you want the deep version

| Resource | What it is | Cost |
|---|---|---|
| [The Python Tutorial](https://docs.python.org/3/tutorial/) | The official beginner tutorial. Denser and more complete than this course. | Free |
| [The Hitchhiker's Guide to Python](https://docs.python-guide.org/) | An opinionated handbook on how Python is used *in practice* — structure, style, tooling. The best "how real Python is written" guide. | Free |
| [Python for Everybody](https://www.py4e.com/) | A complete video + textbook course covering Python and data handling. The best free full-course option. | Free |
| [Invent with Python](https://inventwithpython.com/) | Programming through games. Excellent for people who bounce off dry theory. | Free |
| [Kaggle Learn — Python](https://www.kaggle.com/learn/python) | A short, hands-on, in-browser Python course. Good for a fast confidence boost. | Free |

---

## Official documentation

The official docs are better than people give them credit for. They are accurate, complete, and
searchable.

| Resource | What it is |
|---|---|
| [docs.python.org](https://docs.python.org/3/) | The home of all official Python documentation. |
| [The Tutorial](https://docs.python.org/3/tutorial/) | The official beginner-to-intermediate tutorial. |
| [Library Reference](https://docs.python.org/3/library/) | Every module in the standard library, documented. This is your answer to "does Python already do this?". |
| [Language Reference](https://docs.python.org/3/reference/) | The precise, formal rules of the language. Read it when a tutorial is ambiguous. |
| [The Glossary](https://docs.python.org/3/glossary.html) | Official definitions of every Python term. The single best page for clearing up confusion. |
| [What's New in Python](https://docs.python.org/3/whatsnew/index.html) | What changed in each version, and which version introduced each feature. Use it to answer "since when can I do this?". |
| [Python on Windows](https://docs.python.org/3/using/windows.html) / [macOS](https://docs.python.org/3/using/mac.html) / [Unix and Linux](https://docs.python.org/3/using/unix.html) | Official install and platform notes. Read the Windows one before installing on Windows. |
| [Using Python on the Command Line](https://docs.python.org/3/using/cmdline.html) | The full reference for `python`, its flags, and how the interpreter finds your code. |
| [The Python Developer's Guide](https://devguide.python.org/) | How to contribute to CPython itself. Also the best guide to how the language is designed and governed. |
| [Python Packaging User Guide](https://packaging.python.org/en/latest/) | The authoritative guide to packaging and distributing Python code. |
| [Python Enhancement Proposals (PEPs)](https://peps.python.org/) | Where new language features are designed. PEP 8 and PEP 20 are the famous ones. |
| [Python on PyPI](https://pypi.org/project/pip/) | The package installer itself, on the package index. |
| [The Python Software Foundation](https://www.python.org/community/) | The organisation that owns Python, plus the list of local user groups and events. |
| [The Python Wiki](https://wiki.python.org/moin/) | Community-maintained pages on all sorts of topics. Older in places, still useful. |

---

## Style, conventions and "how should I write this"

| Resource | What it is |
|---|---|
| [PEP 8 — Style Guide for Python Code](https://peps.python.org/pep-0008/) | The official style guide. Line length, naming, spacing. Non-negotiable for anyone who will work with other people. |
| [PEP 20 — The Zen of Python](https://peps.python.org/pep-0020/) | Nineteen principles that summarise the language's philosophy. Run `import this` to see them. |
| [PEP 257 — Docstring Conventions](https://peps.python.org/pep-0257/) | How docstrings should be written and structured. |
| [PEP 484 — Type Hints](https://peps.python.org/pep-0484/) | The proposal that introduced type hints. The "why" behind [file 11](11-type-hints-and-modern-python.md). |
| [PEP 621 — Project Metadata](https://peps.python.org/pep-0621/) | How metadata is declared in `pyproject.toml`. |
| [Hitchhiker's Guide: Code Style](https://docs.python-guide.org/writing/style/) | The style chapter of the Hitchhiker's Guide, with idioms and conventions. |
| [Hitchhiker's Guide: Common Gotchas](https://docs.python-guide.org/writing/gotchas/) | Mutable default arguments, late-binding closures, and other traps, explained properly. |
| [Hitchhiker's Guide: Project Structure](https://docs.python-guide.org/writing/structure/) | How to lay out a Python project so other humans can navigate it. |

---

## Interactive tools, debuggers and learning aids

| Resource | What it is |
|---|---|
| [Python Tutor](https://pythontutor.com/) | Watch your code execute step by step, with the variables visualised. The single most useful tool for a beginner who does not yet know how to read a traceback. |
| [traceback module](https://docs.python.org/3/library/traceback.html) | The official docs for how Python reports errors, including how to read and print them yourself. |
| [pdb — the Python debugger](https://docs.python.org/3/library/pdb.html) | The built-in debugger. Set a breakpoint, step through line by line, inspect variables. |
| [debugpy](https://github.com/microsoft/debugpy) | The debugger behind VS Code's "Debug Python". Attach to a running process and inspect it live. |
| [Programiz Python Tutorials](https://www.programiz.com/python-programming/tutorial) | Clean, example-heavy tutorials for each language topic. Useful as a second explanation when something is still fuzzy. |
| [learnpython.org](https://www.learnpython.org/) | A browser-based Python REPL with guided exercises. No install needed — the fastest way to get your first win. |
| [codecov / coverage.py docs](https://coverage.readthedocs.io/en/latest/) | Official docs for measuring which lines your tests actually execute. |
| [Real Python](https://realpython.com/) | Deep, well-written articles on intermediate and advanced Python topics. The best "I already know the basics, now what?" resource. |

---

## Practice and exercises

You cannot learn to program by reading. These are where the real learning happens.

| Resource | What it is |
|---|---|
| [Exercism — Python track](https://exercism.org/tracks/python) | Free exercises with human mentor feedback. Excellent difficulty curve for a beginner. |
| [Codewars](https://codewars.com/) | Small, bite-sized kata, from "Hello World" upward. Great for daily practice. |
| [Advent of Code](https://adventofcode.com/) | A yearly December puzzle series. Brilliant for practising data manipulation, and it makes you think like a programmer. |
| [The Algorithms — Python](https://github.com/TheAlgorithms/Python) | Hundreds of classic algorithms implemented in Python. Read them after you can write them yourself. |
| [Python Patterns](https://github.com/faif/python-patterns) | Design patterns in idiomatic Python. Good to read before or during [file 10](10-object-oriented-programming.md). |
| [Freecodecamp: Scientific Computing with Python](https://www.freecodecamp.org/learn/scientific-computing-with-python/) | Free, project-based NumPy/pandas course. A preview of Step 3. |
| [simonw/til](https://github.com/simonw/til) | Simon Willison's "Today I Learned" — hundreds of short, practical Python tips. Reading this is a free, continuous education. |

---

## Tooling and project setup

| Resource | What it is |
|---|---|
| [uv](https://docs.astral.sh/uv/) | The modern, extremely fast tool that manages Python versions, virtual environments, dependencies and builds in one. The direction the ecosystem is moving. |
| [uv on PyPI](https://pypi.org/project/uv/) | The package listing and install instructions. |
| [Ruff](https://docs.astral.sh/ruff/) | One fast binary that replaces flake8, isort, pyupgrade and (optionally) black. The default linter and formatter in new Python projects. |
| [Ruff on PyPI](https://pypi.org/project/ruff/) | Install instructions and configuration reference. |
| [Black](https://black.readthedocs.io/en/stable/) | The formatter that made formatting automatic. Still widely used; ruff format is its modern successor. |
| [black on GitHub](https://github.com/psf/black) | Source, changelog and the "black" style in detail. |
| [pip documentation](https://pip.pypa.io/en/stable/) | The official pip docs, including the resolver behaviour that confuses people. |
| [pipx](https://pypi.org/project/pipx/) | Install command-line tools into their own isolated environments so they never clash with your project. |
| [pre-commit](https://pre-commit.com/) | Run linters, formatters and type checkers automatically before every commit. |
| [pre-commit on GitHub](https://github.com/pre-commit/pre-commit) | Configuration examples and hook catalogue. |
| [python-dotenv](https://pypi.org/project/python-dotenv/) | Loads `.env` files into environment variables — the standard way to keep API keys out of your code. |
| [Packaging your project](https://packaging.python.org/en/latest/tutorials/packaging-projects/) | The official walkthrough for turning a folder of code into a distributable package. |
| [pyenv](https://github.com/pyenv/pyenv) | Install and switch between multiple Python versions on one machine. |
| [VS Code Python extension](https://github.com/microsoft/vscode-python) | The most popular editor setup for Python: debugging, linting, type hints and virtual environment detection. |
| [JupyterLab](https://github.com/jupyterlab/jupyterlab) | The notebook environment used across AI and data work. |
| [JupyterLab on PyPI](https://pypi.org/project/jupyterlab/) | Install instructions. |

---

## Type checking

| Resource | What it is |
|---|---|
| [mypy documentation](https://mypy.readthedocs.io/en/stable/) | The most widely used static type checker for Python. |
| [mypy on GitHub](https://github.com/python/mypy) | Source, plugins and release notes. |
| [mypy common issues](https://mypy.readthedocs.io/en/stable/common_issues.html) | The errors beginners hit most, and how to silence or fix them properly. |
| [mypy running mypy](https://mypy.readthedocs.io/en/stable/running_mypy.html) | Every command-line flag explained. |
| [typing module docs](https://docs.python.org/3/library/typing.html) | The official reference for every typing construct: `Optional`, `Literal`, `TypedDict`, `Protocol`, `NewType` and more. |
| [typing spec](https://typing.python.org/en/latest/) | The community-run specification behind the typing system, including how it may evolve. |

---

## Testing

| Resource | What it is |
|---|---|
| [pytest documentation](https://docs.pytest.org/en/stable/) | The official pytest docs, and the best-written documentation of any Python testing tool. |
| [pytest on GitHub](https://github.com/pytest-dev/pytest) | Source, plugins and the changelog. |
| [pytest fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html) | How to set up and tear down test data properly. |
| [pytest parametrize](https://docs.pytest.org/en/stable/how-to/parametrize.html) | Running one test against many inputs. |
| [pytest monkeypatch](https://docs.pytest.org/en/stable/how-to/monkeypatch.html) | Safely modifying objects and environment variables inside a test. |
| [pytest tmp_path](https://docs.pytest.org/en/stable/how-to/tmp_path.html) | Isolated temporary directories for tests that touch the filesystem. |
| [pytest good practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html) | What to test, what not to test, and how to keep a test suite maintainable. |
| [pytest-cov](https://pypi.org/project/pytest-cov/) | Coverage measurement for pytest. |
| [unittest.mock](https://docs.python.org/3/library/unittest.mock.html) | The official docs for mocking, patching and spying — the standard library's answer to "what if I don't want to call the real API?". |
| [Hitchhiker's Guide: Testing](https://docs.python-guide.org/writing/tests/) | A short, opinionated take on how to structure tests in a Python project. |

---

## The standard library, by task

You do not need to install anything for any of these. The official
[Library Reference](https://docs.python.org/3/library/) documents all of them.

| I want to... | Use | Docs |
|---|---|---|
| Work with file paths | `pathlib` | [docs](https://docs.python.org/3/library/pathlib.html) |
| Handle dates and times | `datetime`, `zoneinfo` | [docs](https://docs.python.org/3/library/datetime.html) |
| Count and group things | `collections` (`Counter`, `defaultdict`, `deque`) | [docs](https://docs.python.org/3/library/collections.html) |
| Chain and slice iterables | `itertools` | [docs](https://docs.python.org/3/library/itertools.html) |
| Cache results, build partials | `functools` | [docs](https://docs.python.org/3/library/functools.html) |
| Parse and write JSON | `json` | [docs](https://docs.python.org/3/library/json.html) |
| Read and write CSV | `csv` | [docs](https://docs.python.org/3/library/csv.html) |
| Match text patterns | `re` | [docs](https://docs.python.org/3/library/re.html) |
| Build CLI tools | `argparse` | [docs](https://docs.python.org/3/library/argparse.html) |
| Log properly | `logging` | [docs](https://docs.python.org/3/library/logging.html) |
| Write context managers | `contextlib` | [docs](https://docs.python.org/3/library/contextlib.html) |
| Define constants and enums | `enum` | [docs](https://docs.python.org/3/library/enum.html) |
| Build structured records | `dataclasses` | [docs](https://docs.python.org/3/library/dataclasses.html) |
| Run another program | `subprocess` | [docs](https://docs.python.org/3/library/subprocess.html) |
| Manage concurrency | `concurrent.futures`, `asyncio`, `threading`, `multiprocessing` | [futures](https://docs.python.org/3/library/concurrent.futures.html) · [asyncio](https://docs.python.org/3/library/asyncio.html) · [threading](https://docs.python.org/3/library/threading.html) · [multiprocessing](https://docs.python.org/3/library/multiprocessing.html) |
| Use async task groups | `asyncio.TaskGroup` | [docs](https://docs.python.org/3/library/asyncio-task.html) |
| Create temporary files | `tempfile` | [docs](https://docs.python.org/3/library/tempfile.html) |
| Generate secure tokens | `secrets` | [docs](https://docs.python.org/3/library/secrets.html) |
| Work with archives and zips | `zipfile`, `tarfile` | [zipfile](https://docs.python.org/3/library/zipfile.html) · [tarfile](https://docs.python.org/3/library/tarfile.html) |
| Query a local database | `sqlite3` | [docs](https://docs.python.org/3/library/sqlite3.html) |
| Do exact decimal maths | `decimal` | [docs](https://docs.python.org/3/library/decimal.html) |
| Compute statistics | `statistics` | [docs](https://docs.python.org/3/library/statistics.html) |
| Compare and diff text | `difflib`, `textwrap` | [difflib](https://docs.python.org/3/library/difflib.html) · [textwrap](https://docs.python.org/3/library/textwrap.html) |
| Talk HTTP with the stdlib | `urllib.request`, `http` | [urllib](https://docs.python.org/3/library/urllib.request.html) · [http](https://docs.python.org/3/library/http.html) |
| Inspect objects at runtime | `inspect`, `ast` | [inspect](https://docs.python.org/3/library/inspect.html) · [ast](https://docs.python.org/3/library/ast.html) |
| Work with timezones properly | `zoneinfo` | [docs](https://docs.python.org/3/library/zoneinfo.html) |

---

## Moving toward AI and data (preview of later steps)

You do not need these for Step 1. They are here so you know what exists when you reach Steps 3, 7
and 9.

| Resource | What it is |
|---|---|
| [NumPy](https://pypi.org/project/numpy/) | Fast n-dimensional arrays. The foundation of every numerical and ML library. |
| [pandas](https://pypi.org/project/pandas/) | DataFrames: tabular data manipulation. The tool you will use most in Step 3. |
| [Matplotlib](https://pypi.org/project/matplotlib/) | The standard plotting library. |
| [Seaborn](https://pypi.org/project/seaborn/) | Statistical plots that look good without much effort. |
| [scikit-learn](https://pypi.org/project/scikit-learn/) | Classical machine learning in one consistent API. The core of Step 5. |
| [PyTorch](https://pypi.org/project/torch/) | The deep learning framework used across Step 7. |
| [OpenAI Python SDK](https://github.com/openai/openai-python) | The official client for the OpenAI API. |
| [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python) | The official client for the Claude API. |
| [OpenAI API docs](https://platform.openai.com/docs/overview) | The API reference for OpenAI models. |
| [Anthropic API docs](https://docs.anthropic.com/en/docs/intro-to-claude) | The API reference for Claude models. |
| [Hugging Face Transformers](https://huggingface.co/docs/transformers/index) | Thousands of pretrained models behind one API. The core of Step 8. |
| [LiteLLM](https://pypi.org/project/litellm/) | One interface for calling many model providers. |
| [Chroma](https://pypi.org/project/chromadb/) | An embedding database for retrieval-augmented generation. The core of Step 9. |
| [simonw/llm](https://github.com/simonw/llm) | A command-line tool for calling LLMs. Useful for experimenting, and the code is short enough to read. |

---

## Staying current

Python changes every year, but the core language is famously stable. You do not need to chase every
release.

| Resource | What it is |
|---|---|
| [Python Insider](https://blog.python.org/) | The official Python blog — release announcements and the Core Developers' newsletter. |
| [The Python.org blog aggregator](https://www.python.org/blogs/) | Every post from the PSF and the wider community in one feed. |
| [Real Python newsletter](https://realpython.com/) | A weekly digest of Python articles, videos and projects. |
| [Python Discuss](https://discuss.python.org/) | The official community forum. The right place to ask a real question about the language itself. |
| [Python Weekly](https://www.pythonweekly.com/) | A well-regarded weekly roundup of Python news, articles and tools. |
| [Talk Python To Me](https://talkpython.fm/) | A long-running podcast with interviews from Python core developers and the industry. |
| [Python Bytes](https://pythonbytes.fm/) | A short weekly podcast covering Python news in about 20 minutes. |

---

## Books worth owning

| Book | Why |
|---|---|
| *Python Crash Course* — Eric Matthes | The best beginner book. Project-based, paced well, genuinely teaches. |
| *Automate the Boring Stuff with Python* — Al Sweigart | Free to read online. Automating spreadsheets, files and the web. |
| *Fluent Python* — Luciano Ramalho | The book to read once you are comfortable. Explains *why* Python works the way it does. |
| *Effective Python* — Brett Slatkin | 90 concrete, immediately-applicable items. The best "improve your code today" book. |
| *The Hitchhiker's Guide to Python* — Kenneth Reitz | The website above in book form. Opinionated and practical. |

---

## A note on how to actually use this page

Do not try to read all of it. The mistake beginners make is treating a resource list like a second
curriculum and burning out in week two.

**A better way to use it:**

1. Finish the course chapters. They are self-contained.
2. When a chapter says "see the docs for the full details", come here and read *that one page*.
3. When you finish Step 1 and want more practice, pick **one** resource from the practice section
   and stick with it for a month.
4. When you are stuck on a real problem, search the [Library Reference](https://docs.python.org/3/library/)
   before writing your own utility. It is almost always already there.

---

**← Previous:** [17 — Python for AI and data](17-python-for-ai-and-data.md)
