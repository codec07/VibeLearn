# Python — From Absolute Zero to AI Engineer

> **Welcome.** You are about to start the longest single step of this repository: learning Python
> properly, from the very first line of code to the point where you can build real AI applications.
> You do not need any prior experience. You do not need a maths degree. You need a computer, an
> internet connection, and about 17 hours of honest, focused time spread over a few weeks.

---

## What this course actually is

This folder contains a complete, self-paced Python course written as plain Markdown. Every page is a
chapter. You read it, you run the code, you do the exercises, you move on. There is no video to
watch and no "final exam" — the only thing that matters is that you can write working Python by the
end.

The course is deliberately ordered. Each file assumes you read the ones before it (unless you already
know that material — in which case, skip it and use the table of contents to jump ahead). The order
below is the order that has worked for thousands of beginners: **learn the language, then learn to
think in it, then learn to build real programs with it, then learn to build production software with
it, then apply it to AI.**

---

## The 5 arcs

| Arc | Files | You are learning to… | Ends with you able to… |
|---|---|---|---|
| **0 — Orientation** | `00` | use this repo and install Python | run your first script |
| **1 — The Language** | `01`–`04` | speak Python: values, types, control flow | write programs that take decisions |
| **2 — Thinking in Python** | `05`–`07` | structure code and data | transform and organise any dataset |
| **3 — Real Programs** | `08`–`11` | build multi-file, tested, typed projects | ship code a team can maintain |
| **4 — Professional Python** | `12`–`15` | use the ecosystem the industry uses | work on a real AI codebase |
| **5 — Apply & Ship** | `16`–`17` | build end-to-end projects | build an LLM app from scratch |

The **1-hour rule** beats the "10,000 hours" meme. After each file, do the 🧪 exercises. If you
cannot solve them, that is signal — go back and re-read that file. Reading alone does not teach
code; running code does.

---

## Table of contents

### Arc 0 — Orientation

| # | File | What it covers | ⏱️ |
|---|---|---|---|
| 00 | [How to use this course](00-how-to-use-this-course.md) | The learning loop, how to run code, how to get unstuck | 25 min |

### Arc 1 — The Language

| # | File | What it covers | ⏱️ |
|---|---|---|---|
| 01 | [Getting started](01-getting-started.md) | Installing Python, the REPL, running scripts, how Python actually runs your code | 40 min |
| 02 | [Syntax and variables](02-syntax-and-variables.md) | Names, values, assignment, operators, strings, f-strings, comments | 50 min |
| 03 | [Data types and operators](03-data-types-and-operators.md) | int/float/bool/None, comparisons, logic, truthiness, type conversion | 55 min |
| 04 | [Control flow](04-control-flow.md) | `if`, `for`, `while`, `break`, `continue`, `else` clauses | 55 min |

### Arc 2 — Thinking in Python

| # | File | What it covers | ⏱️ |
|---|---|---|---|
| 05 | [Functions](05-functions.md) | Defining, arguments, defaults, returns, scope, docstrings | 1 hr |
| 06 | [Data structures](06-data-structures.md) | list, tuple, dict, set — when to use which, slicing, mutability | 55 min |
| 07 | [Comprehensions and iterators](07-comprehensions-and-iterators.md) | generators, `yield`, `iter()`/`next()`, unpacking, the iterator protocol | 50 min |

### Arc 3 — Real Programs

| # | File | What it covers | ⏱️ |
|---|---|---|---|
| 08 | [Modules and packages](08-modules-and-packages.md) | imports, `__name__`, project layout, `pip`, `venv`, publishing | 45 min |
| 09 | [File I/O and errors](09-file-io-and-errors.md) | reading/writing files, CSV, JSON, exceptions, `try`/`except`, logging | 1 hr 5 min |
| 10 | [Object-oriented programming](10-object-oriented-programming.md) | classes, instances, methods, inheritance, `dataclass`, protocols | 55 min |
| 11 | [Type hints and modern Python](11-type-hints-and-modern-python.md) | annotations, `mypy`, dataclasses, `match`, walrus, comprehensions | 55 min |

### Arc 4 — Professional Python

| # | File | What it covers | ⏱️ |
|---|---|---|---|
| 12 | [Environments and tooling](12-environments-and-tooling.md) | `venv`, `pip`, `pyproject.toml`, `ruff`, `black`, `mypy`, pre-commit | 55 min |
| 13 | [Testing](13-testing.md) | `pytest`, fixtures, parametrisation, mocking, coverage, TDD | 1 hr |
| 14 | [Standard library](14-standard-library.md) | `pathlib`, `datetime`, `collections`, `itertools`, `json`, `re`, `subprocess` | 1 hr |
| 15 | [Concurrency and async](15-concurrency-and-async.md) | threads, processes, `asyncio`, `await`, async HTTP, the GIL | 55 min |

### Arc 5 — Apply and ship

| # | File | What it covers | ⏱️ |
|---|---|---|---|
| 16 | [Practice projects](16-practice-projects.md) | 8 guided projects, from CLI tools to a working API client | ~2 hrs |
| 17 | [Python for AI and data](17-python-for-ai-and-data.md) | NumPy, pandas, HTTP APIs, LLM SDKs, embeddings, RAG basics | 55 min |
| — | [Resources](resources.md) | Curated official docs, courses, books, tools, cheat sheets | reference |

