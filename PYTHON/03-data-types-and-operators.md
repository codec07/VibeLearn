# Data types and operators

Every value in Python has a **type** — the shape of the data — and every **operator** is
a rule for combining values of certain types. You never have to write the type down, but
you do have to know what it is, because Python will happily add a `str` to an `int` and
give you a `TypeError` you did not expect. This file walks through the types you will use
every single day, the operators that combine them, and the handful of Python-specific
behaviours (like `None` and floating-point precision) that trip up even experienced
programmers.

> **⏱️ Time:** ~40 minutes
> **📚 Prereqs:** [02 — Syntax and variables](02-syntax-and-variables.md)
> **🎯 By the end you can:** pick the right built-in type for a value, convert between types
> safely, and predict exactly what any expression in Python will evaluate to.

---

## Why this matters for AI engineering

Types are the vocabulary of a program. In an AI system, a **token id** is an `int`, an
**embedding** is a `float`, a **prompt** is a `str`, and a **missing tool result** is `None`.
When you mix them up, you get silent numerical bugs: an `int` where a `float` was expected
turns a probability into a `0`, and `None` quietly becomes `False` in a guard clause and the
agent takes the wrong branch. Understanding exactly how Python stores and compares values is
the difference between "the model hallucinated" and "I passed `None` where a number belonged".

---

## The five types you will actually use

Python has more built-in types than you will ever memorise, but you can ignore most of them
for months. These five carry almost all beginner code:

| Type | What it holds | How to make one | How to check it |
|---|---|---|---|
| `int` | a whole number | `42` | `type(42) is int` |
| `float` | a number with a decimal part | `3.14` | `type(3.14) is float` |
| `str` | text (a sequence of characters) | `"hello"` | `type("hello") is str` |
| `bool` | exactly one of `True` or `False` | `True` | `type(True) is bool` |
| `None` | "there is no value here" | `None` | `x is None` |

A **value** is a piece of data that lives in memory. A **type** is the category that value
belongs to. `42` and `3.14` are different values *and* different types, and Python will refuse
to mix them in some operations.

```python
print(type(42))        # <class 'int'>
print(type(3.14))      # <class 'float'>
print(type("hello"))   # <class 'str'>
print(type(True))      # <class 'bool'>
print(type(None))      # <class 'NoneType'>

# The other two useful built-ins for a second:
print(type([1, 2, 3]))  # <class 'list'>
print(type({"a": 1}))   # <class 'dict'>
```

`list`, `dict`, `tuple` and `set` are the container types. They deserve their own file, which
is exactly what [06 — Data structures](06-data-structures.md) is for. For now, treat them as
"things you will meet later".

### Real examples of each type

```python
# int — counts, token ids, token budgets
max_new_tokens = 512

# float — probabilities, learning rates, prices
temperature = 0.7

# str — prompts, model names, file paths
model_name = "gpt-4o-mini"

# bool — flags that turn features on and off
stream_response = True

# None — "no tool result yet", "no user id", "nothing found"
tool_result = None

for value in (max_new_tokens, temperature, model_name, stream_response, tool_result):
    print(f"{value!r:>18}  ->  {type(value).__name__}")
```

### A tiny AI example that mixes them

Look at a stripped-down version of one step of a language model's forward pass. This is the
real shape of the code you will see in a transformer implementation:

```python
# A tiny stand-in for one step of a language model's forward pass.
token_ids = [101, 2054, 2003, 1037]      # int   — ids from the tokenizer vocabulary
embeddings = [0.03, -0.11, 0.07, 0.02]   # float — one weight per token
scale = 1.0 / 100.0                      # float — a normalisation factor

logit = 0.0
for token_id, embedding in zip(token_ids, embeddings):
    logit += embedding * scale * (token_id % 17)

print("token id type :", type(token_ids[0]).__name__)
print("embedding type:", type(embedding).__name__)
print("logit         :", round(logit, 6))
print("logit type    :", type(logit).__name__)
```

```text
token id type : int
embedding type: float
logit         : -0.0008
logit type    : float
```

Read that output carefully: `int * float` produces a `float`. Python promotes the "weaker"
type rather than refusing. The number `logit` starts as a float and stays a float.

---

## `None` — the value that means "no value"

`None` is Python's way of saying *there is no value here*. It is not zero, it is not an empty
string, and it is most definitely **not** `False`.

```python
print(None == False)   # False
print(None == 0)       # False
print(None is None)    # True
print(bool(None))      # False
```

Why does this matter? Because "no value yet" and "the value is zero" mean completely different
things in an AI pipeline. A retrieval step that found *zero* documents is a result; a
retrieval step that found *no* documents is a failure. `None` tells you which one happened.

