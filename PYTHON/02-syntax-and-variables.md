# Syntax and Variables

This chapter is the language itself. By the end of it you will know how to write a name, give it a
value, change that value, do arithmetic and text on it, and print the result so a human can read
it. Everything in the rest of the course is built on this file, so type the examples rather than
skimming them.

> **⏱️ Time:** ~35 minutes
> **📚 Prereqs:** [01 Getting started](01-getting-started.md)
> **🎯 By the end you can:** write valid Python with correct indentation, name things the way
> professional Python does, and build readable formatted output with f-strings

---

## Why this matters for AI engineering

In an AI codebase you spend far more time *handling text* than doing maths. Prompt templates,
model responses, tool-call arguments, JSON payloads — all of it is strings, and all of it needs to
be formatted, parsed and checked. f-strings and string handling are not "chapter 2 stuff"; they are
how you build a prompt, log what the model returned, and pull a field out of a tool response
without an IndexError. The naming rules in this chapter are the difference between code a colleague
can read and code they have to reverse-engineer at 2am.

---

## 1. Statements, indentation and blocks

A **statement** is one complete instruction. `price = 10` is a statement. `print(price)` is a
statement. Python runs one statement at a time, top to bottom.

Some statements introduce a **block** — a group of statements that only run under a condition, or
that run several times. In most languages a block is wrapped in curly braces `{ }`. Python has no
braces. **Indentation defines the block.**

```text
JavaScript / Java / C          Python
---------------------          -----
if (score > 50) {              if score > 50:
    print("pass");                print("pass")
    print("well done")            print("well done")
}                             print("done")
```

In Python, the block is everything indented under the line ending in a colon. The `:` is not
optional — it is Python's way of saying "a block follows".

```python
if True:
    print("This line is indented by four spaces")
    print("So is this one")

print("This line is not indented")
```

```text
This line is indented by four spaces
So is this one
This line is not indented
```

### The rules

1. Indent with **four spaces** per level. Never mix tabs and spaces — Python 3 raises
   `TabError: inconsistent use of tabs and spaces in indentation` when you do.
2. The **colon** at the end of the line introduces the block.
3. The **first line** of a program is not indented.
4. Blank lines do not end a block; the indentation does.

Your editor handles indentation for you. In VS Code, pressing `Enter` after a line ending in `:`
auto-indents the next line, and `Shift+Tab` moves back out. Never type a space four times by
hand — let the editor do it, and the indentation will always be consistent.

