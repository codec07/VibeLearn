# Getting Started

This chapter gets Python onto your computer and into your hands. You will install it, run it three
different ways, write your first script, and — because a lot of beginners find this mysterious —
find out what actually happens between "I pressed run" and "my program printed something". Nothing
here is hard. It is just new.

> **⏱️ Time:** ~25 minutes
> **📚 Prereqs:** [00 How to use this course](00-how-to-use-this-course.md)
> **🎯 By the end you can:** install Python 3.12 or newer, run code in the terminal, the REPL and
> VS Code, and explain in one sentence what the interpreter does with your `.py` file

---

## Why this matters for AI engineering

Every AI system you will build in this repository is a Python program that calls other Python
programs — PyTorch, Hugging Face Transformers, the OpenAI SDK, pandas, your own agent loop. Your
environment is part of your product: if `pip install` resolves to the wrong Python, or a virtual
environment is missing, nothing works and the error messages are baffling. Installing cleanly and
knowing which interpreter is running is the difference between a five-minute fix and an afternoon
lost to a virtual environment that was never activated.

---

## 1. What Python is

Python is a **high-level, interpreted, general-purpose programming language**. "High-level" means
you write instructions close to how a human thinks rather than close to how the CPU works.
"Interpreted" means a program called the **interpreter** reads your source code and executes it,
instead of you compiling it into machine code first. "General-purpose" means it is not designed for
one special job — it is used for web backends, games, spreadsheets, scientific computing, automation
and AI.

It is **dynamically typed** (a variable's type is decided by what you put in it, not by what you
declare) and it comes with a very large **standard library** of ready-made tools — file handling,
dates, JSON, HTTP, maths — plus tens of thousands of third-party packages you can install with one
command.

### What Python is good at

- **Text and data processing.** Splitting, cleaning and reshaping messy data is a two-line job.
- **Automation.** Renaming 10,000 files, calling an API 10,000 times, scraping a report every
  morning.
- **Writing things fast.** Python is close to English, so you spend your time on the problem rather
  than on the syntax.
- **Gluing.** Python is the standard language for calling into C, C++, Rust or CUDA — which is
  exactly what makes it the standard language for AI.

### Why it is the language of AI

Almost every published model ships as a Python package. PyTorch, TensorFlow, scikit-learn, NumPy,
pandas, Hugging Face Transformers, LangChain, the OpenAI Python SDK, vLLM, llama.cpp — all of them
are Python packages you install with `pip`. If you want to fine-tune a model, serve it, build a
RAG pipeline or write an agent loop, you are writing Python.

---

## 2. Installing Python

You want **Python 3.12 or newer**. Older versions (3.8, 3.9) are still in the wild but lack modern
syntax and the best typing support. Newer versions (3.13, 3.14) are fine.

### Windows

**Option A — `winget`, the Windows package manager (recommended).**

`winget` is the built-in Windows package manager. Open **PowerShell** (press `Win`, type
"PowerShell", press Enter) and run:

```bash
winget install -e --id Python.Python.3.13
```

That is it. When it finishes, close and reopen PowerShell so the new `PATH` entry is picked up.

**Option B — the official installer.** If `winget` is unavailable (it is missing on Windows 7 and on
some locked-down corporate machines):