```python
# A realistic "nothing found" signal.
search_results = None      # the retriever has not run yet

if search_results is None:
    print("Retrieval has not run yet.")
else:
    print(f"Found {len(search_results)} documents.")
```

```text
Retrieval has not run yet.
```

A `None` value usually appears when a function returns early without a value, or when a
dictionary lookup misses. You will see both in [05 — Functions](05-functions.md) and
[06 — Data structures](06-data-structures.md).

---

## Converting between types

Conversion is done by calling a type like a function. The *constructor* for a type turns one
value into that type.

```python
print(int("42"))       # 42      — a numeric string becomes a number
print(int(42.9))       # 42      — a float is truncated toward zero
print(int(-42.9))      # -42     — truncation, not rounding
print(float("3.14"))   # 3.14
print(float(3))        # 3.0
print(str(3))          # '3'
print(str(3.0))        # '3.0'
print(bool(0))         # False
```

But conversion can fail, and when it fails it raises a `ValueError` — a built-in error meaning
"the value is the wrong shape for this type".

```python
try:
    number = int("forty two")
except ValueError as error:
    print("Conversion failed:", error)
```

```text
Conversion failed: invalid literal for int() with base 10: 'forty two'
```

Two conversions surprise beginners constantly:

```python
print(bool("False"))   # True!  A non-empty string is truthy
print(bool("0"))       # True!  Same reason
print(bool([0]))       # True!  The list is not empty
```

`bool("False")` is `True` because the string has four characters in it. Python never parses
the *contents* of a string to decide truthiness. This is the single most common source of
"why is my flag always on?" bugs, and it is why you should never store flags as strings.

---

## Arithmetic operators

| Operator | Name | Example | Result |
|---|---|---|---|
| `+` | add | `3 + 4` | `7` |
| `-` | subtract | `3 - 4` | `-1` |
| `*` | multiply | `3 * 4` | `12` |
| `/` | divide (always float) | `7 / 2` | `3.5` |
| `//` | floor divide | `7 // 2` | `3` |
| `%` | modulo (remainder) | `7 % 2` | `1` |
| `**` | power | `2 ** 10` | `1024` |

The `//` versus `/` difference is the one that catches people. `/` always produces a `float`,
even when the division is exact. `//` floors the result and returns an `int`.

```python
print(7 / 2)     # 3.5   <- true division, always a float
print(7 // 2)    # 3     <- floor division, an int
print(7 % 2)     # 1     <- the remainder
print(6 / 3)     # 2.0   <- still a float, even when exact
print(6 // 3)    # 2     <- an int
```

You will use `//` constantly in AI code for two things: chunking text into fixed-size pieces,
and computing how many batches a dataset needs.

```python
chars_per_chunk = 1000
text_length = 3450

chunks = text_length // chars_per_chunk
leftover = text_length % chars_per_chunk

print(f"{chunks} full chunks, {leftover} characters left over")
```

```text
3 full chunks, 450 characters left over
```

### Modulo with negative numbers

Python's modulo always returns a result with the **same sign as the divisor**, which is not
what most other languages do. This surprises people, so it is worth memorising:

```python
print(7 % 2)     # 1   (normal case)
print(-7 % 2)    # 1   (Python) — sign follows the divisor, which is positive
print(7 % -2)    # -1  (Python) — sign follows the divisor, which is negative

# Compare with floor division, which always rounds toward negative infinity:
print(-7 // 2)   # -4
print(-7 % 2)    # 1
```

The useful mental model: `a // b` is the number of whole times `b` fits into `a`, and `a % b` is
what is left over. The twist is that Python rounds *down* — toward negative infinity —
rather than toward zero, and that is exactly why the leftover always carries the sign of
the divisor. The identity `a == (a // b) * b + (a % b)` holds for every pair of integers,
including negative ones.

```python
print(divmod(-7, 2))   # (-4, 1) — the // and % results, together
```

`divmod()` is a built-in that gives you both answers in one call, and it is faster than
computing them separately.

---

## The float precision trap

This is the most famous surprise in all of programming, and it will appear in interview
questions and in real bug reports.

```python
print(0.1 + 0.2)
print(0.1 + 0.2 == 0.3)
print(0.1 + 0.2 != 0.3)
```

```text
0.30000000000000004
False
True
```

### Why this happens (no hand-waving)

Computers store floating-point numbers in **binary** — base 2 — but humans write them in
base 10. The number `0.1` means "one tenth", and one tenth is `0.000110011001100110011...`
in binary: it repeats forever, exactly like `1/3` repeats in decimal as `0.333333...`.

A repeating binary fraction cannot be stored exactly. A `float` in Python is a 64-bit
**IEEE 754** number, so Python stores the *closest value it can* to the true `0.1`.

You can see the exact stored value:

```python
from decimal import Decimal

print(Decimal(0.1))
print(Decimal(0.2))
print(Decimal(0.3))
```

```text
0.1000000000000000055511151231257827021181583404541015625
0.200000000000000011102230246251565404236316680908203125
0.299999999999999988897769753748434595763683319091796875
```

Both `0.1` and `0.2` are stored slightly *above* their true values, and `0.3` is stored
slightly *below* its true value. So when you add the two approximations you get a number that
is one tiny step away from the approximation of `0.3`.

The difference is smaller than one part in a quadrillion — the *printed* `0.30000000000000004`
and the *true* `0.3` differ by about `1.4 × 10⁻¹⁷`. But floating-point equality is exact:
the two numbers are genuinely different, so `==` correctly reports `False`.

Here is the same fact in a much more compact form — the hexadecimal "machine" form of each
number. Only the final digit differs:

```python
print((0.1).hex())        # 0x1.999999999999ap-4
print((0.2).hex())        # 0x1.999999999999ap-3
print((0.1 + 0.2).hex())  # 0x1.3333333333334p-2
print((0.3).hex())        # 0x1.3333333333333p-2
```

### What to do about it

Three practical rules, in order of how often you will need them.

### Rule 1: never compare floats with `==` for real-valued data

Use `math.isclose()` instead. It has a default relative tolerance of `1e-09`.

```python
import math

print(math.isclose(0.1 + 0.2, 0.3))        # True
print(math.isclose(0.1 + 0.2, 0.31))       # False
print(math.isclose(1000.0, 1000.1, rel_tol=0.001))  # True
```

### Rule 2: for money, use `Decimal`

`Decimal` stores base-10 numbers exactly, so the digits always add up.

```python
from decimal import Decimal

price = Decimal("0.30")
tax = Decimal("0.075")
print(price + tax)                     # 0.375
print(price + tax == Decimal("0.375"))  # True
```

Note the quotes: `Decimal("0.30")` converts the *string* `"0.30"` exactly, while
`Decimal(0.30)` converts the already-imperfect float and inherits its error.

### Rule 3: for exact rational arithmetic, use `Fraction`

`Fraction` stores a numerator and a denominator, so no rounding happens at all.

```python
from fractions import Fraction

third = Fraction(1, 3)
sixth = Fraction(1, 6)
print(third + sixth)   # 1/2  (exactly, with no rounding at all)
```

For most AI work, rule 1 is enough. Loss values, learning rates, and probabilities are all
approximations anyway, and every real framework on earth uses 32-bit floats internally.

---

## Python integers are arbitrarily large

In C, an `int` is usually 32 bits and overflows at 2,147,483,647. In JavaScript, numbers are
doubles, which start losing precision above 2⁵³. Python's `int` grows to fit whatever you
give it — it is an *arbitrary precision* integer.

```python
big = 2 ** 100
print(big)
print(big + 1)
print(len(str(big)), "digits")
```

```text
1267650600228229401496703205376
1267650600228229401496703205377
31 digits
```

This is a genuine advantage, and you will use it for things a C programmer cannot: cryptographic
keys, exact big-number arithmetic, and computing `factorial(1000)` without planning for it.

```python
import math

print(math.factorial(20))    # 2432902008176640000 — exact, no overflow
print(math.factorial(100) > 10**150)  # True
```

The cost is memory and speed: very large integers are slower to add and multiply than small
ones. For AI workloads you almost always want `float` anyway, because model weights are
decimals.

---

## Infinity and NaN

Python can represent two special float values that are not ordinary numbers.

```python
import math

print(float("inf"))     # inf
print(float("-inf"))    # -inf
print(math.inf)         # inf
print(math.nan)         # nan
```

**Infinity** is useful as a default "no limit" value — an unlimited retry budget, an
unbounded context window, a sentinel meaning "not set yet".

**NaN** means "Not a Number": the result of an operation that has no meaningful answer, such
as `0.0 / 0.0` or `math.sqrt(-1)`.

NaN has one notorious property: **it breaks every comparison**. It is not equal to anything,
not even itself.

```python
import math

nan = math.nan

print(nan == nan)     # False  <- not even itself!
print(nan != nan)     # True
print(nan > 1)        # False
print(nan < 1)        # False
print(nan >= 1)       # False
print(nan <= 1)       # False
```

This matters enormously in data pipelines. If a NaN creeps into a column of scores, a filter
like `if score > 0.5:` will quietly drop the row instead of flagging it. Always check for NaN
explicitly:

```python
import math

scores = [0.82, float("nan"), 0.41]

for score in scores:
    if math.isnan(score):
        print("skipped a missing score")
    elif score > 0.5:
        print("kept a good score:", score)
    else:
        print("kept a low score:", score)
```