> **Tabs vs spaces:** some old codebases use tabs. Modern Python, and [PEP 8](https://peps.python.org/pep-0008/),
> say spaces only. In VS Code, set *Render Whitespace* to *All* (View → Appearance) and you will
> see the difference immediately.

---

## 2. Comments and docstrings

A **comment** is a note for humans. Python ignores everything from `#` to the end of the line.

```python
# Convert kilometres to miles.
# The conversion factor is exact to 6 decimal places.
distance_km = 12.5
distance_miles = round(distance_km * 0.621371, 2)   # Multiply by the conversion factor.

print(distance_miles)
```

```text
7.77
```

### Why comments are not "obvious" comments

A comment that repeats the code is noise:

```python
# Add 1 to total
total = 0
total += 1

print(total)
```

```text
1
```

That comment tells you nothing you cannot see. A **useful** comment explains the things the code
cannot say: *why* this value, *what* this edge case is, *what would break* if you changed it.

```python
# The API rejects requests faster than 60 per minute, so we sleep between calls.
RATE_LIMIT = 60

# Prices are stored in pence to avoid floating-point rounding errors.
price_pence = 1999

print(f"Rate limit: {RATE_LIMIT} per minute, price: {price_pence} pence")
```

```text
Rate limit: 60 per minute, price: 1999 pence
```

### Docstrings

A **docstring** is a string literal at the very top of a function, class or module. It documents
what the thing does, and — unlike a comment — it is stored in the object at runtime, so tools can
read it.

```python
def area(width, height):
    """Return the area of a rectangle.

    Both arguments must be numbers in the same unit.
    """
    return width * height


print(area.__doc__)
```

```text
Return the area of a rectangle.

    Both arguments must be numbers in the same unit.
```

Functions and classes are covered properly in [05 Functions](05-functions.md); this is just a
preview so you recognise the pattern when you see it.

---

## 3. Variables: names and values

A **variable** is a name that refers to a value stored in memory. A **value** is the actual piece
of data — a number, a piece of text, a list.

Think of a variable as a labelled box. The label is the name; the thing inside the box is the
value.

```text
   name = "Ada"        age = 36
        |                   |
        v                   v
   [ "Ada" ]           [  36  ]
    a string            an integer
```

You write the name on the left of an `=` and the value on the right:

```python
name = "Ada"
age = 36
is_learning = True

print(name)
print(age)
print(is_learning)
```

```text
Ada
36
True
```

The `=` sign is an **assignment operator**. It means "take the value on the right and stick it in
the box on the left". It does *not* mean "these are equal" — we get to that in
[03 Data types and operators](03-data-types-and-operators.md).

A variable can hold anything:

```python
price = 19.99
first_name = "Ada"
is_valid = True
nothing_yet = None          # None means "no value at all"
items = ["apple", "pear"]   # a list of things

print(price, first_name, is_valid, nothing_yet, items)
```

```text
19.99 Ada True None ['apple', 'pear']
```

---

## 4. Python is dynamically typed

**Dynamic typing** means the type of a variable is decided by the value you put in it, not by a
declaration you write. A name is just a label — it can be re-pointed at a completely different
kind of value later.

```python
value = 42
print(type(value))

value = "forty two"
print(type(value))

value = [42]
print(type(value))
```

```text
<class 'int'>
<class 'str'>
<class 'list'>
```

One name, three types over the life of the program. `type()` tells you what a value currently is.

This is a feature and a trap. It is a feature because you never have to declare types. It is a trap
because nothing stops you from reassigning a number variable to a string three lines later, and
then `value + 1` breaks.

**The habit to build now:** keep one variable meaning one thing. If you find yourself reassigning a
name to a different type, use a new name instead. You will meet **type hints** in
[11 Type hints and modern Python](11-type-hints-and-modern-python.md), which let you declare the
type you expect and have tools check it for you.

---

## 5. Naming rules

### What is a valid name

A **name** (technically an *identifier*) may contain letters, digits and underscores, and must not
start with a digit. It cannot be a Python keyword.

```python
first_name = "Ada"           # good
user2 = "grace"              # good
MAX_RETRIES = 3              # good
_private = "internal"        # allowed, with a special meaning

print(first_name, user2, MAX_RETRIES, _private)
```

```text
Ada grace 3 internal
```

And these are all errors:

```text
$total = 5                 # SyntaxError: names cannot contain $
2fast = "no"               # SyntaxError: names cannot start with a digit
my name = "no"             # SyntaxError: no spaces allowed
class = "no"               # SyntaxError: keyword cannot be used as identifier
```

Python is case-sensitive: `name`, `Name` and `NAME` are three different names.

### The conventions

These are the rules from [PEP 8](https://peps.python.org/pep-0008/#naming-conventions), the
official style guide that almost every Python project on Earth follows:

| Kind of thing | Convention | Example |
|---|---|---|
| Variables and functions | `snake_case` | `total_price`, `calculate_tax` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_RETRIES`, `API_KEY` |
| Classes | `CapWords` | `Invoice`, `OrderProcessor` |
| Methods | `snake_case` | `send_email`, `total_price` |
| Module names | short, `snake_case` | `order_utils`, not `OrderUtils.py` |

`snake_case` means lowercase words joined by underscores: `total_price`, not `totalPrice` and
definitely not `totalprice`.

A leading underscore is a **convention that means "private, do not touch"**. Python does not
enforce it — it is a promise to other humans reading your code. A double leading underscore
(`__name__`) is reserved by Python itself.

### Keywords you cannot use

Python has 35 reserved words. You cannot use them as names.

```python
import keyword

print(keyword.kwlist)
```

```text
['False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await', 'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except', 'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try', 'while', 'with', 'yield']
```

You will use most of these within the next ten files. Here is a program that checks a list of
candidate names for you:

```python
import keyword

candidates = ["2fast", "my name", "class", "first_name", "MAX_RETRIES", "user2"]

for candidate in candidates:
    is_keyword = keyword.iskeyword(candidate)
    is_valid = candidate.isidentifier() and not is_keyword
    print(f"{candidate!r:12} valid: {str(is_valid):5}  keyword: {is_keyword}")
```

```text
'2fast'      valid: False  keyword: False
'my name'    valid: False  keyword: False
'class'      valid: False  keyword: True
'first_name' valid: True   keyword: False
'MAX_RETRIES' valid: True  keyword: False
'user2'      valid: True   keyword: False
```

`class` is a keyword, so it is not a valid name. `2fast` and `my name` are not identifiers at all.

---

## 6. Reassignment, and `=` is not `==`

You can point a name at a new value at any time. The old value is simply forgotten.

```python
score = 10
print(score)

score = 20
print(score)

score = score + 5
print(score)
```

```text
10
20
25
```

Notice that `score = score + 5` is not a contradiction. Python evaluates the **right-hand side
first** (20 + 5 = 25), then assigns the answer to the name on the left.

### `=` versus `==`

This is the single most common confusion for people coming from other languages:

| | Meaning | Example |
|---|---|---|
| `=` | **Assignment** — put the value on the right into the name on the left | `total = 5` |
| `==` | **Comparison** — are these two values equal? Gives `True` or `False` | `total == 5` |

```python
a = 5
b = 5

print(a == b)   # comparison -> True
print(a, b)     # both are 5
```

```text
True
5 5
```

Writing `print(a = b)` is a **SyntaxError**, not a comparison — Python will not let you confuse the
two.

---

## 7. Multiple assignment and unpacking

You can assign to several names on one line. The right-hand side is a comma-separated list of
values; the left-hand side is a matching list of names.

```python
a, b = 1, 2
print(a)
print(b)

x = y = 10
print(x)
print(y)
```

```text
1
2
10
10
```

The second form (`x = y = 10`) assigns the same value to both names.

### The swap idiom

Because the right-hand side is evaluated before the assignment happens, you can swap two variables
in one line — no temporary variable needed:

```python
first, second = "left", "right"
print(first, second)

first, second = second, first
print(first, second)
```

```text
left right
right left
```

This **unpacking** style is not limited to two. It is how you pull a list or a tuple apart into
named pieces, and you will use it constantly:

```python
lat, lon = 51.5074, -0.1278
print(f"Latitude {lat}, longitude {lon}")
```

```text
Latitude 51.5074, longitude -0.1278
```

---

## 8. Augmented assignment

An **augmented assignment** does an operation and assigns the result back to the same variable in
one step. It is shorter and less error-prone than writing it out longhand.

```python
count = 0
count += 1
count += 1
print(count)

balance = 100
balance -= 25
print(balance)

score = 10
score *= 3
print(score)

average = 100
average /= 4
print(average)

boxes = 13
boxes //= 4
print(boxes)

remainder = 13
remainder %= 4
print(remainder)

power = 2
power **= 10
print(power)
```

```text
2
75
30
25.0
3
1
1024
```

| Operator | Meaning | Longhand equivalent |
|---|---|---|
| `+=` | add | `x = x + 1` |
| `-=` | subtract | `x = x - 1` |
| `*=` | multiply | `x = x * 2` |
| `/=` | true division | `x = x / 2` |
| `//=` | floor division | `x = x // 2` |
| `%=` | remainder | `x = x % 2` |
| `**=` | power | `x = x ** 2` |

Note that `average /= 4` produced `25.0`, not `25`. `/=` always produces a float, because `/`
always produces a float.

---

## 9. Arithmetic operators

| Operator | Name | Example | Result | When to use it |
|---|---|---|---|---|
| `+` | addition | `2 + 3` | `5` | Adding numbers; joining strings with `+` |
| `-` | subtraction | `7 - 3` | `4` | Taking away; negative numbers |
| `*` | multiplication | `4 * 3` | `12` | Scaling; repeating a string `"ab" * 3` |
| `/` | true division | `7 / 2` | `3.5` | Whenever you want the exact answer, decimals fine |
| `//` | floor division | `7 // 2` | `3` | When you need whole numbers: groups, pages, boxes |
| `%` | modulo | `7 % 2` | `1` | Every other item, wrapping around, "is it divisible?" |
| `**` | exponentiation | `2 ** 10` | `1024` | Powers; square roots via `** 0.5` |

```python
print(7 / 2)     # 3.5   -> a float, always
print(7 // 2)    # 3     -> floor: rounds down
print(7 % 2)     # 1     -> the remainder
print(10 / 5)    # 2.0   -> still a float, even when it divides evenly
print(2 ** 10)   # 1024
print(-7 // 2)   # -4    -> floor rounds towards negative infinity
print(-7 % 2)    # 1     -> the remainder takes the sign of the divisor
```

```text
3.5
3
1
2.0
1024
-4
1
```

### `//` and `%` in practice

**Floor division `//`** — "how many whole groups fit?"

```python
students = 87
per_classroom = 30

print(students // per_classroom)   # 2 complete classrooms
print(students % per_classroom)    # 27 students left over
```

```text
2
27
```

**Modulo `%`** — "take every other one" and "wrap around".

```python
colours = ["red", "green", "blue"]

for index in range(7):
    print(index, colours[index % len(colours)])
```

```text
0 red
1 green
2 blue
3 red
4 green
5 blue
6 red
```

`index % 3` cycles through `0, 1, 2, 0, 1, 2, 0` — that is how you wrap around a list, deal cards,
or pick a rotating role.

---

## 10. Strings

A **string** is a sequence of characters — text. In Python it is written between quotes.

### Single and double quotes are identical

```python
single = 'Hello'
double = "Hello"

print(single == double)   # True
print(single)
print(double)
```

```text
True
Hello
Hello
```

They are the same type and behave the same way. The only difference is convenience: use double
quotes when your text contains a single quote, and single quotes when it contains a double quote.

```python
print("It's ready")
print('She said "hello"')
```

```text
It's ready
She said "hello"
```

Python's official style guide (PEP 8) prefers **double quotes** for new code. Either is fine; just
be consistent within a file.

### Triple-quoted strings

Three quotes in a row let a string span multiple lines.

```python
poem = """Roses are red,
violets are blue,
this string spans three lines."""

print(poem)
```

```text
Roses are red,
violets are blue,
this string spans three lines.
```

Triple quotes are also how **docstrings** are written — same idea, used as documentation.

### Escaping

A **backslash** `\` inside a string means "the next character is special".

```python
print("She said: \"Hello!\"")   # \" -> a literal double quote
print("Line one\nLine two")     # \n -> a newline
print("Path: C:\\Users\\ada")   # \\ -> a literal backslash
print("Tab:\tseparated")        # \t -> a tab character
```

```text
She said: "Hello!"
Line one
Line two
Path: C:\Users\ada
Tab:	separated
```

The common escapes are `\n` (newline), `\t` (tab), `\\` (backslash), `\"` (quote), `\'` (quote).
If you want a backslash to be a backslash — common with Windows paths and regular expressions —
you either escape it as `\\` or prefix the string with `r`:

```python
print(r"C:\Users\ada\Documents")
```

```text
C:\Users\ada\Documents
```

### Strings are immutable

**Immutable** means "cannot be changed after it is created". A string is a fixed piece of text.
There is no way to edit a character in place; every "change" creates a brand-new string.

```python
greeting = "Hello"
greeting = greeting + ", world"    # builds a NEW string and re-points the name

print(greeting)
print(greeting.upper())

text = "Hello"
print(text.upper())   # returns a new string; text is unchanged
print(text)
```

```text
Hello, world
HELLO, WORLD
HELLO
Hello
```

Trying to edit a character directly fails:

```text
>>> text = "Hello"
>>> text[0] = "J"
TypeError: 'str' object does not support item assignment
```

This is not a Python quirk to work around — it is a safety feature. Because strings cannot change,
you can pass them around, use them as dictionary keys, and compare them without worrying that
somebody will modify them underneath you.

---

## 11. f-strings

An **f-string** — a *formatted string literal* — is the modern and by far the most important way
to build text in Python. Put an `f` in front of the quotes and you can drop variables straight
inside `{}` braces.

This is the single tool you will use most in this course.

### Basics

```python
name = "Ada"
age = 36

print(f"{name} is {age} years old.")
```

```text
Ada is 36 years old.
```

### Any expression goes inside the braces

You are not limited to variable names. The braces contain a normal Python expression, and its
*value* is inserted.

```python
name = "Ada"
age = 36
price = 19.99

print(f"{name} will be {age + 1} next year.")
print(f"The total is {price * 3:.2f}.")
print(f"Uppercased: {name.upper()}")
print(f"Even? {age % 2 == 0}")
```

```text
Ada will be 37 next year.
The total is 59.97.
Uppercased: ADA
Even? True
```

### Format specs

After the expression you can add a **format spec** — a colon and a mini-language that controls
alignment, padding, rounding and separators.

```python
price = 1234.5678
name = "Ada"
ratio = 0.856
count = 42

print(f"${price:,.2f}")     # thousands separator + 2 decimals
print(f"|{name:<10}|")      # left-aligned in a 10-wide field
print(f"|{name:>10}|")      # right-aligned
print(f"|{name:^10}|")      # centred
print(f"{ratio:.1%}")       # percentage
print(f"{count:5d}")        # integer, right-aligned in 5 columns
print(f"{price:>12,.2f}")  # right-aligned AND grouped
```

```text
$1,234.57
|Ada       |
|       Ada|
|   Ada    |
85.6%
   42
    1,234.57
```

### The self-documenting `=` form

Adding `=` inside the braces prints the expression *and* its value. This is genuinely useful when
you are debugging a long f-string.

```python
count = 42
ratio = 0.5

print(f"{count=}")
print(f"{ratio=}")
print(f"{count * 2=}")
```

```text
count=42
ratio=0.5
count * 2=84
```

### Formatting cheat sheet

| Spec | Does | Example | Result |
|---|---|---|---|
| `:.2f` | 2 decimal places | `f"{3.14159:.2f}"` | `3.14` |
| `:,.2f` | Thousands separator + 2 dp | `f"{1234.5:,.2f}"` | `1,234.50` |
| `:>10` | Right-align in 10 columns | `f"{'hi':>10}"` | `        hi` |
| `:<10` | Left-align in 10 columns | `f"{'hi':<10}"` | `hi        ` |
| `:^10` | Centre in 10 columns | `f"{'hi':^10}"` | `    hi    ` |
| `:10` | Left-align, width 10 | `f"{'hi':10}"` | `hi        ` |
| `:d` | Integer, no decimals | `f"{42:d}"` | `42` |
| `:5d` | Integer, width 5 | `f"{42:5d}"` | `   42` |
| `:%` | Percentage | `f"{0.856:.1%}"` | `85.6%` |
| `:b` | Binary | `f"{5:b}"` | `101` |
| `:x` | Hexadecimal | `f"{255:x}"` | `ff` |
| `!r` | Show the `repr()` | `f"{'a':!r}"` | `'a'` |
| `=` | Print name and value | `f"{x=}"` | `x=42` |
| `:>8.2f` | Width *and* precision | `f"{3.14159:>8.2f}"` | `    3.14` |

**The rule of thumb:** for plain text use `{name}`. For numbers a human reads, use `{:,.2f}` or
`{:.1%}`. For fixed-width columns, use `:<10`, `:>10` or `:^10`.

---

## 12. `print()` essentials

`print()` takes any number of values and writes them to the screen, separated by a single space
and followed by a newline.

```python
print("a", "b", "c")
```

```text
a b c
```

Two keyword arguments change that behaviour:

| Argument | Default | Does |
|---|---|---|
| `sep=` | `" "` (one space) | The string placed **between** values |
| `end=` | `"\n"` (newline) | The string placed **after** the last value |

```python
print("2024", "01", "15", sep="-")
print("Loading", end="...")
print(" done")
print("a", "b", "c", sep=" | ")
print()
print("end of report")
```

```text
2024-01-15
Loading... done
a | b | c

end of report
```

`print()` with no arguments prints an empty line — that is the blank line above.

---

## 13. `input()` — and the classic beginner bug

`input()` prints a prompt, waits for the user to type something, and returns what they typed.

```python
name = input("What is your name? ")
print(f"Hello, {name}!")
```

```text
What is your name? Ada
Hello, Ada!
```

### The trap

**`input()` always returns a string.** Always. Even if the user types `42`. Even if they type
`3.14`. This is the single most common beginner bug. Watch what happens:

```python
age = input("How old are you? ")     # the user types 31
print("Type of the value you typed:", type(age))
```

```text
How old are you? 31
Type of the value you typed: <class 'str'>
```

The user typed a number, and Python handed you a **string**. So the obvious next line explodes:

```text
>>> age = input("How old are you? ")
How old are you? 31
>>> next_year = age + 1
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: can only concatenate str (not "int") to str
```

The fix is to **convert** the string to a number with `int()` (or `float()`):

```python
age = int(input("How old are you? "))
next_year = age + 1
print(f"Next year you will be {next_year}.")
```

```text
How old are you? 31
Next year you will be 32.
```

### Making it robust

`int()` will crash on anything that is not a valid whole number, including a stray space. Two
defensive habits:

```python
raw = input("How old are you? ").strip()      # remove surrounding whitespace
age = int(raw) if raw.isdigit() else 0        # fall back to 0 instead of crashing

print(f"Age recorded as {age}.")
```

```text
How old are you? 31
Age recorded as 31.
```

`.strip()` removes leading and trailing whitespace. `.isdigit()` returns `True` if the string is
made only of digits. Full details on strings and their methods are in
[03 Data types and operators](03-data-types-and-operators.md).

---

## 14. Semicolons, line continuation and multi-line expressions

### The semicolon

Python allows `x = 1; y = 2` on one line. **Do not do it.** It is legal, it works, and it will
make your code unreadable and your debugging harder.

```python
x = 1; y = 2; print(x + y)     # legal, and bad style
```

```text
3
```

### Logical line continuation

A single **logical line** — one statement — can span several **physical lines** if you wrap it in
parentheses. This is the clean way to write a long expression.

```python
total = (
    19.99
    + 4.50
    + 2.99
)
print(total)

report = (
    "Name: Ada\n"
    "Role: Engineer\n"
    "Status: Active"
)
print(report)
```

```text
27.479999999999997
Name: Ada
Role: Engineer
Status: Active
```

That first number looks wrong, but it is not — it is exactly what Python prints. A `float` cannot
represent `27.48` precisely in binary, so the addition lands a hair away from it. This is why you
round for display with a format spec (`:.2f` gives `27.48`) and why money is stored as whole
pence rather than as floats.

You can also use a backslash at the end of a line, but it is easy to break (a trailing space after
the backslash silently breaks it) and it does not work inside brackets. **Prefer parentheses.**

```python
total = 1 + \
        2 + \
        3
print(total)
```

```text
6
```

### Reading several lines of input

`input()` reads exactly one line. To collect multiple lines, loop until the user sends an empty
one.

```python
print("Type your notes. Send an empty line to finish.")

notes = []
while True:
    line = input()
    if line == "":
        break
    notes.append(line)

print(f"You entered {len(notes)} lines.")
```

```text
Type your notes. Send an empty line to finish.
You entered 2 lines.
```

---

## 🧪 Try it yourself

### Exercise 1 — Fix the broken calculator

A colleague sends you this script and says "it does not add". Find the bug, fix it, and explain
what `type()` told you.

```python
first = input("First number: ")
second = input("Second number: ")

result = first + second
print("The sum is:", result)
```

Type `2` and then `3` and it prints:

```text
The sum is: 23
```

That is the bug: `23`, not `5`. Now fix it, and explain what `type()` told you.

<details>
<summary>Hint</summary>

Print `type(first)` before doing anything else.

</details>

<details>
<summary>Solution</summary>

```python
first = input("First number: ")
second = input("Second number: ")

print("Types:", type(first), type(second))

result = int(first) + int(second)
print("The sum is:", result)
```

```text
Types: <class 'str'> <class 'str'>
The sum is: 5
```

Both values are **strings**, so `first + second` performs *text joining*: `"2" + "3"` produces the
string `"23"`, not the number `5`. `int()` converts each one to an integer before adding, which
gives `5`. The two results look nothing alike, which is exactly why this bug is so confusing the
first time you hit it.

</details>

### Exercise 2 — A receipt formatter

Write a script that defines these values:

```python
item_name = "Coffee Beans"
quantity = 3
unit_price = 12.50

print(f"Working with {quantity} x {item_name}")
```

Then print a receipt where the item name is left-aligned in a 20-character field and the total is
right-aligned in a 10-character field with two decimals. Use one f-string per line.

<details>
<summary>Hint</summary>

Two format specs on one f-string: `f"{item_name:<20}"` and `f"{total:>10.2f}"`. You can put
several fields in one f-string.

</details>

<details>
<summary>Solution</summary>

```python
item_name = "Coffee Beans"
quantity = 3
unit_price = 12.50

total = quantity * unit_price

print(f"{item_name:<20}{quantity:>4} x {unit_price:>8.2f}")
print(f"{'TOTAL':<20}{total:>18.2f}")
print(f"{'Paid:':<20}{total:>18.2f}")
```

```text
Coffee Beans           3 x    12.50
TOTAL                            37.50
Paid:                            37.50
```

The `:<20` pads the name with spaces on the right so the next column starts in the same place
every time. That is how you build a table that lines up.

</details>

### Exercise 3 — Swap without a temporary

Two variables hold two values. Swap them using one line, then verify the swap worked.

```python
first = "apples"
second = "oranges"

# Your one-line swap goes here

print(first)
print(second)
```

<details>
<summary>Hint</summary>

Python evaluates the whole right-hand side before assigning anything, so the two names can be
swapped in one statement.

</details>

<details>
<summary>Solution</summary>

```python
first = "apples"
second = "oranges"

first, second = second, first

print(first)
print(second)
```

```text
oranges
apples
```

</details>

### Exercise 4 — Seconds into minutes and seconds

Write a script that takes a number of seconds from the user and prints how many whole minutes and
leftover seconds that is. Use `//` and `%`.

<details>
<summary>Hint</summary>

`total_seconds // 60` gives the whole minutes and `total_seconds % 60` gives the leftovers.

</details>

<details>
<summary>Solution</summary>

```python
total_seconds = int(input("How many seconds? "))

minutes = total_seconds // 60
seconds = total_seconds % 60

print(f"{total_seconds} seconds is {minutes} minutes and {seconds} seconds.")
```

```text
How many seconds? 3725
3725 seconds is 62 minutes and 5 seconds.
```

</details>

### Exercise 5 — Everything is a string

Predict the output of this script **before** you run it:

```python
value = "10"
value = value + "5"
print(value)
print(type(value))
```

Then change the first line to `value = 10` and run it again. Explain the difference in one
sentence.

<details>
<summary>Hint</summary>

What does `+` do when both sides are strings? What does it do when both sides are numbers?

</details>

<details>
<summary>Solution</summary>

First version:

```text
105
<class 'str'>
```

Second version:

```text
15
<class 'int'>
```

`+` means *concatenation* for strings and *addition* for numbers. In the first version both
operands are strings, so `"10" + "5"` joins them into `"105"` — the digits are stuck together
rather than added. The second version adds two integers to get `15`.

</details>

### Exercise 6 — A comment that earns its place

Write a script that converts a temperature in Celsius to Fahrenheit. Add **one** comment that
explains something the code cannot say on its own — not "add 32" or "multiply by 9". Then add a
docstring to the function explaining what it returns.

<details>
<summary>Hint</summary>

A good comment explains a *why*, a *constraint*, or a *gotcha*. Examples: why the formula is
`(celsius * 9/5) + 32` and not `celsius * 1.8 + 32` (floating-point drift in long calculations),
or that the function assumes Celsius, not Kelvin.

</details>

<details>
<summary>Solution</summary>

```python
def celsius_to_fahrenheit(celsius):
    """Return the Fahrenheit temperature for a temperature given in Celsius."""
    # Multiplying by 9/5 first avoids a rounding error that celsius * 1.8 would introduce.
    return (celsius * 9 / 5) + 32


print(celsius_to_fahrenheit(100))
print(celsius_to_fahrenheit(0))
print(celsius_to_fahrenheit(-40))
```

```text
212.0
32.0
-40.0
```

The `-40` check is a nice touch: `-40` Celsius is exactly `-40` Fahrenheit, so if your formula
gives anything else, it is wrong.

</details>

---

## ✅ Checkpoint

1. How does Python know where a block ends, given that it has no curly braces, and what is the
   difference between a comment and a docstring?
2. In `price = 19.99`, what is `price` and what is `19.99`?
3. What does it mean that Python is dynamically typed, and what habit prevents it hurting you?
4. Write the name of a variable holding a user's email address using the PEP 8 convention, and
   explain why you cannot name a variable `class`.
5. What is the difference between `=` and `==`?
6. What do `7 / 2` and `7 // 2` return, which would you use to find how many whole boxes fit on a
   shelf, and what does `%` give you?
7. In `f"{total:.2f}"`, what is the `:2f` part called and what does it do?
8. What does `input()` always return and how do you fix it, and how do `sep=` and `end=` differ in
   `print()`?

<details>
<summary>1. Blocks, comments and docstrings</summary>

A block is delimited by **indentation** — everything indented under a line that ends in a `:` is
part of that block. Python uses four spaces per level and never mixes tabs and spaces.

A **comment** (`# ...`) is ignored entirely by Python — it is a note for humans. A **docstring** is
a string literal at the top of a function, class or module; it is stored in the object at runtime,
so `help()` and documentation tools can display it.

</details>

<details>
<summary>2. price and 19.99</summary>

`price` is the **name** (a label). `19.99` is the **value** (the data). `price = 19.99` puts the
value in the box and writes `price` on the label.

</details>

<details>
<summary>3. Dynamic typing</summary>

The type of a variable comes from the value assigned to it, not from a declaration, so the same
name can hold an `int`, then a `str`, then a `list`. The protective habit: keep one name meaning
one kind of thing, and use a new name rather than re-pointing an existing one at a different type.

</details>

<details>
<summary>4. Naming rules</summary>

`user_email` or `email_address` — lowercase words joined with underscores (`snake_case`).

`class` is one of Python's 35 **reserved keywords** — words the language itself uses, so you
cannot use them as names. `keyword.kwlist` prints them all; `keyword.iskeyword(name)` checks one.

</details>

<details>
<summary>5. = versus ==</summary>

`=` is **assignment**: it puts the right-hand value into the name on the left. `==` is
**comparison**: it asks whether two values are equal and answers `True` or `False`. `print(a = b)`
is a SyntaxError.

</details>

<details>
<summary>6. Division and modulo</summary>

`7 / 2` is `3.5` (true division, always a float). `7 // 2` is `3` (floor division, rounds down).
For "how many whole boxes fit on the shelf" you want `//`, because a half-filled box is not a box.

`%` is the **modulo** operator: it returns the remainder after division (`7 % 2` is `1`). Use it to
take every other item, to wrap around a list, to alternate styles, or to test whether a number
divides evenly by another (`n % 2 == 0` means "n is even").

</details>

<details>
<summary>7. The :2f format spec</summary>

It is a **format spec** (part of the f-string mini-language). `:2f` formats the number as a
floating-point value with 2 digits after the decimal point — `3.14159` becomes `3.14`.

</details>

<details>
<summary>8. input() and print()</summary>

`input()` always returns a **string**, even when the user types digits. Wrap it:
`int(input(...))` for whole numbers, `float(input(...))` for decimals. `.strip()` first if the user
might type spaces.

In `print()`, `sep=` sets the string placed **between** values (`"a-b"`). `end=` sets the string
placed **after** the last value (`"ab"` with no newline). `end=""` is how you print several things
on one line.

</details>

---

## 🐛 Common mistakes

| Mistake | What you see | Fix |
|---|---|---|
| Forgetting the colon after `if`/`for`/`def` | `SyntaxError: invalid syntax` | Every block-introducing line ends with `:` |
| Using 2 spaces or mixing tabs and spaces | `IndentationError` or `TabError: inconsistent use of tabs and spaces` | Four spaces per level, and let your editor insert them (`Tab` / `Shift+Tab`) |
| Using `=` when you meant `==` | `SyntaxError: invalid syntax` | `=` assigns, `==` compares |
| Believing `input()` gives you a number | `TypeError: can only concatenate str (not "int") to str` | Wrap it: `int(input(...))` |
| Expecting `7 / 2` to be `3` | You get `3.5` | Use `7 // 2` for floor division |
| Using `name` for a variable that holds a list, then a string | Confusing bugs far from the cause | One name, one meaning — use a new name instead |
| Naming a variable `list`, `sum`, `print`, `input` | Your code silently behaves oddly, or crashes | `list`, `sum`, `print`, `input` are **built-ins**; never shadow them |
| Forgetting that strings are immutable and trying `text[0] = "J"` | `TypeError: 'str' object does not support item assignment` | Build a new string: `text = "J" + text[1:]` |

---

## 🔗 Resources

- [The official Python tutorial](https://docs.python.org/3/tutorial/) — chapters 3 and 5 of the
  tutorial cover exactly this material, written by the core team
- [PEP 8 — Style Guide for Python Code](https://peps.python.org/pep-0008/) — the official style
  guide; read the naming conventions and indentation sections, they cover most of this chapter
- [PEP 20 — The Zen of Python](https://peps.python.org/pep-0020/) — nineteen aphorisms about how
  Python code should be written; short enough to read in three minutes
- [An Informal Introduction to Python](https://docs.python.org/3/tutorial/introduction.html) — the
  Pythonic way to use numbers and strings, straight from the docs
- [Lexical analysis: the Python language grammar](https://docs.python.org/3/reference/lexical_analysis.html)
  — the exact, formal rules for names, keywords, strings and operators
- [Built-in functions reference](https://docs.python.org/3/library/functions.html) — the
  authoritative list of `print`, `input`, `type`, `len` and everything else built in
- [String methods](https://docs.python.org/3/library/stdtypes.html#string-methods) — every method
  available on a string, including `strip`, `isdigit`, `split` and `join`
- [Formatted string literals](https://docs.python.org/3/reference/expressions.html#formatted-string-literals)
  — the official specification of f-strings and the format spec mini-language
- [The `keyword` module](https://docs.python.org/3/library/keyword.html) — the full list of
  reserved words, plus `keyword.iskeyword` and `keyword.kwlist`
- [The `tokenize` module](https://docs.python.org/3/library/tokenize.html) — how Python splits
  source code into tokens; useful when you want to understand the parsing step from
  [01 Getting started](01-getting-started.md)

---

## ➡️ Next

- [03 Data types and operators](03-data-types-and-operators.md) — the full set of types
  (`int`, `float`, `bool`, `None`), comparisons, logic, truthiness and type conversion

**← Previous:** [01 Getting started](01-getting-started.md)