1. Go to [python.org/downloads](https://www.python.org/downloads/).
2. Click the big yellow **Download Python 3.13.x** button for Windows.
3. Run the installer.
4. **Tick the box labelled "Add python.exe to PATH"** on the very first screen.

> **The classic beginner trap**
>
> If you skip that box, the install "works" — the installer says success — but the terminal has no
> idea where Python is. Every later command fails with
> `'python' is not recognized as an internal or external command`. The fix is not to reinstall
> everything: either re-run the installer and tick the box, or add the folder
> `C:\Users\<your-name>\AppData\Local\Programs\Python\Python313\` to your `PATH` by hand.
>
> Take the screenshot of that installer window. When something breaks in three weeks, you will be
> glad you know what you ticked.

Windows also installs a **`py` launcher**, which always points at a sensible Python regardless of
`PATH` ordering:

```bash
py --version
py hello.py
```

Avoid the "Python 3.x (Microsoft Store)" entry in the Windows Store. It runs inside a sandboxed
container, it is invisible to most tools, and it has caused confusing problems for beginners for
years.

### macOS

**Option A — Homebrew (recommended if you already use it).** Install [Homebrew](https://brew.sh/)
first, then:

```bash
brew install python
python3 --version
```

**Option B — the python.org installer.** Download the "macOS 64-bit universal2 installer" from
[python.org/downloads/macos](https://www.python.org/downloads/macos/) and run it.

> **The macOS caveat**
>
> The python.org installer places Python in `/Library/Frameworks/` and puts it *ahead* of Homebrew in
> your `PATH`. If you later run `brew install` for something that depends on Python, Homebrew may
> build against the framework Python instead of its own, and you can end up with two Pythons that
> disagree. Pick one and stick with it. If you already have Homebrew, use Homebrew.
>
> Separately, macOS ships a stub `python3` that prompts you to install the Xcode Command Line Tools.
> That stub is not a real Python — ignore it and use the one you installed.

Whichever route you take, verify with `python3 --version`. Some scripts expect the command to be
`python`; you can make that permanent by adding an alias to your shell profile:

```bash
echo 'alias python=python3' >> ~/.zshrc
```

### Linux

**Debian / Ubuntu:**

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv
```

**Fedora / RHEL / Rocky:**

```bash
sudo dnf install -y python3 python3-pip
```

**Arch:**

```bash
sudo pacman -S python
```

> **The distro caveat**
>
> The Python your distribution ships is often older than 3.12 — Ubuntu 22.04 ships 3.10, Ubuntu
> 24.04 ships 3.12. That is fine for learning, but some modern packages (and everything in Arc 4
> of this course) want 3.12 or newer. If `python3 --version` is too old, install a newer one with
> [pyenv](https://github.com/pyenv/pyenv) or [uv](https://docs.astral.sh/uv/). Both are covered in
> [12 Environments and tooling](12-environments-and-tooling.md).

---

## 3. Verify the install

Run these three commands:

```bash
python --version
python3 --version
python -c "print('Python is alive')"
```

```text
Python 3.13.1
Python 3.13.1
Python is alive
```

If `python` says "command not found" but `python3` works, your machine is fine — just use `python3`
(or the `py` launcher on Windows).

### Which Python is actually running?

This matters more than it looks. You can have four Pythons installed and only one of them is on
your `PATH`.

```bash
python -c "import sys; print(sys.executable)"
```

```text
C:\Python313\python.exe
```

That is the exact file doing the work. On macOS and Linux the equivalent is
`/usr/local/bin/python3` or `/opt/homebrew/bin/python3`.

To see every Python the shell can find:

```bash
where python        # Windows
which python3       # macOS and Linux
```

```text
C:\Python313\python.exe
C:\Program Files\Python313\python.exe
```

Two answers means two installations. The **first** one in the list is the one that wins. If the
first one is an old version, that is the bug.

---

## 4. The interactive prompt (the REPL)

Start it by running `python` (or `python3`) with no file name:

```bash
python
```

```text
Python 3.13.1 (tags/v3.13.1:0671451, Dec  3 2024, 19:06:28) [MSC v.1942 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> 
```

The `>>>` is the **prompt**. Python is waiting for you to type something and press Enter.

```text
>>> 2 + 2
4
>>> name = "Ada"
>>> name
'Ada'
>>> print(name)
Ada
```

Notice that `name` on its own printed `'Ada'` — with quotes. The REPL shows you the *value* of an
expression, and for a string that includes the quotes. `print(name)` shows you the *rendered*
text instead.

### Multi-line blocks

The REPL uses a second prompt, `...`, when a statement is not finished. This happens with
`for` loops, `if` blocks, and function definitions. When Python needs more input, the prompt
changes from `>>>` to `...`:

```text
>>> total = 0
>>> for number in range(1, 6):
...     total = total + number
...     print(number, total)
...
1 1
2 3
3 6
4 10
5 15
>>> total
15
```

The block ends when you press Enter on an **empty line** — that is what the lone `...` followed by
Enter means. If you get stuck in a `...` prompt, press `Ctrl+C` to cancel the block and get your
`>>>` back.

### Leaving the REPL

Type `.exit()` and press Enter. `exit()` and `quit()` also work, and `Ctrl+D` (macOS/Linux) or
`Ctrl+Z` then Enter (Windows) does the same thing.

### REPL versus script

| | REPL | Script (`.py` file) |
|---|---|---|
| Value of an expression | Displayed automatically | Nothing is displayed — you need `print()` |
| What you typed | Kept in session history, gone when you close | Saved on disk forever |
| Imports and variables | Stay alive between lines | Start fresh every run |
| An error | Prints a traceback and keeps going | Stops the program |
| Good for | Trying things, poking at values | Anything you want to keep |

Because the REPL remembers everything, it can hide a bug: you might define a variable in one line
and use it twenty lines later, and then the same code fails when you put it in a script. When you
move code from the REPL into a file, make sure it still works from the top.

---

## 5. Your first script

Create a file called `hello.py` and put this in it:

```python
print("Hello, world!")
```

Run it from the terminal, in the folder that contains the file:

```bash
python hello.py
```

```text
Hello, world!
```

Make it slightly more interesting — this is the script we will grow over the next few chapters
(the `f"..."` prefix is an **f-string**, the modern way to put a variable inside a string; it is
explained properly in [02 Syntax and variables](02-syntax-and-variables.md)):

```python
name = "Ada"
greeting = f"Hello, {name}!"

print(greeting)
print(f"Your name is {len(name)} characters long.")
```

```text
Hello, Ada!
Your name is 3 characters long.
```

### The shebang line

On macOS and Linux you can start a script directly with `./hello.py`, but only if the first line
tells the operating system which interpreter to use. That line is the **shebang**:

```python
#!/usr/bin/env python3
print("Hello, world!")
```

Then make it executable and run it:

```bash
chmod +x hello.py
./hello.py
```

`chmod` changes the file's permissions. `+x` adds "executable". Windows ignores the shebang
completely, which is why you can leave it in and the file still works everywhere.

---

## 6. What Python actually does when it runs your code

This section is short on purpose, but it answers a question every beginner has: *when I press run,
what actually happens?*

```text
   hello.py  (your source code, plain text)
        |
        |  1. tokenise + parse
        v
   an AST  (the structure of your program)
        |
        |  2. compile
        v
   bytecode  (low-level instructions, like an assembly for the VM)
        |
        |  3. stored in a cache
        v
   __pycache__/hello.cpython-313.pyc
        |
        |  4. execute
        v
   the CPython virtual machine runs the instructions
        |
        v
   output on your screen
```

Step by step:

1. **Read and parse.** Python reads your file as text, splits it into *tokens* (names, operators,
   keywords), and checks the grammar. If the grammar is wrong you get a `SyntaxError` — and the
   program never runs at all.
2. **Compile to bytecode.** The parsed program is turned into a compact set of low-level
   instructions. This is the same kind of thing a Java virtual machine or .NET runtime does.
3. **Cache the bytecode.** Python writes it next to your source file, in a folder called
   `__pycache__`. Next time you run the file, it loads the cached bytecode instead of recompiling.
4. **Execute.** The CPython virtual machine runs the instructions.

You can watch step 2 happen with the standard-library `dis` module, which **disassembles** bytecode
back into a readable listing:

```python
import dis


def add(a, b):
    return a + b


dis.dis(add)
```

```text
  4           RESUME                   0

  5           LOAD_FAST_LOAD_FAST      1 (a, b)
              BINARY_OP                0 (+)
              RETURN_VALUE
```

Read it as: "load the two parameters, add them, return the result". The exact instruction names
change between Python versions — Python 3.13 loads both arguments in one step, Python 3.12 does it
in two — but the shape is always *load, operate, return*.

### Where `__pycache__` comes from

After running `hello.py`, you will see a new folder appear next to it:

```text
python-basics/
├── hello.py
└── __pycache__/
    └── hello.cpython-313.pyc
```

The `.pyc` file is the cached bytecode. The `cpython-313` part means "built by CPython 3.13".

**It is completely safe to delete.** Python will just rebuild it next time you run the file. It is
normally listed in `.gitignore` because it is a build artefact — it should never be committed to
Git.

You can also compile a snippet by hand, without a file:

```python
source = "answer = 6 * 7"
compiled = compile(source, "demo.py", "exec")

print("Type of the compiled result:", type(compiled).__name__)
print("Size of the bytecode, in bytes:", len(compiled.co_code))

exec(compiled)
print("answer =", answer)
```

```text
Type of the compiled result: code
Size of the bytecode, in bytes: 8
answer = 42
```

`compile()` turns source text into a code object; `exec()` runs a code object. That is exactly what
Python does behind the scenes when you run a file.

---

## 7. `python -m module` — the more reliable way to run things

You can run a module as a program by putting `-m` before its name:

```bash
python -m pip install requests
python -m pytest
python -m json.tool settings.json
```

`python -m pytest` means "find the `pytest` module, and run it as a program". You will meet
`python -m pytest` in [13 Testing](13-testing.md).

### Why it is better than `python script.py`

| | `python script.py` | `python -m package.module` |
|---|---|---|
| Which directory goes on `sys.path` | The folder containing the script | The **current** working directory |
| Do you need to know the file path | Yes | No — just the module name |
| If the tool is not installed | `No such file or directory` | `No module named 'tool'` — the message tells you what to install |

That first row is the important one. `sys.path` is Python's list of folders it searches when you
write `import something`. Running a script directly puts the script's own folder on that list, which
means your project package may not be importable. Running with `-m` puts the folder you are
standing in on the list, which is what you almost always want.

**Rule of thumb:** use `python -m <tool>` for any tool you did not write yourself, and
`python <script>.py` for your own scripts.

---

## 8. A preview of `if __name__ == "__main__":`

You will see this pattern in almost every Python file ever written, including every example in
this course:

```python
def greet(name):
    return f"Hello, {name}!"


if __name__ == "__main__":
    print(greet("Ada"))
```

Run it directly and it prints `Hello, Ada!`.

Here is the one-line teaser: **Python sets the built-in variable `__name__` to `"__main__"` when the
file is run as a program, and to the module's own name when the file is imported by something
else.** So the block inside the `if` runs only when you execute the file, and is skipped when
another file imports it.

That is the whole trick. The full explanation — including `__name__`, `__file__`, and how the
`if __name__ == "__main__":` block became the universal entry-point convention — is in
[08 Modules and packages](08-modules-and-packages.md).

Try this right now to see it work. Create `greeter.py`:

```python
def greet(name):
    return f"Hello, {name}!"


print("This line runs every time the file is imported.")
print("__name__ is:", __name__)

if __name__ == "__main__":
    print("This line runs only when the file is executed directly.")
```

Run it with `python greeter.py` and you get:

```text
This line runs every time the file is imported.
__name__ is: __main__
This line runs only when the file is executed directly.
```

Now create a **second** file, `use_greeter.py`, in the same folder. It is shown here as plain text
because it only makes sense next to `greeter.py`:

```text
# use_greeter.py
from greeter import greet

print(greet("Grace"))
```

Run `python use_greeter.py` and you get:

```text
This line runs every time the file is imported.
__name__ is: greeter
Hello, Grace!
```

The last line of `greeter.py` did **not** print, because when it was imported, `__name__` was
`"greeter"`, not `"__main__"`.

---

## 9. VS Code and the Python extension

VS Code is a free code editor by Microsoft. The Python extension adds syntax highlighting,
autocomplete, debugging and a run button.

**Install:**

1. Download and install [VS Code](https://code.visualstudio.com/).
2. Open VS Code. Click the **Extensions** icon in the left sidebar (or press `Ctrl+Shift+X` /
   `Cmd+Shift+X`).
3. Search for `Python`, and install **"Python" by Microsoft** (`ms-python.python`).
4. While you are there, install **"Pylance"** by Microsoft too — it is the fast autocomplete and
   type-checking engine.

**Set up your project:**

1. Make a folder on your machine, e.g. `python-basics`.
2. **File → Open Folder** and choose it. Opening the *folder*, not just the file, is what makes
   VS Code's features work properly.
3. Create a file inside it: right-click in the Explorer panel → **New File** → name it `hello.py`.
4. **Select the interpreter.** Press `Ctrl+Shift+P` (`Cmd+Shift+P` on macOS), type
   `Python: Select Interpreter`, and pick the Python 3.13 you installed. VS Code guesses wrong
   surprisingly often, and a wrong choice here is the cause of most "it works in the terminal but
   not in VS Code" problems.
5. Press the **▷ Run Python File** button in the top-right of the editor, or press `Ctrl+F5`
   (`Cmd+F5`).

**The integrated terminal.** Press `` Ctrl+` `` (`` Cmd+` `` on macOS) to open a terminal inside
VS Code, at the bottom of the window. It starts in your project folder, which means `python
hello.py` works there without any `cd`.

---

## 10. Working from the terminal

Four commands do almost all the work:

```bash
pwd          # print working directory — where am I?
ls           # list files (macOS, Linux)
dir          # list files (Windows, and PowerShell)
cd           # change directory
```

```text
$ pwd
/home/ada/python-basics
$ ls
hello.py  notes.txt
$ cd notes
$ pwd
/home/ada/python-basics/notes
$ cd ..
```

On Windows PowerShell, `pwd` and `ls` work as aliases for `Get-Location` and `Get-ChildItem`, so
the same commands work in all three terminals. `cd ..` goes up one level.

### Running from the right directory

This is the single most common beginner problem. `python hello.py` looks for `hello.py` in your
**current working directory**, not in the folder where the script lives.

```text
$ python hello.py
python: can't open file '/home/ada/desktop/hello.py': [Errno 2] No such file or directory
```

Three ways to fix it:

1. `cd` into the folder that contains the file, then run it.
2. Give the full path: `python ~/python-basics/hello.py`.
3. Open the folder in VS Code and use the integrated terminal, which starts in the right place.

**Check first.** If a script "does not exist" but you can see it, run `pwd` and `ls`. Ninety
seconds of checking saves an hour of reinstalling Python.

---

## 🧪 Try it yourself

### Exercise 1 — Install, verify, and report

Install Python using the instructions for your operating system. Then run all of these and write
down the output of each:

```bash
python --version
python -c "import sys; print(sys.executable)"
python -c "import sys; print(sys.platform)"
python -c "print(2 ** 100)"
```

The last one prints a 31-digit number — the largest power of two that fits in 128 bits. Write down
the exact path from the second command. That path is the interpreter that will run all your code.

<details>
<summary>Hint</summary>

If `python` is not recognised but `python3` is, use `python3` for the rest of the chapter. On
Windows, `py` also works.

</details>

<details>
<summary>Solution</summary>

The output should look something like this (your paths, versions and platform will differ):

```text
Python 3.13.1
C:\Python313\python.exe
win32
1267650600228229401496703205376
```

The key line is the second one — the absolute path of the interpreter. If that path looks
unexpected, fix it now, before you install any packages.

</details>

### Exercise 2 — Live in the REPL

Start the REPL and, without creating any file, do all of the following:

1. Calculate `17 ** 4`.
2. Assign `city = "Lagos"` and then print the number of characters in it.
3. Write a three-line `for` loop that prints the squares of 1, 2, 3, 4.
4. Make a deliberate mistake — divide by zero — and read the traceback from the bottom up.
5. Type `.exit()`.

Write down the exact error message from step 4.

<details>
<summary>Hint</summary>

After typing `for number in range(1, 5):` the prompt becomes `...`. Press Enter on an empty line to
end the block.

</details>

<details>
<summary>Solution</summary>

```text
>>> 17 ** 4
83521
>>> city = "Lagos"
>>> len(city)
5
>>> for number in range(1, 5):
...     print(number ** 2)
...
1
4
9
16
>>> 1 / 0
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ZeroDivisionError: division by zero
>>> .exit()
```

The last line is the answer: `ZeroDivisionError: division by zero`. Note `File "<stdin>", line 1` —
`<stdin>` means "code you typed directly into the REPL", and there is no file to open.

</details>

### Exercise 3 — A script that runs from anywhere

Create a folder called `python-basics` and put this inside it as `hello.py`:

```python
name = "Ada"
greeting = f"Hello, {name}!"

print(greeting)
print(f"Your name is {len(name)} characters long.")
```

1. `cd` into that folder and run `python hello.py`.
2. `cd` to your home directory (or another folder) and try to run it again. Read the error.
3. Run it using the full path instead.
4. Add `import os` at the top of the file, and a `print()` line that reports the current folder:
   `print(os.getcwd())`.

<details>
<summary>Hint</summary>

`os.getcwd()` means "get the current working directory".

</details>

<details>
<summary>Solution</summary>

Step 1 prints:

```text
Hello, Ada!
Your name is 3 characters long.
```

Step 2 fails with something like:

```text
python: can't open file '/home/ada/hello.py': [Errno 2] No such file or directory
```

Step 3 works: `python ~/python-basics/hello.py`.

Step 4 prints the folder you are standing in, which explains why step 2 failed — you were somewhere
else entirely. This is the habit that saves you: **when a script "does not exist", print the
directory before you change anything.**

</details>

### Exercise 4 — Catch the cache

1. Run `python hello.py` from inside `python-basics`.
2. List the directory. Find the `__pycache__` folder.
3. Look inside it and note the file name.
4. Delete the whole `__pycache__` folder.
5. Run `python hello.py` again. Does it still work? Does `__pycache__` come back?

<details>
<summary>Hint</summary>

On Windows use `dir` and `del /s /q __pycache__` (or just delete it in your file browser). On
macOS/Linux use `ls` and `rm -rf __pycache__`.

</details>

<details>
<summary>Solution</summary>

Yes — the script still works, and yes, the folder comes back. That is the point: `__pycache__` is a
**cache**, not part of your program. Python rebuilds it because it needs the bytecode again. The
file inside is named something like `hello.cpython-313.pyc`, where `cpython-313` tells you which
Python version built it.

</details>

### Exercise 5 — Look at the bytecode

Create `bytecode_demo.py`:

```python
import dis


def add(a, b):
    return a + b


def shout(text):
    return text.upper()


dis.dis(add)
dis.dis(shout)
```

Run it. Then, using the [Python Tutor](https://pythontutor.com/) visualiser, paste the two
functions and step through them. Write one sentence describing what the `LOAD_FAST_LOAD_FAST`
instruction does.

<details>
<summary>Hint</summary>

`LOAD_FAST` means "put the value of a local variable on the stack". In Python 3.13 two of them are
combined into one instruction.

</details>

<details>
<summary>Solution</summary>

The output for `shout` looks like this:

```text
  8           RESUME                   0

  9           LOAD_FAST                0 (text)
              LOAD_ATTR                1 (upper + NULL|self)
              CALL                     0
              RETURN_VALUE
```

`LOAD_FAST_LOAD_FAST` pushes the values of the local variables `a` and `b` onto the stack — the
working area where the interpreter keeps the values it is about to operate on. `BINARY_OP 0 (+)`
then pops them both, adds them, and pushes the sum. `RETURN_VALUE` hands the result back to
whoever called `add`.

</details>

### Exercise 6 — Set up VS Code

1. Install VS Code and the Python extension.
2. Open your `python-basics` **folder**.
3. Select the interpreter: `Ctrl+Shift+P` → `Python: Select Interpreter` → choose Python 3.13.
4. Open `hello.py`, change the name to your own, and press the ▷ Run button.
5. Open the integrated terminal with `` Ctrl+` `` and run `python hello.py` from there too.

<details>
<summary>Hint</summary>

If the ▷ button is missing, the Python extension is not installed or the file is not recognised as
Python. Check the Extensions panel and the bottom-right status bar.

</details>

<details>
<summary>Solution</summary>

After step 4 the Output panel shows:

```text
Hello, Ada!
Your name is 3 characters long.
```

After step 5 the terminal shows the same two lines. If the terminal shows a different result than
the ▷ button, you have two different interpreters selected — check the interpreter setting again.
That mismatch is the classic VS Code beginner problem.

</details>

---

## ✅ Checkpoint

1. What version of Python does this course need, and why not something older?
2. You install Python on Windows and the terminal says `'python' is not recognized`. What did you
   most likely forget to tick?
3. What are the two commands you can use to find out which Python the terminal is using?
4. In the REPL, why do you not need `print()` to see the value of `2 + 2`?
5. What does the `...` prompt mean, and how do you end a multi-line block?
6. What are the three steps that happen between "I run `hello.py`" and "it prints", and what is
   `__pycache__` — is it safe to delete?
7. What is the difference between `python script.py` and `python -m package.module`?
8. What does `if __name__ == "__main__":` actually check?

<details>
<summary>1. Version needed</summary>

Python **3.12 or newer**. Older versions lack modern syntax, the best typing support, and the
newest versions of most AI packages.

</details>

<details>
<summary>2. The forgotten checkbox</summary>

**"Add python.exe to PATH"** on the first screen of the python.org installer. The install succeeds
but the terminal cannot find the interpreter. Re-run the installer and tick it, or add
`C:\Users\<you>\AppData\Local\Programs\Python\Python313\` to your `PATH` by hand.

</details>

<details>
<summary>3. Finding the interpreter</summary>

`python -c "import sys; print(sys.executable)"` prints the exact path of the interpreter that will
run your code. `where python` (Windows) and `which python3` (macOS/Linux) list every candidate; the
first one wins.

</details>

<details>
<summary>4. Why no print needed in the REPL</summary>

The REPL **displays the value of every expression** you type. A script does not — it just evaluates
and throws the result away, so you need `print()` to see it.

</details>

<details>
<summary>5. The ... prompt</summary>

`...` is the **continuation prompt**. It appears when Python needs more input to finish a statement,
such as the body of a `for` loop or `if` block. You end the block by pressing Enter on an empty
line. `Ctrl+C` cancels a block you are stuck in.

</details>

<details>
<summary>6. The three steps and __pycache__</summary>

1. **Parse** the source into a structured form (a syntax error here stops everything).
2. **Compile** it to bytecode, and cache that bytecode in `__pycache__`.
3. **Execute** the bytecode on the CPython virtual machine, producing your output.

`__pycache__` is the folder holding those cached `.pyc` bytecode files. It is a build artefact, it
is safe to delete (Python rebuilds it on the next run), and it should be in your `.gitignore`.

</details>

<details>
<summary>7. python script.py vs python -m module</summary>

`-m` runs an installed module **as a program**, using its module name instead of a file path, and it
puts your **current working directory** on `sys.path` (so your project package is importable).
`python script.py` puts the **script's own folder** on `sys.path` instead. For third-party tools
such as `pytest` or `pip`, prefer `python -m pytest` and `python -m pip`.

</details>

<details>
<summary>8. What the __main__ guard checks</summary>

Whether the current file is being **executed directly** as a program (in which case Python sets
`__name__` to `"__main__"`), rather than **imported** by another file (in which case `__name__` is
the module's own name). Full details in
[08 Modules and packages](08-modules-and-packages.md).

</details>

---

## 🐛 Common mistakes

| Mistake | What you see | Fix |
|---|---|---|
| Not ticking "Add python.exe to PATH" on Windows | `'python' is not recognized as an internal or external command` | Re-run the installer with the box ticked, or add the Python folder to `PATH` manually |
| Using the Microsoft Store version of Python | Tools cannot see it; `pip` behaves oddly; scripts fail to launch | Uninstall it and install from python.org or with `winget` |
| Expecting `python` on macOS/Linux | `command not found: python` | Use `python3`, or add `alias python=python3` to `~/.zshrc` |
| Running `python hello.py` from the wrong folder | `can't open file ... No such file or directory` | Run `pwd` and `ls`, then `cd` into the folder that has the file |
| Using the system Python on Linux instead of a newer one | `python3 --version` says 3.10, and modern packages refuse to install | Install 3.12+ with pyenv or uv |
| Forgetting to save before running | The old output appears and you think your edit was ignored | `Ctrl+S` first — the terminal never autosaves |
| Running `pip install` from the wrong Python | "Module not found" even though you just installed it | Use `python -m pip install <package>` so the install and the runtime always match |
| Committing `__pycache__` to Git | Noisy diffs and merge conflicts | Add `__pycache__/` and `*.pyc` to `.gitignore` |

---

## 🔗 Resources

- [Download Python](https://www.python.org/downloads/) — official installers for Windows, macOS and
  Linux, and the source code
- [Python: Getting Started](https://docs.python.org/3/using/index.html) — the official
  install-and-first-steps guide for every platform
- [Using Python on Windows](https://docs.python.org/3/using/windows.html) — the `py` launcher, PATH
  handling and Windows-specific behaviour
- [Using Python on macOS](https://docs.python.org/3/using/mac.html) — the framework installer, the
  `PATH` order and how to uninstall cleanly
- [Using Python on Unix](https://docs.python.org/3/using/unix.html) — distro packages, `pyenv` and
  the caveats about system Pythons
- [The Python tutorial](https://docs.python.org/3/tutorial/) — the official beginner course; start
  at the beginning and read it alongside this repository
- [An interactive tour of the Python interpreter](https://docs.python.org/3/tutorial/interactive.html)
  — everything the REPL can do, including `help()` and command history
- [Command line and environment options](https://docs.python.org/3/using/cmdline.html) — the full
  reference for `python`, `python -m`, `python -c`, and the environment variables that affect it
- [The `dis` module](https://docs.python.org/3/library/dis.html) — the official documentation for
  the bytecode disassembler you used in Exercise 5
- [VS Code: Python tutorial](https://code.visualstudio.com/docs/python/python-tutorial) — the
  official guide to using VS Code with Python
- [Python extension for VS Code](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
  — the Microsoft extension itself, with its feature list and settings
- [pyenv](https://github.com/pyenv/pyenv) — install and switch between any version of Python on
  Linux and macOS; your escape hatch when the distro Python is too old

---

## ➡️ Next

- [02 Syntax and variables](02-syntax-and-variables.md) — the actual language: indentation, names,
  assignment, operators, strings and f-strings

**← Previous:** [00 How to use this course](00-how-to-use-this-course.md)