```text
kept a good score: 0.82
skipped a missing score
kept a low score: 0.41
```

A second trap: because NaN never compares equal to anything — not even to itself — the
`in` operator cannot find it. `nan in my_list` can be `False` even when a NaN is sitting
right there in the list. Use `math.isnan()` to hunt for them instead.

---

## Comparing values

Six comparison operators: `==`, `!=`, `<`, `>`, `<=`, `>=`. They work on numbers and on
strings, and string comparison is *alphabetical* (lexicographic), not numeric.

```python
print(3 == 3)      # True
print(3 != 4)      # True
print(3 < 4)       # True
print(3 >= 4)      # False
print("apple" < "banana")   # True — alphabetical
print("Apple" < "banana")   # True — uppercase sorts before lowercase
print("10" < "9")           # True — it compares characters, not numbers!
```

That last one is a classic bug: comparing numeric strings as strings. Convert first.

### Chained comparisons

Python lets you chain comparisons directly, and it means exactly what it looks like.

```python
score = 7

print(0 <= score <= 10)   # True  — "is score between 0 and 10?"
print(0 <= score <= 5)    # False
```

This is *not* a special case bolted onto Python — it is how the language is defined. `a <= b <= c`
evaluates as `a <= b and b <= c`, and it evaluates `b` only once. Compare with writing it the
long way:

```python
score = 7

# The long way, and it is strictly worse:
print(0 <= score and score <= 10)
```

Chained comparisons are especially natural for the kind of range checks that appear all over
AI code: temperature bounds, learning-rate schedules, score buckets.

```python
learning_rate = 3e-5
print(1e-6 <= learning_rate <= 1e-4)   # True
```

---

## `==` versus `is`

These two look similar and are completely different.

- `==` asks: **do these two values have the same content?**
- `is` asks: **are these two names pointing at the same object in memory?**

```python
a = [1, 2, 3]
b = [1, 2, 3]

print(a == b)   # True  — same contents
print(a is b)   # False — two separate list objects

c = a
print(a is c)   # True  — c is just another name for the same object
```

### The small-integer caching gotcha

CPython keeps a cache of small integer objects, so identical small numbers can end up being
the *same object*. This makes `is` on numbers look like it "works" — until it does not.

```python
x = 256
y = 256
print(x is y)   # True  (CPython caches small ints, roughly -5 to 256)

p = int("1000")
q = int("1000")
print(p is q)   # False — built at runtime, so two different objects
print(p == q)   # True  — same value
```

The rule to remember: **`is` on numbers is an implementation detail, not a language guarantee.**
Different Python implementations, and different versions of the same one, are free to change
it. Never use `is` to compare numbers.

### The one place `is` is correct

`is` is the right operator for `None`, and for `None` you should always use `is`:

```python
value = None

print(value is None)   # True  <- correct
print(value == None)  # True  <- works, but is the wrong habit
```

`x == None` looks like it works because `None` compares equal only to itself. But the
convention across the whole Python ecosystem — the standard library, every framework, the
style guides — is `x is None`, because it is *unambiguous* and it cannot be fooled by a
custom class that defines its own `__eq__`.

```python
# The classic failure of `== None`
class AlwaysEqual:
    def __eq__(self, other):
        return True


thing = AlwaysEqual()
print(thing == None)   # True  <- the lie
print(thing is None)   # False <- the truth
```

Use `is None` and `is not None`. Always.

---

## Logical operators: `and`, `or`, `not`

Three operators that combine conditions:

| Operator | Meaning | True when |
|---|---|---|
| `and` | both sides must be true | both operands are truthy |
| `or` | at least one side must be true | either operand is truthy |
| `not` | flips a truth value | the operand is falsy |

The operands are not required to be booleans. `and` and `or` work on any values and return
one of their *operands*, not necessarily a `bool`. This is the part that confuses people.

```python
print(True and False)   # False
print(True or False)    # True
print(not True)         # False

# `and`/`or` return operands, not booleans
print(1 and 2)          # 2   <- the last truthy operand
print(0 or "fallback")  # 'fallback' <- the first truthy operand
print([] or {})         # {}  <- both are falsy, so the right-hand operand is returned
```

### Short-circuit evaluation

`and` and `or` do **not** evaluate both sides. They stop as soon as the answer is known.
This is called *short-circuit evaluation*, and it is a performance feature *and* a safety
feature.

```python
def expensive_check(name):
    print(f"  ...running {name}")
    return True


def cheap_check(name):
    print(f"  ...running {name}")
    return False


print("Testing `cheap and expensive`:")
result = cheap_check("cheap") and expensive_check("expensive")
print("result:", result)
```

```text
Testing `cheap and expensive`:
  ...running cheap
result: False
```

