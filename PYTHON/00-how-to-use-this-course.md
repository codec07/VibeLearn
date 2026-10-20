# How to Use This Course

This file is about the mechanics of learning Python: how to actually run code on your machine, how
to read the error messages when something breaks, and what to do when you are stuck. It is short on
purpose — the *roadmap* of the course lives in [guide.md](guide.md), and this file just teaches you
how to work through it. Everything here applies to every later chapter.

> **⏱️ Time:** ~10 minutes
> **📚 Prereqs:** [guide.md](guide.md) — the course roadmap and the list of chapters
> **🎯 By the end you can:** run Python three different ways, read a traceback from the bottom up, and
> work yourself out of a bug using a five-step checklist

---

## Why this matters for AI engineering

An AI engineer reads code constantly — other people's code, generated code, and their own code from
three days ago. The skill that separates people who ship AI products from people who get stuck is
not memorising syntax; it is reading an error message calmly and finding the one line that is
wrong. Every LLM SDK, every agent loop, every training script is thousands of lines of Python you
did not write, and most of your day will be spent navigating exactly that. A red traceback is not a
sign of failure. It is the normal output of a normal day.

---

## The learning loop

Every chapter in this course is built around the same five-step loop. Do not skip steps 2 and 3 —
they are where the learning actually happens.

```text
    read  ──▶  type it  ──▶  break it  ──▶  exercise  ──▶  checkpoint
      ▲                                                          │
      └──────────────────────────────────────────────────────────┘
                  not confident?  →  read it again
```

| Step | What you actually do | Why it exists |
|---|---|---|
| **read** | Read one section, one file. Not the whole folder. | You need a small, finishable target or you will not start. |
| **type it** | Type every example by hand into a file. Do not copy-paste. | Typing forces you to notice the colon, the quotes, the indentation. Copy-paste hides all three. |
| **break it** | Deliberately change something — delete a colon, misspell a name, change a number — and run it again. | Reading the error is more valuable than reading the correct code. |
| **exercise** | Do the 🧪 exercises at the bottom of the file without peeking at the hints. | Recall is what makes the next file feel familiar. |
| **checkpoint** | Answer the ✅ questions out loud. If you cannot, re-read that one section. | It tells you exactly where to go back, instead of "somewhere earlier". |

**How long per file.** The time estimate at the top of each file is the honest number for reading
and typing alone. Multiply it by two or three for the exercises. If you have thirty minutes, read
one chapter and do two exercises. That is a good session.

---

## The three ways to run Python code

You will use all three. None is "the right one" — they are for different moments.

### 1. The interactive prompt (the REPL)

The REPL stands for **Read, Eval, Print, Loop**. It is a live Python session that prints the result of
every expression you type. Start it from a terminal:

```bash
python
```

```text
Python 3.13.1 (tags/v3.13.1:0671451, Dec  3 2024, 19:06:28) [MSC v.1942 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> 2 + 2
4
>>> name = "Ada"
>>> name
'Ada'
>>>
```

On macOS and many Linux distributions the command is `python3` instead of `python`. Type `.exit()`
(or press `Ctrl+D` / `Ctrl+Z`) to leave.

**Use the REPL when** you want to try one expression, check what a function returns, or poke at a
value. It gives instant feedback with zero setup.

**The REPL's limits.** Nothing you type in it is saved. It has a history you can scroll with the
arrow keys, but if you close the window, the work is gone. And in the REPL, an expression prints its
value automatically — you do not need `print()`.

### 2. A script, run from the terminal

A **script** is a plain text file with Python code in it, usually ending in `.py`. Save the file,
then run it:

```bash
python hello.py
```

**Use a script when** the code is more than a couple of lines, when you want to keep the result, or
when you are building anything real. Almost everything from
[01 Getting started](01-getting-started.md) onward is done in scripts.

If your machine only has the `python3` command (common on macOS and Linux), use `python3 hello.py`.
On Windows, the `py` launcher also works: `py hello.py`.

### 3. An editor, with the Python extension

The third option is a **text editor** — a program built for writing code. VS Code is free, runs on
all three operating systems, and is the safest default. It gives you syntax highlighting, automatic
indentation, autocomplete, and a "Run" button.

Install VS Code, then install the official Python extension by Microsoft (search for
"Python" in the extensions panel), then open your project folder. Press the ▷ **Run Python File**
button in the top-right corner of the editor, or press `Ctrl+F5` (`Cmd+F5` on macOS).