---

## Where to start if you already know some of this

You do **not** have to read this course front to back. Use this table to skip:

| If you already… | Skip to |
|---|---|
| installed Python before and run scripts | [01 Getting started](01-getting-started.md) → [02 Syntax](02-syntax-and-variables.md) |
| know variables, `if`, loops | [05 Functions](05-functions.md) |
| know functions and lists/dicts | [07 Comprehensions](07-comprehensions-and-iterators.md) |
| have written OOP code | [11 Type hints](11-type-hints-and-modern-python.md) |
| have shipped a Python package | [12 Environments and tooling](12-environments-and-tooling.md) |
| have used `pytest` and CI | [14 Standard library](14-standard-library.md) |

**But** do not skip the 🧪 exercises in any file you do read. And if a file feels easy, skim it for the
🐛 Common mistakes table — the traps listed there are the ones that cost real engineers real hours.

---

## Prerequisites

- A computer: Windows, macOS or Linux. The examples here are written to work on all three.
- Python **3.12 or newer**. [01 Getting started](01-getting-started.md) shows you how to check and install.
- A text editor. VS Code is the safest default, but anything works.
- About **500 MB** of free disk space once you start installing packages in Arc 4.
- No prior programming experience. Genuinely none.

Cost: **nothing**. Everything in this course is free and open source. If a later step of this
repository suggests a paid tool, it will always be marked as optional.

---

## How to actually study this (the important part)

1. **Read one file.** Not five. One. Resist the urge to binge.
2. **Type the code out yourself.** Do not copy-paste. Typing it is where the learning happens.
3. **Break things on purpose.** Change a value, delete a colon, print the wrong variable. Read the
   error. Python's error messages are unusually good — they are the curriculum.
4. **Do the 🧪 exercises without looking at the hints** (they are folded away, so you have to
   resist peeking).
5. **Answer the ✅ Checkpoint honestly.** If you cannot, re-read the section it came from.
6. **Move on.** You do not need 100% recall. You need enough recall that the next file feels familiar.

### When you get stuck

Work down this list — it is ordered by how often it is the actual answer:

1. Read the **full error message**, including the last line. It usually names the file, the line
   number and the problem.
2. Print the value you are unsure about. `print(repr(x))` shows hidden whitespace and `None`.
3. Search the error message verbatim in Google — you are almost never the first person to hit it.
4. Check the [🐛 Common mistakes](00-how-to-use-this-course.md) table in the relevant file.
5. Use the [Python Tutor](https://pythontutor.com/) to watch your code execute step by step. This is
   the single best debugging tool for beginners and it still helps professionals.
6. Ask an LLM with your actual code and the full traceback pasted in. AI coding assistants are
   excellent at Python — treat them as a patient tutor, not an oracle, and always verify the answer.

---

## The bigger picture: where this is going

This is **Step 1 of 10** in the full repository:

| Step | Folder | What you will be able to do after it |
|---|---|---|
| 1 | **PYTHON** *(you are here)* | write, test and ship Python |
| 2 | [DEVELOPER FOUNDATIONS](../DEVELOPER%20FOUNDATIONS/guide.md) | use Git, GitHub, Linux, FastAPI and design systems |
| 3 | [DATA MANAGEMENT](../DATA%20MANAGEMENT/guide.md) | Excel, SQL, NumPy, pandas, Matplotlib, Seaborn |
| 4 | [MATHEMATICS FOR AIML](../MATHEMATICS%20%28FOR%20AIML%29/guide.md) | linear algebra, calculus, statistics |
| 5 | [CLASSICAL MACHINE LEARNING](../CLASSICAL%20MACHINE%20LEARNING/guide.md) | train and evaluate classical models |
| 6 | [ML PROJECTS](../ML%20PROJECTS/guide.md) | ship prediction, cancer-detection and stock models |
| 7 | [DEEP LEARNING](../DEEP%20LEARNING/guide.md) | neural networks from scratch to PyTorch |
| 8 | [NLP & TRANSFORMERS](../NLP%20&%20TRANSFORMERS/guide.md) | transformers, attention, fine-tuning |
| 9 | [GENERATIVE AI](../GENERATIVE%20AI/guide.md) | RAG, agents, evals, prompt engineering |
| 10 | [AGENTIC AI](../AGENTIC%20AI/guide.md) | build autonomous agent systems |

The later steps assume you are comfortable in Python. That is the entire reason this step exists and
the reason it starts at absolute zero.

---

## Conventions used in every file

| Marker | Meaning |
|---|---|
| `⏱️ Time` | how long the file should take you, honestly |
| `📚 Prereqs` | which file you must have read first |
| `🎯 By the end` | the single concrete skill you gain |
| `🧪 Try it yourself` | exercises — do these, do not skip them |
| `✅ Checkpoint` | short quiz to test recall |
| `🐛 Common mistakes` | the traps that catch beginners |
| `🔗 Resources` | verified, high-quality links |
| `➡️ Next` | where to go next |

Code blocks are labelled with the language (`python`, `bash`, `text`). Everything in a `python` block
is meant to be pasted into a file and run as-is.

---

## Ready?

Start here: **[00 — How to use this course](00-how-to-use-this-course.md)**

If you want the shortest possible path to a working program first, read
[01 Getting started](01-getting-started.md) and write your first script in about ten minutes.