`expensive_check` never ran. The `and` already knew the answer was `False` after the left
side, so it stopped.

Here are the same two functions again, this time used the other way round:

```python
def expensive_check(name):
    print(f"  ...running {name}")
    return True


def cheap_check(name):
    print(f"  ...running {name}")
    return False


print("Testing `expensive or cheap`:")
result = expensive_check("expensive") or cheap_check("cheap")
print("result:", result)
```

```text
Testing `expensive or cheap`:
  ...running expensive
result: True
```

Same story with `or`: the left side was truthy, so the answer was already `True`.

This is exactly how you write safe code that would crash if it were eager:

```python
message = None

# Safe: `message` is None, so `and` short-circuits and never evaluates the right side.
if message and message.strip():
    print("message has content")
else:
    print("message is empty or missing")
```

Without short-circuiting, `None.strip()` would raise `AttributeError`.

---

## Truthiness

Python's conditions do not need to be `True` or `False`. Any value can be used in a
condition, and Python decides whether it is *truthy* or *falsy* by asking a simple question:
is this value empty, zero, or missing?

**Falsy values** (treated as `False`):

| Value | Type | Why it is falsy |
|---|---|---|
| `False` | `bool` | it is `False` |
| `None` | `NoneType` | it means "no value" |
| `0` | `int` | zero |
| `0.0` | `float` | zero |
| `""` | `str` | empty string |
| `[]` | `list` | empty |
| `{}` | `dict` | empty |
| `()` | `tuple` | empty |
| `set()` | `set` | empty |

**Everything else is truthy** — including `"0"`, `[0]`, `{"a": 1}` and `-1`.

The `bool()` function applies the same rule, which makes it a great teaching tool:

```python
values = [0, 0.0, "", [], {}, set(), None, False, 1, -1, "0", [0]]

for value in values:
    print(f"{value!r:>8}  ->  {bool(value)}")
```

```text
       0  ->  False
     0.0  ->  False
      ''  ->  False
      []  ->  False
      {}  ->  False
   set()  ->  False
    None  ->  False
   False  ->  False
       1  ->  True
      -1  ->  True
     '0'  ->  True
     [0]  ->  True
```

The general rule for your own objects: an object is falsy if it defines `__bool__` or
`__len__` and that says "empty". A list with one item is truthy even if that item is `0`.

Truthiness is used constantly in real code:

```python
messages = ["hello", "goodbye"]

if messages:
    print(f"sending {len(messages)} messages")

# The same idea, more explicitly
if len(messages) > 0:
    print(f"sending {len(messages)} messages")
```

You will use this style constantly in [04 — Control flow](04-control-flow.md).

---

## `in` and `not in`

The `in` operator tests **membership**. It works on strings, lists, tuples, dicts and sets.

```python
print("ell" in "hello")        # True  — is this substring present?
print("xyz" in "hello")        # False
print(3 in [1, 2, 3])          # True  — is this item in the list?
print("a" in {"a": 1, "b": 2})  # True  — is this key in the dict?
print(2 in (1, 2, 3))          # True  — is this item in the tuple?

print("z" not in "hello")      # True
print(9 not in [1, 2, 3])      # True
```

For a **dict**, `in` checks the *keys*, not the values. That trips people up constantly:

```python
config = {"model": "gpt-4o-mini", "temperature": 0.7}

print("model" in config)        # True  — it is a key
print("gpt-4o-mini" in config)  # False — it is a value, not a key
```

Checking membership in a list is slow for big lists, because Python looks at each item in
turn. A **set** does the same job instantly, which is why experienced Python programmers
reach for `set` whenever they are about to write `x in some_long_list` inside a loop.

```python
allowed = {"read", "write", "list"}
print("read" in allowed)   # True — and it stays fast with a million items
```

---

## Operator precedence

When an expression contains several operators, Python evaluates them in a fixed order.
Getting this wrong is a classic source of silent bugs, so here is the full table, tightest
binding first.

| Level | Operators | Example | Evaluated as |
|---|---|---|---|
| 1 | `**` | `2 ** 3 ** 2` | `2 ** (3 ** 2)` |
| 2 | `+x`, `-x`, `~x` (unary) | `-3 + 2` | `(-3) + 2` |
| 3 | `*`, `/`, `//`, `%` | `2 + 3 * 4` | `2 + (3 * 4)` |
| 4 | `+`, `-` | `10 - 4 - 3` | `(10 - 4) - 3` |
| 5 | `<<`, `>>` | `8 >> 1` | bit shift |
| 6 | `&` | `5 & 3` | bitwise and |
| 7 | `^` | `5 ^ 3` | bitwise xor |
| 8 | `\|` | `5 \| 3` | bitwise or |
| 9 | `in`, `not in`, `is`, `is not`, `<`, `<=`, `>`, `>=`, `!=`, `==` | `a == b` | comparison |
| 10 | `not` | `not x` | negation |
| 11 | `and` | `x and y` | logical and |
| 12 | `or` | `x or y` | logical or |
| 13 | `:=` (walrus) | `if (n := len(s)) > 3:` | assignment expression |