**Use an editor when** you are writing more than a few lines, writing a file you will keep, or
editing an existing project.

```text
   one-off question            keep the code            building a project
   "what is 2 ** 10?"     →    hello.py            →    a folder of .py files
        REPL                  terminal                 VS Code
```

---

## The anatomy of a traceback

When your program crashes, Python prints a **traceback**: a report that lists every function call it
was inside, all the way down to the line that failed. Here is the script:

```python
def greet(name):
    return "Hello, " + name + "!"


greeting = greet("Ada")
print(greeting)
```

It runs fine and prints `Hello, Ada!`. Now change `"Ada"` to the number `42` — no quotes — and run
it again. You get this traceback:

```text
Traceback (most recent call last):
  File "C:\Users\you\python-basics\greet.py", line 5, in <module>
    greeting = greet(42)
  File "C:\Users\you\python-basics\greet.py", line 2, in greet
    return "Hello, " + name + "!"
           ~~~~~~~~~~^~~~~~
TypeError: can only concatenate str (not "int") to str
```

### Read it from the BOTTOM up

This is the single most valuable habit in this file. Beginners read the top because it appears
first. The bottom contains the answer.

```text
  ┌───────────────────────────────────────────────────────────────────────┐
  │ LINE 1   Traceback (most recent call last):                          │  ← ignore this
  ├───────────────────────────────────────────────────────────────────────┤
  │ LINE 2   File "...greet.py", line 5, in <module>                     │  ← where the
  │ LINE 3     greeting = greet(42)                                      │    crash was
  ├───────────────────────────────────────────────────────────────────────┤    triggered
  │ LINE 4   File "...greet.py", line 2, in greet                        │
  │ LINE 5     return "Hello, " + name + "!"                             │  ← where the
  │ LINE 6                ~~~~~~~~~~^~~~~~                                │    crash happened
  ├───────────────────────────────────────────────────────────────────────┤
  │ LINE 7   TypeError: can only concatenate str (not "int") to str      │  ← THE ANSWER
  └───────────────────────────────────────────────────────────────────────┘
```

| Part | What it tells you |
|---|---|
| `Traceback (most recent call last):` | Just a header. It tells you the list below is in the order the calls happened. |
| `File "...", line 5, in <module>` | The **file** the crash happened in, the **line number**, and the **function** it was in. `<module>` means top-level code — not inside any function. |
| The source line | Python shows you the exact line that failed, so you do not have to go hunting for it. |
| The `^` and `~` markers | Python 3.11+ underlines the exact expression that blew up. The `^` points at the precise spot — here the `+` operator — and the `~` regions cover the two operands on either side of it. |
| `TypeError: ...` | The **error type** and the **message**. Read it word by word. It usually tells you the fix. |

### The answer, in plain English

The last line says: *you tried to add (concatenate) a string and an integer, and Python does not
allow that.* The `^` marker points at the `+` on line 2, and the `~` regions on either side cover
the two things being added — the string literal `"Hello, "` and the variable `name`, which was
supposed to hold a string but was given the number `42`.

The fix is on the calling line (line 5): `greeting = greet("42")` or `greeting = greet(str(42))`.

### Other tracebacks you will meet early

```text
  File "...greet.py", line 3
    print("oops")
                 ^
IndentationError: unindent does not match any outer indentation level
```

```text
  File "...greet.py", line 1
    print("hello"
         ^
SyntaxError: '(' was never closed
```

Both of these are **syntax errors**: Python refused to even start, because the code is not
grammatically valid Python. (`IndentationError` is a kind of `SyntaxError` — same family.) Syntax
errors are reported before your program runs a single line, so the line number is always the line
with the problem. A `NameError` (you used a variable you never defined) and a `TypeError` (wrong
kind of value) are *runtime* errors — they happen while running.

---

## Five ways to get unstuck

Work down this list. It is roughly ordered by how often each one is the actual answer. The order is
a checklist, not a law — in practice you will often read the error message first and then come back
here.

### 1. Print the value you are unsure about

Put `print(x)` on the line *before* the one that breaks. Half of all beginner bugs are "the value is
not what I thought it was".

```python
user_input = "  42  "
print(user_input)
stripped = user_input.strip()
print(stripped)
number = int(stripped)
print(number)
print(number * 2)
```

```text
  42
42
42
84
```

### 2. Print `repr(x)` instead of `print(x)`