Two things to internalise:

- **`not` binds tighter than `and` and `or`, but looser than comparisons.** So
  `not x == y` means `not (x == y)`, and `not x and y` means `(not x) and y`.
- **Comparison operators chain**, as you saw above.

```python
x = 5
y = 10

print(not x == y)          # False — means "not (x == y)"
print(not x and y)         # False — means "(not x) and y"
print(-2 ** 2)             # -4  — unary minus binds looser than **
print(2 ** 3 ** 2)         # 512 — ** is right-associative
```

### The golden rule

**Use parentheses for anything you are not completely sure about.** Parentheses are not
clutter; they are documentation that the next human (including you in three months) will
read. The cost of one pair of parentheses is zero. The cost of an hour debugging a
misplaced precedence is not.

```python
# Instead of relying on your memory:
a, b, c, d, e = 2, 3, 4, 20, 5
result = a + b * c > d / e
print(result)

# Write what you mean:
result = (a + (b * c)) > (d / e)
print(result)
```

---

## A quick tour of the `math` module

Python ships with a huge **standard library** — a collection of modules that come with the
interpreter, no installation needed. You will meet it properly in
[14 — Standard library](14-standard-library.md), but `math` is the one you need earliest,
because it is the vocabulary of AI mathematics.

```python
import math

print(math.pi)             # 3.141592653589793
print(math.e)              # 2.718281828459045
print(math.tau)            # 6.283185307179586  (2 * pi)

print(math.sqrt(16))       # 4.0
print(math.floor(3.9))     # 3    -> the largest int <= 3.9
print(math.ceil(3.1))      # 4    -> the smallest int >= 3.1
print(math.pow(2, 10))     # 1024.0
print(math.factorial(5))   # 120
print(math.log(math.e))    # 1.0  — natural logarithm
print(math.log(8, 2))      # 3.0  — logarithm with an explicit base
```

Note `math.floor` and `math.ceil` return **integers**, while `int()` truncates toward zero.
For negative numbers those are different:

```python
import math

print(int(-3.9))       # -3  (toward zero)
print(math.floor(-3.9))  # -4  (toward negative infinity)
print(math.ceil(-3.9))   # -3  (toward positive infinity)
```

`math.log(x, base)` is worth remembering: logarithms appear constantly in machine learning
because cross-entropy loss is a negative log-probability.

```python
import math

# Cross-entropy for a model that assigned 0.3 probability to the right answer
loss = -math.log(0.3)
print(f"cross-entropy loss: {loss:.4f} nats")

# The same thing with a different base
loss_bits = -math.log2(0.3)
print(f"cross-entropy loss: {loss_bits:.4f} bits")
```

```text
cross-entropy loss: 1.2040 nats
cross-entropy loss: 1.7370 bits
```

---

## 🧪 Try it yourself

Do these without looking at the hints. Type the code, run it, read the output, change
something and run it again.

### Exercise 1 — Type detective

Write a script that prints the `type()` of each of these values, and uses `isinstance()` to
check whether each is an `int`:
`42`, `42.0`, `"42"`, `True`, `None`.

<details>
<summary>Hint</summary>

`isinstance(value, int)` returns `True` if the value is an `int` **or a subclass of it**.
Remember that `bool` is a subclass of `int` in Python — that will surprise you.
</details>

<details>
<summary>Solution</summary>

```python
values = [42, 42.0, "42", True, None]

for value in values:
    print(f"{value!r:>6}  type={type(value).__name__:>9}  "
          f"isinstance(int)={isinstance(value, int)}")
```

```text
    42  type=      int  isinstance(int)=True
  42.0  type=    float  isinstance(int)=False
  '42'  type=      str  isinstance(int)=False
  True  type=     bool  isinstance(int)=True
  None  type= NoneType  isinstance(int)=False
```

`True` is an `int` because `bool` is defined as a subclass of `int`. That is why
`isinstance(True, int)` is `True`.
</details>

### Exercise 2 — Predict the result

Before running anything, write down what each of these prints. Then run the file and check
yourself. Getting all eight right means you have genuinely mastered precedence.

1. `7 / 2`
2. `7 // 2`
3. `7 % 2`
4. `-7 // 2`
5. `-7 % 2`
6. `2 ** 3 ** 2`
7. `-2 ** 2`
8. `not 1 == 2`

<details>
<summary>Hint</summary>