`repr()` — short for *representation* — shows you the value the way Python stores it, including
quotes around strings, hidden spaces, and the literal word `None`. When `print()` looks identical
to `repr()`, the difference is invisible; `repr()` makes it obvious.

```python
name = "Ada Lovelace"
plain = "Ada Lovelace "
print(plain)       # the trailing space is invisible here
print(repr(plain))  # now you can see it
print(repr(name))
print(repr(None))
```

```text
Ada Lovelace 
'Ada Lovelace '
'Ada Lovelace'
None
```

### 3. Read the error message — all of it

The last line of the traceback is the diagnosis. It names the *kind* of problem (`TypeError`,
`NameError`, `SyntaxError`, `KeyError`, `IndexError`, `ValueError`) and usually says what it
wanted instead. Then look at the `^` markers to find the exact spot.

You do not need to understand the whole traceback to fix the bug. You need the last line and the
line it points at.

### 4. Search the error message verbatim

Copy the *whole* final line — including the error type name — and paste it into a search engine.
You are almost never the first person to have hit it. A good search looks like:

```text
TypeError: can only concatenate str (not "int") to str
```

Searching that exact string finds the official docs and thousands of people who fixed the same
thing.

### 5. Watch it execute in Python Tutor

[Python Tutor](https://pythontutor.com/) runs your code in the browser and shows you a visual
diagram of your variables changing as each line executes. You can watch a list grow, see exactly
where a value becomes `None`, and understand *why* a line failed. It is still the single best
debugging tool for beginners, and it is genuinely useful for professionals too.

Paste your code in, press "Visualize", and click "Run" one step at a time.

---

## How to ask a good question (including to an AI assistant)

Whether you are asking a person on a forum, a colleague, or an AI coding assistant, the formula is
the same. **A good question contains three things:**

1. The **code** — the smallest snippet that still shows the problem.
2. The **full error message** — every line of the traceback, not a paraphrase.
3. The **gap** — what you expected, and what actually happened.

### A bad question

> My code doesn't work. Can you fix it?

That is unanswerable. The responder has to guess your file name, your variable names, and the error.
They will ask you to paste the code, and you will wait two days.

### A good question

> Here is what I have. Python 3.13 on Windows.
>
> The code:
>
> ```python
> from pathlib import Path
>
> data = Path("notes.txt").read_text()
> lines = data.split("\n")
> print(lines[10])
> ```
>
> The full traceback:
>
> ```text
> Traceback (most recent call last):
>   File "read_notes.py", line 5, in <module>
>     print(lines[10])
>           ~~~~~^^^^
> IndexError: list index out of range
> ```
>
> What I expected: the tenth line of the file.
> What actually happened: `IndexError: list index out of range`.
> The file has 6 lines. I checked by printing `len(lines)`.

That question is answerable in one message. The assistant (or the human) can see immediately that
the file is shorter than expected, and can suggest `lines[-1]`, a `for` loop, or a bounds check.

### Asking an AI assistant well

AI coding assistants are genuinely excellent at Python. Treat them as a patient tutor, not an oracle:

- Paste the **code and the full traceback**, exactly as the brief above.
- Say what you already tried. It stops them repeating a suggestion you have rejected.
- Ask them to **explain**, not just to fix: *"Explain why `read_text()` returns a string and why
  `split("\n")` gives me one extra empty element at the end."*
- **Verify.** Run the code they give you. Never paste code you have not read.

---

## What "reproducing a bug" means

A **bug** is a defect in your program: it does something you did not ask for. A **reliable bug** is
one you can make happen again, every time, on demand.

**Reproducing a bug** means making the faulty behaviour happen again yourself, deliberately, so you
can watch it. If you cannot reproduce it, you cannot fix it — you would just be guessing at what
changed.

Here is what a reproducible bug looks like in practice:

```python
def average(numbers):
    return sum(numbers) / len(numbers)


scores = [80, 90, 100]
print("Average:", average(scores))
```

```text
Average: 90.0
```

Now add an empty list and divide by it too:

```text
empty_scores = []
print("Average:", average(empty_scores))
```

```text
Traceback (most recent call last):
  File "average.py", line 6, in <module>
    print("Average:", average(empty_scores))
                      ~~~~~~~^^^^^^^^^^^^~~
  File "average.py", line 2, in average
    return sum(numbers) / len(numbers)
           ~~~~~~~~~~~~~^~~~~~~~~~~~~~
ZeroDivisionError: division by zero
```

The reproduction recipe is short and specific:

1. **The exact input** — `[80, 90, 100]` and then `[]`.
2. **The exact steps** — put the file in `average.py`, run `python average.py`.
3. **The exact output** — the traceback above, every time.
4. **What you expected** — a sensible answer (maybe `0`, maybe an error with a clear message).

When someone asks you to "reproduce" a bug, they are asking for exactly this. When *you* hit a bug
you cannot reproduce, it is often because you are changing several things at once. Change one thing,
run it, change the next.

---

## Where to put throwaway code

You will constantly want to try something without polluting your project. Keep a dedicated scratch
area:

```text
my-python-project/
├── scratch.py          <-- experiments live here, git-ignored if you like
├── README.md
└── src/
```

Use `scratch.py` for one-off experiments. When it gets messy, delete it and start again — it has
no value. When you start needing several files, make a `scratch/` folder inside your project.

**Notebooks are optional.** A Jupyter notebook (`.ipynb`) is a document that mixes code, output and
text in one file, and it is genuinely excellent for data analysis and for iterating on machine
learning models. But it is *not* how you write applications. For this course, plain `.py` files
are enough for everything until [17 Python for AI and data](17-python-for-ai-and-data.md). Do not
install anything extra yet.

One habit worth starting now: keep your experiments in a folder that is **not** the folder you will
ship. You will not accidentally `import scratch` from somewhere weird.

---

## Keyboard shortcuts that matter

These are VS Code shortcuts (macOS equivalents in brackets). You do not need to memorise them all —
use the first four and the rest will arrive.

| Shortcut | What it does | Why it matters |
|---|---|---|
| `Tab` / `Shift+Tab` | Indent / outdent the current line | Python's blocks are defined by indentation. Never type spaces by hand. |
| `Ctrl+/` [`Cmd+/`] | Toggle a `#` comment on the selected lines | The fastest way to try something without deleting code. |
| `Ctrl+S` [`Cmd+S`] | Save | Python does not auto-save in the terminal. The classic beginner error is running an unsaved file. |
| `Ctrl+Space` | Autocomplete / IntelliSense | Shows what functions exist, their arguments and their docstrings. |
| `Ctrl+F5` [`Cmd+F5`] | Run the current file without the debugger | The "run" key for scripts. `F5` starts the debugger, which you do not need yet. |
| `Ctrl+Shift+P` [`Cmd+Shift+P`] | Command palette — type any command | The escape hatch for everything you forget. |
| `Ctrl+Shift+F` [`Cmd+Shift+F`] | Search the whole folder | Find every place a variable or function is used. |
| `Alt+Shift+F` | Format the document | Auto-fixes spacing and indentation to the standard style. |

---

## 🧪 Try it yourself

Do these in order. Each one builds on the last.

### Exercise 1 — Same answer, two ways

Run this from your terminal:

```bash
python -c "print(2 ** 10)"
```

Then start the REPL with `python` and run `2 ** 10` with no `print()` at all. Write one sentence
answering: why did you need `print()` in the first case and not the second?

<details>
<summary>Hint</summary>

One of them is running a *script* (a whole program, which produces no output unless you ask for it).
The other is a *live session* that displays the value of every expression you type.

</details>

<details>
<summary>Solution</summary>

`python -c "..."` runs a complete program. A program that evaluates `2 ** 10` and throws the result
away prints nothing — you must call `print()` to see it. In the REPL, Python displays the value of
each expression automatically, so `2 ** 10` shows `1024` with no help.

</details>

### Exercise 2 — Catch a traceback on purpose

Create a file called `bug.py` containing exactly this:

```python
def greet(name):
    return "Hello, " + name + "!"


greeting = greet("Ada")
print(greeting)
```

Run it with `python bug.py` — it works. Now change the `"Ada"` on the last-but-one line to the
number `42` (no quotes) and run it again. Then answer these in a text file:

1. What is the **last line** of the output?
2. What is the **line number** in your file where the crash happened?
3. What is the **error type**?
4. Put the quotes back and run it a third time. What does it print?

<details>
<summary>Hint</summary>

The answer to question 2 is in the traceback, in the `File "...", line N, in greet` line. Question 4
should print `Hello, Ada!`.

</details>

<details>
<summary>Solution</summary>

1. `TypeError: can only concatenate str (not "int") to str`
2. Line 2 — the line with `return "Hello, " + name + "!"`
3. `TypeError`
4. `Hello, Ada!`

The `^` marker on line 2 points at the `+`, and the `~` regions beside it cover the string
literal and the `name` variable — which held the integer `42` rather than a string.

</details>

### Exercise 3 — Print your way to the answer

Write a file `debug_me.py`:

```python
name = "  Ada  "

print(name)
print(repr(name))
print(len(name))
```

Run it. Then write down how many characters the string actually has, and how `repr()` revealed the
spaces that `print()` hid.

<details>
<summary>Hint</summary>

`repr()` puts quotes around the string, so a trailing space looks like `'  Ada  '` instead of
`  Ada  `.

</details>

<details>
<summary>Solution</summary>

```text
  Ada
'  Ada  '
7
```

`repr()` made the invisible spaces visible: the string is `'  Ada  '` — two spaces, three letters,
two spaces. `len()` confirms it: 7 characters, not 3. The `print()` output looked like it had 3
letters because trailing spaces are invisible on a terminal.

</details>

### Exercise 4 — Reproduce a bug on purpose

Write `repro.py`:

```python
def first_char(text):
    return text[0]


print(first_char("hello"))
```

Run it — it works. Now add one more line at the bottom:

```text
print(first_char(""))
```

Run it again and it crashes. Then write the "reproduction recipe" for this bug in four lines: the
exact input, the exact steps, the exact output, and what you expected instead.

<details>
<summary>Hint</summary>

The recipe should be reproducible by someone who has never seen your code — name the file, the
command, and paste the error message.

</details>

<details>
<summary>Solution</summary>

```text
1. Input: the empty string "" passed to first_char().
2. Steps: save the code as repro.py, then run `python repro.py`.
3. Output: IndexError: string index out of range, with a traceback pointing at
   `return text[0]` on line 2.
4. Expected: either a clear error message saying the string is empty, or a
   sensible default such as "".
```

</details>

### Exercise 5 — Write a question an AI assistant can answer

Take the `greet.py` bug from Exercise 2 and write a prompt for an AI assistant that includes the
code, the full traceback, what you expected, and what actually happened. Then paste it into any AI
assistant and check whether its answer is actually correct by running the code it gives you.

<details>
<summary>Hint</summary>

Follow the four-part structure from the "How to ask a good question" section above. If the
assistant's answer does not work, it is because the question was missing something — go back and
add it.

</details>

<details>
<summary>Solution</summary>

A strong prompt looks like this:

> Python 3.13, Windows. Here is my code:
>
> ```python
> def greet(name):
>     return "Hello, " + name + "!"
>
>
> greeting = greet(42)
> print(greeting)
> ```
>
> Full traceback:
>
> ```text
> Traceback (most recent call last):
>   File "greet.py", line 5, in <module>
>     greeting = greet(42)
>   File "greet.py", line 2, in greet
>     return "Hello, " + name + "!"
>            ~~~~~~~~~~^~~~~~
> TypeError: can only concatenate str (not "int") to str
> ```
>
> I expected a greeting. Instead I get a TypeError. I think the problem is that `name` is an
> integer, not a string. Should I convert it with `str()`, or should I change the caller to pass
> `"42"`? Which is better design, and why?

Note the last question — it asks the assistant to *explain and compare*, not just to paste a fix.
And the final step (running the code it gives you) is the one people skip.

</details>

---

## ✅ Checkpoint

Answer these without looking back. If you cannot answer one, go re-read the section it came from.

1. What are the three ways to run Python, and when would you pick each one?
2. A script prints this traceback. Which line tells you *what actually went wrong*?
3. In a traceback, what do `File "...greet.py", line 5, in <module>` mean?
4. What is the difference between `print("hello")` and `print(repr("hello "))`?
5. Why do you search for the whole last line of a traceback instead of just the error name?
6. What three things belong in a good question to an AI assistant?
7. What does it mean to *reproduce* a bug?
8. Why is `scratch.py` a better home for experiments than a file inside your project package?

<details>
<summary>1. The three ways to run Python</summary>

The interactive REPL (`python`, then type expressions) for one-off questions and instant feedback;
a `.py` script run from the terminal (`python hello.py`) for code you want to keep; and an editor
such as VS Code with the Python extension for writing and editing real files.

</details>

<details>
<summary>2. Which line tells you what went wrong</summary>

The **last line** — the one that names the error type and describes the problem, such as
`TypeError: can only concatenate str (not "int") to str`. That is why you read a traceback from the
bottom up.

</details>

<details>
<summary>3. What the File line means</summary>

The file the crash happened in, the line number inside that file, and the function that line was in.
`<module>` means top-level code — the line was not inside any function.

</details>

<details>
<summary>4. print vs repr</summary>

`repr()` shows the *representation* of a value: quotes around strings, hidden leading or trailing
spaces shown, and `None` spelled out. `print()` renders a string for a human, so whitespace is
invisible.

</details>

<details>
<summary>5. Why search the whole line</summary>

The full message is far more specific than the error name, so it finds the exact case you hit
instead of thousands of unrelated pages. `TypeError` alone matches every type error ever written.

</details>

<details>
<summary>6. The three parts of a good question</summary>

The code (smallest snippet that shows the problem), the **full** traceback, and the gap between
what you expected and what actually happened. Add what you already tried, and always verify the
answer by running it.

</details>

<details>
<summary>7. Reproducing a bug</summary>

Making the faulty behaviour happen again, on purpose and reliably, so you can watch it and work
out the cause. If you cannot reproduce it, you cannot diagnose it.

</details>

<details>
<summary>8. Why scratch.py</summary>

Experiments in `scratch.py` are disposable and cannot accidentally be imported by the code you ship.
It keeps junk out of your package and out of your commits.

</details>

---

## 🐛 Common mistakes

| Mistake | What you see | Fix |
|---|---|---|
| Reading the traceback from the top | You get stuck on `Traceback (most recent call last):` and learn nothing | Read from the **bottom up**; the last line is the diagnosis |
| Running a file you never saved | The old output appears again and you think nothing changed | `Ctrl+S` before every run — the terminal never autosaves |
| `python script.py` from the wrong directory | `python: can't open file '...': No such file or directory` | `pwd` (Windows: `cd`) to check where you are, then `cd` into the folder with the file |
| Typing `python` and getting "command not found" | Windows: `'python' is not recognized...` | Reinstall and tick **"Add python.exe to PATH"** — see [01 Getting started](01-getting-started.md) |
| Pasting a traceback but trimming it | The assistant asks for the full traceback again | Copy the whole block from `Traceback` to the last line |
| Assuming `print(x)` shows you everything | A trailing space is invisible and you chase a phantom bug | Use `print(repr(x))` when whitespace or `None` matters |
| Using `python3` on Windows, or `python` on some Linux distros | "command not found" | Try the other one: `python`, `python3`, and `py` on Windows |
| Pasting a prompt into the REPL | The REPL executes it as Python and throws a `SyntaxError` | Paste code into a `.py` file and run it with `python file.py` |

---

## 🔗 Resources

- [The official Python tutorial](https://docs.python.org/3/tutorial/) — the canonical beginner
  course, written by the Python core team; it is dense but authoritative
- [Python: Getting Started](https://docs.python.org/3/using/index.html) — the official installation
  and first-steps guide for every operating system
- [Python standard library reference: `traceback`](https://docs.python.org/3/library/traceback.html)
  — the full documentation of tracebacks, including how to format and print them yourself
- [Handling Exceptions in Python](https://docs.python.org/3/tutorial/errors.html) — why Python's
  errors look the way they do, and how to catch them on purpose
- [Python Tutor](https://pythontutor.com/) — paste your code and watch each line execute; the best
  single debugging tool for a beginner
- [The Python Language Reference](https://docs.python.org/3/reference/index.html) — the precise,
  formal rules of the language; read it when the tutorial is not enough
- [PEP 8 — Style Guide for Python Code](https://peps.python.org/pep-0008/) — the official style
  rules; even beginners should follow it so their code is readable by everyone
- [Download Python](https://www.python.org/downloads/) — the official installers for Windows, macOS
  and Linux
- [CPython on GitHub](https://github.com/python/cpython) — the source code of the interpreter you
  will be using; the "Issues" and "Discussions" tabs are a great place to see how bugs are reported
- [An explanation of Python's error messages](https://docs.python.org/3/library/exceptions.html) —
  the complete list of built-in exception types and what each one means

---

## ➡️ Next

- [01 Getting started](01-getting-started.md) — install Python on your machine, meet the REPL, write
  and run your first script, and find out what Python actually does when it runs your code

**← Previous:** [Course guide](guide.md)