Division always produces a float. `//` floors toward negative infinity, `%` follows the
sign of the divisor. `**` is right-associative. Unary minus binds *looser* than `**` but
*tighter* than `*`.
</details>

<details>
<summary>Solution</summary>

```python
print(7 / 2)          # 3.5
print(7 // 2)         # 3
print(7 % 2)          # 1
print(-7 // 2)        # -4
print(-7 % 2)         # 1
print(2 ** 3 ** 2)    # 512   -> 2 ** (3 ** 2)
print(-2 ** 2)        # -4   -> -(2 ** 2)
print(not 1 == 2)     # True  -> not (1 == 2)
```
</details>

### Exercise 3 — The temperature guard

An LLM API call should be rejected if the temperature is outside the range 0.0 to 2.0
inclusive. Write code that:

- takes a `temperature` value,
- uses a **chained comparison** to decide whether it is valid,
- prints a clear message either way,
- and correctly rejects `None` (use `is None`, not `==`).

<details>
<summary>Hint</summary>

`None` in a chained comparison raises `TypeError`, so you must check for it *first*, and
separately. Chained comparisons short-circuit, so `temperature is not None and 0.0 <= temperature <= 2.0`
is safe — the right side only runs if the left side was `True`.
</details>

<details>
<summary>Solution</summary>

```python
def check_temperature(temperature):
    if temperature is None:
        return "rejected: no temperature supplied"
    if 0.0 <= temperature <= 2.0:
        return f"accepted: temperature={temperature}"
    return f"rejected: temperature={temperature} is outside [0.0, 2.0]"


print(check_temperature(0.7))
print(check_temperature(3.5))
print(check_temperature(None))
```

```text
accepted: temperature=0.7
rejected: temperature=3.5 is outside [0.0, 2.0]
rejected: no temperature supplied
```
</details>

### Exercise 4 — Money that adds up

Write a function `line_total(unit_price, quantity)` that returns the total as a `Decimal`,
so that `Decimal("0.10") * 3` is exactly `0.30` and not `0.30000000000000004`.

Then prove the float version breaks, by also writing a float version and comparing the two
totals with `==`.

<details>
<summary>Hint</summary>

`Decimal` only stays exact if you build it from a **string**. `Decimal(0.10)` inherits the
float's error.
</details>

<details>
<summary>Solution</summary>

```python
from decimal import Decimal


def line_total_exact(unit_price, quantity):
    return Decimal(str(unit_price)) * quantity


def line_total_float(unit_price, quantity):
    return unit_price * quantity


exact = line_total_exact("0.10", 3)
approximate = line_total_float(0.10, 3)

print("exact     :", exact)
print("approximate:", approximate)
print("equal?    :", exact == Decimal("0.30"))
print("float == 0.30:", approximate == 0.30)
```

```text
exact     : 0.30
approximate: 0.30000000000000004
equal?    : True
float == 0.30: False
```
</details>

### Exercise 5 — The short-circuit detective

Write three functions: `left()`, `right()`, and `both()`. `left` prints `"left ran"` and
returns `False`. `right` prints `"right ran"` and returns `True`.

Then write two lines that use `and` and `or` with these functions, and predict — before
running — which of the two functions will print in each case.

<details>
<summary>Hint</summary>

`and` stops as soon as it has a falsy result. `or` stops as soon as it has a truthy result.
</details>

<details>
<summary>Solution</summary>

```python
def left():
    print("left ran")
    return False


def right():
    print("right ran")
    return True


print("--- and ---")
result = left() and right()
print("result:", result)

print("--- or ---")
result = right() or left()
print("result:", result)
```

```text
--- and ---
left ran
result: False
--- or ---
right ran
result: True
```

In the `and` case `right` never ran: `left` returned `False`, which already decides the
answer. In the `or` case `left` never ran, because `right` returned `True`.
</details>

---

## ✅ Checkpoint

Answer these without looking back. If you cannot, go and re-read the section it came from.

1. What does `type(None)` return, and what is the *name* of that type?
2. Is `None == False`? Why does that matter in real code?
3. What is the difference between `7 / 2` and `7 // 2`?
4. In Python, what is the sign of the result of `-7 % 2`, and why?
5. Why is `0.1 + 0.2 != 0.3`? Give the one-sentence version.
6. What is the recommended way to compare two floats for "close enough"?
7. What does `2 ** 100` return, and what is that called?
8. What does `nan == nan` evaluate to, and what must you use instead?
9. Why should you write `x is None` rather than `x == None`?
10. What are the three values that make `and` stop early?
11. Which of these is truthy: `0`, `""`, `"0"`, `[]`?
12. What does `0 <= score <= 10` evaluate to when `score` is `7`?
13. In `not x == y`, which comparison happens first?
14. What does `bool("False")` return, and why?

<details>
<summary>Answers</summary>

1. `<class 'NoneType'>`. The type's name is `NoneType`.
2. No, it is `False`. They mean different things: "no value" versus "explicitly false".
   Conflating them makes guards misfire.
3. `/` is true division and always returns a `float` (`3.5`). `//` is floor division and
   returns an `int` (`3`).
4. `1` — the result takes the sign of the divisor. Python's modulo is defined so that
   `a == (a // b) * b + (a % b)` always holds.
5. Because `0.1` and `0.2` cannot be represented exactly in binary floating point, so the
   stored approximations do not add up to the stored approximation of `0.3`.
6. `math.isclose(a, b)`.
7. `1267650600228229401496703205376` — Python integers have *arbitrary precision*.
8. `False`. Use `math.isnan(x)`, and check for NaN before any comparison.
9. Because `is` compares identity and `==` compares value; a custom class can define `__eq__`
   to claim it equals `None`. `is None` cannot be fooled.
10. `and` stops at the first falsy operand; `or` stops at the first truthy operand;
    `not` takes only one operand so it never short-circuits anything.
11. `"0"` — it is a non-empty string. `0`, `""` and `[]` are all falsy.
12. `True`. It is shorthand for `0 <= score and score <= 10`.
13. The comparison `x == y` happens first, because comparisons bind tighter than `not`. So it
    means `not (x == y)`.
14. `True`. Python checks whether the string is empty, not what it says. Any non-empty
    string is truthy.
</details>

---

## 🐛 Common mistakes

| Mistake | What you see | Fix |
|---|---|---|
| Comparing `None` with `==` | Works today, then a custom class with `__eq__` makes it lie | Use `x is None` and `x is not None` |
| `int("forty two")` | `ValueError: invalid literal for int()` | Validate first, or use `try`/`except ValueError` around the conversion |
| Assuming `0.1 + 0.2 == 0.3` | `False`, and `0.30000000000000004` in the output | Use `math.isclose(a, b)`; use `Decimal` for money |
| Using `==` to compare floats for exactness | A test passes locally and fails in production | Never compare floats with `==` unless the values come from the same computation |
| `bool("False")` | `True`, and your feature flag is always on | Store flags as real `bool` values, not strings |
| Dividing by `/` when you meant a whole number | `3.0` instead of `3`, and a `TypeError` in a `range()` call | Use `//` for floor division, and remember `range()` rejects floats |
| `x is 1000` to compare numbers | `False` for equal values, and it may change between Python versions | Use `==` for numbers; reserve `is` for `None` |
| Forgetting that `//` floors toward negative infinity | `math.floor(-3.9)` gives `-4` but `int(-3.9)` gives `-3` | Pick `int()`, `math.floor()` or `math.ceil()` deliberately |
| Comparing numeric strings with `<` | `"10" < "9"` is `True` | Convert to `int`/`float` before comparing |

---

## 🔗 Resources

- [Built-in Types — Python documentation](https://docs.python.org/3/library/stdtypes.html) —
  the reference for every built-in type, including the exact truthiness rules.
- [Truth Value Testing — Python documentation](https://docs.python.org/3/library/stdtypes.html#truth-value-testing) —
  the official list of which values count as false.
- [Expressions — Python Language Reference](https://docs.python.org/3/reference/expressions.html) —
  the authoritative grammar for operators, precedence and comparisons.
- [Floating Point Arithmetic: Issues and Limitations](https://docs.python.org/3/tutorial/floatingpoint.html) —
  the official explanation of why `0.1 + 0.2 != 0.3`, written by the Python team.
- [The Floating-Point GUI](https://floating-point-gui.de/) — a visual, interactive page that
  shows exactly which numbers a float can and cannot represent.
- [math — Python documentation](https://docs.python.org/3/library/math.html) — every function
  in the `math` module, with worked examples.
- [decimal — Python documentation](https://docs.python.org/3/library/decimal.html) — exact
  base-10 arithmetic for money and anything else where the digits must add up.
- [Built-in Functions](https://docs.python.org/3/library/functions.html) — reference for
  `int()`, `float()`, `str()`, `bool()`, `round()`, `divmod()` and friends.
- [Glossary](https://docs.python.org/3/glossary.html) — the official definitions of
  "truthy", "falsy", "identity", "value" and every other term used on this page.
- [CPython on GitHub](https://github.com/python/cpython) — the source of the interpreter
  itself, if you ever want to see how `int` really works.

---

## ➡️ Next

- [04 — Control flow](04-control-flow.md) — now that you can hold and compare values, you
  can make your program *decide*: `if` statements, `for` and `while` loops, and the
  `for ... else` construct that trips up almost everybody.

**← Previous:** [02 — Syntax and variables](02-syntax-and-variables.md)
