# Control flow

Control flow is how you tell a program what to do **and when**. So far your programs have
run straight down the page, one line after another, doing the same thing every time. This
file adds the three things that make a program useful: making decisions, repeating work, and
stopping early. Every real program — every agent, every API handler, every data pipeline — is
built out of these three ideas.

> **⏱️ Time:** ~35 minutes
> **📚 Prereqs:** [03 — Data types and operators](03-data-types-and-operators.md)
> **🎯 By the end you can:** write branching logic with `if`/`elif`/`else`, loop over data
> with `for` and `while`, and use `break`, `continue` and the `for ... else` construct to
> control exactly how long a loop runs.

---

## Why this matters for AI engineering

The core of an agent is a decision loop: look at the current state, decide what to do, do it,
look again. That is `while` plus `if`. Routing a user's request to the right tool is a chain
of `if`/`elif`. Cleaning a scraped document is a `for` loop with a `continue` to skip the
junk. Reading 200 API responses concurrently is a loop with a timeout guard.

When an agent misbehaves, the cause is almost always a control-flow mistake: a condition that
never becomes true, a loop that never ends, an `off-by-one` that drops the last token, or a
`break` in the wrong place. Learn this file properly and you will debug agents by reading
their branching logic instead of guessing.

---

## Making decisions with `if`

The `if` statement runs a block of code only when a **condition** is truthy.

```python
temperature = 0.7

if temperature > 1.0:
    print("High temperature — output will be more random.")
else:
    print("Normal temperature.")
```

```text
Normal temperature.
```

### Indentation is the syntax

Python uses indentation, not braces, to mark blocks of code. The rule is simple and absolute:

- The line after `if ...:` **must** be indented.
- Everything indented under it belongs to the `if`.
- The indentation must be consistent — use **4 spaces** per level, always.

```python
if True:
    print("This is inside the if.")
    print("So is this.")
print("This is outside the if.")
```

Indentation is not decoration. It *is* the structure of the program. One stray space at the
wrong level changes what your code does, and Python will usually tell you loudly
(`IndentationError`) rather than silently.

### The condition does not have to be a `bool`

Remember from [03 — Data types and operators](03-data-types-and-operators.md) that Python
treats any value as either truthy or falsy. A condition can therefore be:

```python
messages = []

if messages:                      # truthy check on the list itself
    print(f"{len(messages)} messages to send.")
else:
    print("Nothing to send.")
```

```text
Nothing to send.
```

An empty list is falsy, so `if messages:` is a compact, idiomatic "is there anything here?"
test. It is the most common conditional in Python after a plain `if x == y`.

---

## `elif` and `else`

When you have more than two branches, use `elif` ("else if") for the middle cases and `else`
for the fallback. Only **one** branch ever runs.

```python
usage_percent = 78

if usage_percent >= 90:
    tier = "critical"
elif usage_percent >= 70:
    tier = "warning"
elif usage_percent >= 40:
    tier = "normal"
else:
    tier = "idle"

print("Quota status:", tier)
```

```text
Quota status: warning
```

Python checks the conditions **top to bottom** and stops at the first true one. That ordering
is not cosmetic — it is why the `>= 90` test must come before `>= 70`.

There is a common bug here. This looks right but is not:

```python
# BUG: the first condition swallows everything above 40.
usage_percent = 78

if usage_percent >= 40:
    tier = "normal"
elif usage_percent >= 90:
    tier = "critical"

print("tier:", tier, "<- wrong: 78 should be a warning")
```

```text
tier: normal <- wrong: 78 should be a warning
```

### A picture of the flow

```text
        usage_percent = 78
                |
                v
        +-------------------+
        |  78 >= 90 ?       |---- yes ---> tier = "critical"
        +-------------------+
                | no
                v
        +-------------------+
        |  78 >= 70 ?       |---- yes ---> tier = "warning"
        +-------------------+
                | no
                v
        +-------------------+
        |  78 >= 40 ?       |---- yes ---> tier = "normal"
        +-------------------+
                | no
                v
        tier = "idle"

    Exactly one branch runs.
```

---

## Combining conditions

You can join conditions with `and` (both must hold) and `or` (at least one must hold).

```python
score = 0.82
latency_ms = 240

if score > 0.8 and latency_ms < 500:
    print("Send this response to the user.")
```

### The two classic traps

**Trap 1 — mixing `and` and `or` without parentheses.** `and` binds tighter than `or`, so
`A and B or C` is evaluated as `(A and B) or C`, not as `A and (B or C)`. Those are
different programs.

```python
score = 0.5
model = "small-model"
temperature = 0.2

# What the author meant: a high score, on a big model, with a low temperature.
if score > 0.9 and (model == "gpt-4o" or temperature < 0.3):
    print("accept (careful version)")

# What the code actually says: (high score AND big model) OR (low temperature).
if score > 0.9 and model == "gpt-4o" or temperature < 0.3:
    print("accept (what Python actually evaluates)")
```

```text
accept (what Python actually evaluates)
```

The careless version accepted a request with a *low* score, because the low temperature
was enough on its own. That is a silent bug, not a crash — the worst kind.

**Trap 2 — forgetting that `and`/`or` return operands, not booleans.** The expressions
`is_ready` and `has_error` might hold strings or lists, and `and` will hand you one of them
rather than `True`/`False`.

### De Morgan's law, in plain words

De Morgan's law says that you can push `not` inside by flipping `and` to `or` and back:

```text
not (A and B)  ==  (not A) or  (not B)
not (A or B)   ==  (not A) and (not B)
```

In code:

```python
A = True
B = False

print(not (A and B))      # True
print((not A) or (not B)) # True  <- the same thing, rewritten
```

This is genuinely useful, not just trivia. "It is not the case that both A and B hold"
becomes "A failed, or B failed" — which is often easier to read, and lets you attach a
specific error message to each failure.

```python
def validate_request(api_key, prompt):
    if not api_key or not prompt:
        return "Rejected: you need both an API key and a prompt."
    if not api_key:
        return "Rejected: missing API key."
    if not prompt:
        return "Rejected: missing prompt."
    return "Accepted."


print(validate_request("sk-123", "hello"))
print(validate_request("", "hello"))
print(validate_request("sk-123", ""))
```

Rewriting the first check with De Morgan gives "missing api key **or** missing prompt",
which is exactly what the message says. The later two checks then give the *specific* reason.

---

## The ternary expression

Sometimes a value is simply "one thing or the other, depending on a condition". Python has a
one-line syntax for it:

```python
latency_ms = 240
status = "ok" if latency_ms < 500 else "slow"
print(status)
```

Read it as: *the value before `if` if the condition holds, otherwise the value after `else`*.

```python
score = 0.42
label = "confident" if score > 0.7 else "uncertain"
print(label)
```

```text
uncertain
```

**When it helps:** short, symmetric choices between two values, especially when assigning to
a variable.

**When it hurts:** when the two branches are long, when there is more than one condition, or
when you find yourself writing a ternary inside a call inside a ternary. At that point, use
a real `if`/`else` block.

```python
status_code = 503

# Fine
severity = "error" if status_code >= 500 else "info"
print(severity)

# Too dense — switch to an if/else block
severity = "error" if status_code >= 500 else "warning" if status_code >= 400 else "info"
print(severity)
```

---

## Looping with `for`

A `for` loop walks through a **sequence** — a list, a string, a tuple, a dictionary, a file's
lines — and runs your block once per item.

```python
document_ids = ["doc-1", "doc-2", "doc-3"]

for document_id in document_ids:
    print("Indexing", document_id)
```

```text
Indexing doc-1
Indexing doc-2
Indexing doc-3
```

The variable after `in` is the **loop variable**. It is reassigned on every pass, and it
holds the last value when the loop finishes.

```python
languages = ["python", "rust", "go"]

for language in languages:
    last_seen = language

print("Last language:", last_seen)
print("Loop variable:", language)
```

```text
Last language: go
Loop variable: go
```

You can also loop over a string, which gives you one character at a time:

```python
for character in "AI":
    print(character)
```

```text
A
I
```

---

## `range()` — and the off-by-one that haunts everyone

`range()` generates a sequence of numbers. Its signature is:

```text
range(stop)             -> 0, 1, 2, ..., stop - 1
range(start, stop)      -> start, start + 1, ..., stop - 1
range(start, stop, step)-> start, start + step, ..., up to stop
```

**The `stop` value is EXCLUSIVE.** The range never includes it. This is the single most
common off-by-one bug in Python, and it is a deliberate design choice: `range(len(items))`
is the correct way to index a list, because the last valid index is `len(items) - 1`.

```python
print(list(range(5)))       # [0, 1, 2, 3, 4]      <- 5 is NOT included
print(list(range(2, 6)))    # [2, 3, 4, 5]
print(list(range(0, 10, 3)))  # [0, 3, 6, 9]
print(list(range(5, 0, -1)))  # [5, 4, 3, 2, 1]     <- step can be negative
```

```python
scores = [0.5, 0.7, 0.9]

for index in range(len(scores)):
    print(index, scores[index])
```

```text
0 0.5
1 0.7
2 0.9
```

Two things to remember: `range()` does not build a list in memory — it is a lazy object that
produces numbers on demand, so `range(10_000_000)` costs almost nothing. And `range()` only
works with **integers**: `range(2.5)` raises `TypeError`. If you need fractional steps, use
`while` instead.

### The classic off-by-one, side by side

```python
items = ["a", "b", "c", "d"]

# WRONG: index 4 does not exist
try:
    for i in range(len(items) + 1):
        print(i, items[i])
except IndexError as error:
    print("IndexError:", error)
```

```text
0 a
1 b
2 c
3 d
IndexError: list index out of range
```

```python
items = ["a", "b", "c", "d"]

# RIGHT: range(len(items)) covers 0, 1, 2, 3
for i in range(len(items)):
    print(i, items[i])
```

```text
0 a
1 b
2 c
3 d
```

---

## `while` loops

A `while` loop repeats **as long as a condition stays true**. Use it when you do not know
how many times you need to iterate.

```python
retries = 0
max_retries = 3

while retries < max_retries:
    retries += 1
    print(f"Attempt {retries} of {max_retries}")

print("Giving up after", retries, "attempts.")
```

```text
Attempt 1 of 3
Attempt 2 of 3
Attempt 3 of 3
Giving up after 3 attempts.
```

The condition is checked **before** each pass, so a `while` whose condition starts false never
runs at all.

### Guaranteeing termination

A `while` loop that never ends is an **infinite loop** — the program hangs, and you usually
have to kill it with `Ctrl+C`. Two habits prevent this:

1. **Make sure the condition can eventually become false.** Put a counter in the condition.
2. **Give it a hard limit.** An explicit `max_iterations` ceiling turns a hang into a clean
   error.

```python
def stream_until_done(chunks, max_iterations=1000):
    processed = 0

    while chunks and processed < max_iterations:
        chunk = chunks.pop(0)
        processed += 1
        print("processed", chunk)

    if processed >= max_iterations:
        print("Stopped: hit the iteration limit.")
    else:
        print("Finished normally.")


stream_until_done(["a", "b", "c"])
```

```text
processed a
processed b
processed c
Finished normally.
```

In production AI code, the second habit is not optional. A `while` loop that consumes a
network stream, a queue or a tool must have a ceiling, or one flaky API response will hang
your agent forever.

---

## `break`, `continue` and `pass`

Three keywords control the inside of a loop.

| Keyword | What it does |
|---|---|
| `break` | leave the loop immediately, skip the rest of the body |
| `continue` | skip the rest of this pass, go straight to the next item |
| `pass` | do nothing at all — a placeholder so the block is valid Python |

```python
numbers = [3, 7, 11, 4, 18, 9]

for number in numbers:
    if number < 5:
        continue          # skip this one
    if number > 15:
        break             # stop the whole loop
    print("keeping", number)
```

```text
keeping 7
keeping 11
```

The loop stopped at `18`, because `18 > 15` triggered the `break`. The `9` at the end of
the list was never reached.

`pass` exists because Python needs *something* after a `:`. It is useful as a placeholder
when you are writing a class or function you have not finished yet.

```python
class Placeholder:
    pass


def not_written_yet():
    pass


print("Placeholder exists:", Placeholder.__name__)
print("not_written_yet returns:", not_written_yet())
```

---

## `for ... else` and `while ... else`

This one confuses almost everybody the first time, so read it slowly.

Python allows an `else` block on a loop. **The `else` block runs only if the loop finished
normally — that is, it did NOT exit via `break`.**

```python
def find_needle(haystack):
    for item in haystack:
        if item == "needle":
            return f"Found it at position {haystack.index(item)}"
    else:
        return "Not found."


print(find_needle(["hay", "straw", "needle"]))
print(find_needle(["hay", "straw"]))
```

```text
Found it at position 2
Not found.
```

The `return` inside the loop exits the *function*, so the `else` never runs in the first
case. In the second case the loop runs to completion with no `break`, so the `else` runs.

The clearest way to see the rule is to write the `else` against a `break`:

```python
def search(haystack, target):
    for index, item in enumerate(haystack):
        if item == target:
            break                      # leaves the loop -> the else is skipped
    else:
        return f"{target} not found"  # only reached if the loop never broke
    return f"{target} found at index {index}"


print(search(["hay", "straw", "needle"], "needle"))
print(search(["hay", "straw"], "needle"))
```

```text
needle found at index 2
needle not found
```

Read it as: "search all of them, and *if I never broke out*, the answer is 'not found'".

Here is the same thing written the classic "search with early exit" way, where `break` is
used to leave the loop and a flag tracks whether you found it:

```python
def find_needle_classic(haystack):
    found = False

    for item in haystack:
        if item == "needle":
            found = True
            break

    if found:
        return "Found it."
    return "Not found."


print(find_needle_classic(["hay", "straw", "needle"]))
print(find_needle_classic(["hay", "straw"]))
```

Same result, but more lines, an extra variable, and a flag that could get out of sync. This
is the real reason `for ... else` exists: it replaces the flag with the loop's own exit
behaviour.

```text
   +----------------------+
   |   loop body runs     |
   +----------------------+
      |        |        |
      |        |        +--> loop ends normally ---> else: runs
      |        |
      |        +--> break ---> leave the loop ---> (else is skipped)
      |
      +--> continue ---> go to the next item
```

`while ... else` works exactly the same way — the `else` runs when the loop ends because its
condition became false, not because of a `break`.

```python
count = 0

while count < 3:
    count += 1
else:
    print("Loop finished normally, count =", count)
```

```text
Loop finished normally, count = 3
```

A common beginner reaction to `for ... else` is to think the `else` belongs to the `if`
inside the loop. It does not. It belongs to the `for`. If you find it confusing, the classic
flag version above is perfectly fine — but know that `for ... else` is idiomatic Python and
experienced readers expect it.

---

## Nested loops and the O(n²) warning

You can put a loop inside a loop. The outer loop runs once per item, and the inner loop runs
once per item *of that item*.

```python
pairs = []

for user in ["ada", "grace", "alan"]:
    for permission in ["read", "write"]:
        pairs.append(f"{user}:{permission}")

for pair in pairs:
    print(pair)
```

```text
ada:read
ada:write
grace:read
grace:write
alan:read
alan:write
```

That is 3 × 2 = 6 iterations. If both lists had 10,000 items, the inner loop would run
100,000,000 times. This is called **O(n²)** — *quadratic* time — and it is one of the most
common performance traps in data work.

```python
import time

records = list(range(3000))

start = time.perf_counter()
for record in records:
    for other in records:
        pass
nested = time.perf_counter() - start

start = time.perf_counter()
seen = set()
for record in records:
    seen.add(record)
flat = time.perf_counter() - start

print(f"nested loops: {nested:.4f}s")
print(f"single pass : {flat:.4f}s")
```

```text
nested loops: 0.2134s
single pass : 0.0001s
```

The exact numbers vary on your machine, but the ratio does not — expect the nested version
to be hundreds or thousands of times slower. A nested loop over `n` items does `n × n` work;
a single pass with a set does `n` work. When you find yourself nesting
loops over data, look for a set or a dict that lets you do it in one pass. We will build
exactly this optimisation in [06 — Data structures](06-data-structures.md) and
[07 — Comprehensions and iterators](07-comprehensions-and-iterators.md).

---

## `enumerate()` and `zip()`

Two built-in functions that make loops much nicer.

### `enumerate()` — index *and* value

The old-school way to get both is a manual counter, which is ugly and easy to get wrong:

```python
# The manual-counter anti-pattern
index = 0
for name in ["ada", "grace", "alan"]:
    print(index, name)
    index += 1
```

`enumerate()` does it for you:

```python
for index, name in enumerate(["ada", "grace", "alan"]):
    print(index, name)
```

```text
0 ada
1 grace
2 alan
```

It also takes a `start` argument, which is handy when your indices are 1-based:

```python
for line_number, line in enumerate(["first", "second"], start=1):
    print(f"line {line_number}: {line}")
```

```text
line 1: first
line 2: second
```

### `zip()` — two sequences in parallel

`zip()` pairs up items from two (or more) sequences, stopping at the shortest one.

```python
names = ["ada", "grace", "alan"]
scores = [98, 105, 88]

for name, score in zip(names, scores):
    print(f"{name} scored {score}")
```

```text
ada scored 98
grace scored 105
alan scored 88
```

**Watch out:** `zip()` stops at the shortest sequence and silently discards the rest. If
`names` has 3 items and `scores` has 2, you get 2 pairs and no warning. When that matters,
check the lengths first, or use `zip(..., strict=True)` (Python 3.10+), which raises an
error instead of silently truncating.

```python
names = ["ada", "grace", "alan"]
scores = [98, 105]

try:
    for name, score in zip(names, scores, strict=True):
        print(name, score)
except ValueError as error:
    print("Mismatched lengths:", error)
```

```text
ada 98
grace 105
Mismatched lengths: zip() argument 2 is shorter than argument 1
```

---

## `break`/`continue` versus `return`

These three do similar-looking things, and choosing the right one keeps functions readable.

| Statement | What it does |
|---|---|
| `break` | leaves the nearest loop |
| `continue` | skips to the next iteration of the nearest loop |
| `return` | leaves the **entire function**, handing a value back to the caller |

The rule of thumb:

- Use `break` when you have found what you were looking for and the rest of the data is
  irrelevant.
- Use `continue` when *this one item* is uninteresting but the others are fine.
- Use `return` when the function's job is done — it makes the exit explicit and stops the
  loop for you.

```python
def first_long_paragraph(paragraphs, limit=200):
    for paragraph in paragraphs:
        if len(paragraph) >= limit:
            return paragraph          # the function is finished; no flag needed
    return None


def clean_lines(lines):
    cleaned = []
    for line in lines:
        line = line.strip()
        if not line:
            continue                  # skip blanks, keep going
        cleaned.append(line)
    return cleaned


paragraph = first_long_paragraph(["short", "x" * 250, "y" * 300])
print("length of the first long paragraph:", len(paragraph))
print(clean_lines(["  hello  ", "", "   ", "world"]))
```

```text
length of the first long paragraph: 250
['hello', 'world']
```

Using `return` to exit early is one of the most valuable habits in Python. It removes the
need for flags, removes the need for deeply nested `if` blocks, and makes each exit point
obvious.

---

## The `match` statement (Python 3.10+)

`match` is a newer way to write a multi-way branch. It reads like a switch statement from
other languages, but it can do more.

```python
def route(command):
    match command:
        case "start":
            return "starting"
        case "stop":
            return "stopping"
        case "restart" | "reload":
            return "restarting"
        case _:
            return "unknown command"


print(route("start"))
print(route("reload"))
print(route("fly"))
```

```text
starting
restarting
unknown command
```

Compare with the `if`/`elif` version of the same thing:

```python
def route_old(command):
    if command == "start":
        return "starting"
    elif command == "stop":
        return "stopping"
    elif command == "restart" or command == "reload":
        return "restarting"
    else:
        return "unknown command"


print(route_old("start"))
print(route_old("reload"))
print(route_old("fly"))
```

```text
starting
restarting
unknown command
```

**When `match` wins:**

- You are matching a value against **several literal options** — it is much shorter than a
  chain of `elif`s.
- You want to match on **type** or **structure**, not just equality.
- You are matching against **literal patterns** like strings, numbers, or sequences.

```python
def describe(value):
    match value:
        case int() | float():
            return "a number"
        case str() as text if len(text) > 3:
            return f"a long string: {text}"
        case str():
            return "a short string"
        case None:
            return "nothing at all"
        case _:
            return "something else"


print(describe(42))
print(describe("hello"))
print(describe("hi"))
print(describe(None))
print(describe([1, 2]))
```

```text
a number
a long string: hello
a short string
nothing at all
something else
```

Note the two extras: `case int() | float():` matches on **type**, and
`case str() as text if len(text) > 3:` uses `as` to **capture** the value plus an `if`
**guard** to add a condition.

**When `if`/`elif` wins:**

- You are comparing two *variables* against each other rather than against fixed values
  (`if score > threshold:`). `match` cannot do that without a guard.
- You are branching on a boolean flag.
- Your audience (or your linter) prefers the older, more widely understood form.

`match` is covered again, along with other modern-Python syntax, in
[11 — Type hints and modern Python](11-type-hints-and-modern-python.md). If you are ever
unsure, `if`/`elif` is always correct.

---

## Common loop bugs

### 1. The infinite loop

Here is a loop that never ends. It is shown as text because **running it would hang your
terminal** — that is the entire point of the example.

```text
count = 0
while count < 5:
    print("working...", count)
```

`count` is never incremented, so `count < 5` stays `True` forever. Press `Ctrl+C` to stop
it. The fix is always the same: make sure something inside the loop changes the condition.

```python
count = 0

while count < 5:
    print("working...", count)
    count += 1          # <- the line that was missing
```

```text
working... 0
working... 1
working... 2
working... 3
working... 4
```

### 2. The off-by-one

Already covered: `range(len(items))`, not `range(len(items) + 1)`.

### 3. Mutating a list while iterating over it

This one produces genuinely surprising behaviour. When you **append** to a list during a
`for` loop over that list, the loop picks up the new items too — because `for` does not
snapshot the list; it keeps asking for the next element until the list is exhausted.

```python
items = [1, 2, 3]

for item in items:
    if item == 2:
        items.append(4)
    print("saw", item)
```

```text
saw 1
saw 2
saw 3
saw 4
```

The loop visited `4`, a value that was added *after* the loop started. It did not crash — it
just did something you did not plan.

Removing items is worse, because the loop skips elements:

```python
items = [1, 2, 3, 4]

for item in items:
    if item == 2:
        items.remove(item)
    print("saw", item)
```

```text
saw 1
saw 2
saw 4
```

Note that `3` was **skipped**. The `2` was removed from under the loop, which shifted every
later item one place to the left, so the loop's next position landed on `4` instead of `3`.
The safe pattern is to build a **new** list:

```python
items = [1, 2, 3, 4]
kept = []

for item in items:
    if item != 2:
        kept.append(item)

print("kept:", kept)
print("original:", items)
```

```text
kept: [1, 3, 4]
original: [1, 2, 3, 4]
```

### 4. The "loop variable leaks" myth

You may have heard that loop variables "leak" out of the loop and clobber other variables.
**In Python, that is not true.** Python has no block scope; names live in the enclosing
function. A loop variable keeps its final value after the loop, but it does not overwrite
anything you did not assign it to.

```python
for i in range(3):
    pass

print("i is still bound to:", i)   # 2 — it exists, but it is harmless
```

```python
def counter_bug():
    total = 0
    for total in [10, 20, 30]:
        pass
    return total


print(counter_bug())   # 30 — the loop variable DID clobber total,
                       #     because we gave it the same name.
```

That is the real hazard, and it is not "leaking" — it is simply reusing a name. The fix is
to give the loop variable a distinct name:

```python
def counter_fixed():
    total = 0
    for value in [10, 20, 30]:
        total += value
    return total


print(counter_fixed())   # 60
```

The "leaking" behaviour you may have heard about is real in **JavaScript** with `var`, and
in old **C**, where a variable declared inside a block stays alive after the block. Python's
scoping rules (which you will meet properly in
[05 — Functions](05-functions.md)) do not behave that way.

---

## A decision table: routing a user request to a tool

Here is a small, complete example that ties the whole file together. The task: an agent
receives a free-text request and must pick which tool to call.

| Condition on the request | Tool to call |
|---|---|
| mentions weather, forecast, temperature | `get_weather` |
| mentions search, find, look up | `web_search` |
| mentions email, message, send | `send_email` |
| mentions calendar, meeting, schedule | `manage_calendar` |
| mentions code, python, function | `run_code` |
| nothing matched | `ask_clarification` |

```python
TOOLS = {
    "get_weather": "Gets the current weather for a city.",
    "web_search": "Searches the web and returns result snippets.",
    "send_email": "Sends an email to a recipient.",
    "manage_calendar": "Creates, moves or cancels calendar events.",
    "run_code": "Runs a snippet of Python and returns stdout.",
    "ask_clarification": "Asks the user a follow-up question.",
}


def route_request(user_request):
    """Pick the best tool for a user's request."""
    request = user_request.lower()

    if "weather" in request or "forecast" in request:
        return "get_weather"
    if "search" in request or "look up" in request:
        return "web_search"
    if "email" in request or "send" in request:
        return "send_email"
    if "calendar" in request or "meeting" in request:
        return "manage_calendar"
    if "code" in request or "python" in request:
        return "run_code"
    return "ask_clarification"


for request in [
    "What's the weather in Lisbon?",
    "Search for recent papers on RAG",
    "Send an email to Ada about the release",
    "Schedule a meeting for Thursday",
    "Run code that counts vowels",
    "Do a barrel roll",
]:
    tool = route_request(request)
    print(f"{request:<42} -> {tool}")
```

```text
What's the weather in Lisbon?              -> get_weather
Search for recent papers on RAG            -> web_search
Send an email to Ada about the release     -> send_email
Schedule a meeting for Thursday            -> manage_calendar
Run code that counts vowels                -> run_code
Do a barrel roll                           -> ask_clarification
```

Two things to notice. First, `in` on a string is doing the heavy lifting — you do not need
a real NLP model to get a working first version of a router. Second, the ordering of the
`if` statements is the whole design: whoever writes the *most specific* rule first wins. As
your router grows, this chain of conditionals becomes the thing you will want to replace
with something more structured — and
[05 — Functions](05-functions.md) shows you how to pull each rule into its own function.

---

## 🧪 Try it yourself

### Exercise 1 — Grade bands

Write a function `grade(score)` that returns a letter grade:

- `90` or above: `"A"`
- `80` to `89`: `"B"`
- `70` to `79`: `"C"`
- `60` to `69`: `"D"`
- below `60`: `"F"`

The score may be `None` — return `"no score"` for that case. Then test it with a loop over a
list of scores including `None`.

<details>
<summary>Hint</summary>

Check `score is None` **first** and return early. Then use `if`/`elif`/`else` with the
thresholds in descending order, so you never need an `and`.
</details>

<details>
<summary>Solution</summary>

```python
def grade(score):
    if score is None:
        return "no score"
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"


for score in [95, 83, 71, 65, 42, None]:
    print(f"{str(score):>5} -> {grade(score)}")
```

```text
   95 -> A
   83 -> B
   71 -> C
   65 -> D
   42 -> F
 None -> no score
```
</details>

### Exercise 2 — FizzBuzz with a twist

Write a loop that prints the numbers 1 to 20, but:

- prints `"fizz"` instead of numbers divisible by 3,
- prints `"buzz"` instead of numbers divisible by 5,
- prints `"fizzbuzz"` for numbers divisible by both,
- and prints the number itself otherwise.

Then rewrite it using a **chained comparison** to check divisibility in one condition.

<details>
<summary>Hint</summary>

`n % 3 == 0` is the divisibility test. For the chained version, `n % 15 == 0` covers both
cases at once, because 15 is the lowest common multiple of 3 and 5.
</details>

<details>
<summary>Solution</summary>

```python
for number in range(1, 21):
    if number % 3 == 0 and number % 5 == 0:
        print("fizzbuzz")
    elif number % 3 == 0:
        print("fizz")
    elif number % 5 == 0:
        print("buzz")
    else:
        print(number)
```

```text
1
2
fizz
4
buzz
fizz
7
8
fizz
buzz
11
fizz
13
14
fizzbuzz
16
17
fizz
19
buzz
```

The chained-comparison rewrite:

```python
for number in range(1, 21):
    if number % 15 == 0:
        print("fizzbuzz")
    elif number % 3 == 0:
        print("fizz")
    elif number % 5 == 0:
        print("buzz")
    else:
        print(number)
```
</details>

### Exercise 3 — Find the first long word

Write a function `first_long_word(sentence, limit=8)` that returns the **first** word in the
sentence with at least `limit` characters, or `None` if there is no such word. Use a
`for ... else:` block.

Then write a second version that returns the **longest** word, using `max()` with a `key`.

<details>
<summary>Hint</summary>

In the `for ... else` version, `break` when you find the word, then set a result variable
*before* the loop. The `else` block handles the "not found" case. The `max` version needs
`max(words, key=len)`.
</details>

<details>
<summary>Solution</summary>

```python
def first_long_word(sentence, limit=8):
    result = None
    for word in sentence.split():
        if len(word) >= limit:
            result = word
            break
    else:
        result = None
    return result


def longest_word(sentence):
    words = sentence.split()
    if not words:
        return None
    return max(words, key=len)


sentence = "the extraordinarily quick brown fox jumps over lazy dogs"
print(first_long_word(sentence))
print(longest_word(sentence))
print(first_long_word("too short"))
print(longest_word(""))
```

```text
extraordinarily
extraordinarily
None
None
```
</details>

### Exercise 4 — Fix the infinite loop

This code never ends (it is shown as text because running it would hang your terminal).
Fix it in two different ways: once with a counter, once with a `max_iterations` ceiling.
Then explain in a comment why the ceiling version is the safer one for production code.

```text
items = ["a", "b", "c"]
index = 0

while index < len(items):
    print(items[index])
```

<details>
<summary>Hint</summary>

The bug: `index` never changes, so `index < len(items)` stays `True` forever. The fix is
`index += 1` inside the loop body.
</details>

<details>
<summary>Solution</summary>

```python
# Fix 1: a counter that actually advances.
items = ["a", "b", "c"]
index = 0

while index < len(items):
    print(items[index])
    index += 1

# Fix 2: a hard ceiling, so even a logic bug cannot hang the program.
def process(items, max_iterations=100):
    index = 0
    processed = 0

    while index < len(items) and processed < max_iterations:
        print(items[index])
        index += 1
        processed += 1

    if processed >= max_iterations:
        print("Stopped: hit the iteration limit.")


process(["a", "b", "c"])
```

```text
a
b
c
a
b
c
```

The ceiling version is safer because it protects against a *different* bug — for example, a
list that keeps growing while you iterate over it.
</details>

### Exercise 5 — `match` versus `if`

Write the same function twice. First with an `if`/`elif` chain, then with a `match`
statement. The function classifies a status code into a label:
`200` → `"ok"`, `404` → `"not found"`, `500` → `"server error"`, anything else → `"unknown"`.

<details>
<summary>Hint</summary>

In `match`, `case 200:` matches the value 200 exactly. The `case _:` wildcard catches
everything else.
</details>

<details>
<summary>Solution</summary>

```python
def classify_if(status_code):
    if status_code == 200:
        return "ok"
    elif status_code == 404:
        return "not found"
    elif status_code == 500:
        return "server error"
    else:
        return "unknown"


def classify_match(status_code):
    match status_code:
        case 200:
            return "ok"
        case 404:
            return "not found"
        case 500:
            return "server error"
        case _:
            return "unknown"


for code in [200, 404, 500, 302]:
    print(code, "->", classify_if(code), "|", classify_match(code))
```

```text
200 -> ok | ok
404 -> not found | not found
500 -> server error | server error
302 -> unknown | unknown
```

The `match` version is shorter and easier to scan. The `if` version is more familiar to
people coming from other languages, and it is the only option when you are comparing two
variables rather than a value against fixed options.
</details>

---

## ✅ Checkpoint

1. What is wrong with forgetting to indent the line after `if x:`?
2. How many branches of an `if`/`elif`/`else` chain can run at once?
3. Why must `if score >= 90:` come before `if score >= 70:`?
4. What does `not (A and B)` equal, in terms of `A` and `B` alone?
5. What is the difference between `break` and `continue`?
6. In `for x in range(2, 8, 2)`, which numbers are produced?
7. Why is `range(len(items))` usually right, and `range(len(items) + 1)` usually wrong?
8. When does the `else` block of a `for` loop run?
9. What is wrong with `zip()` when the two sequences have different lengths?
10. What does `enumerate()` give you that a plain loop does not?
11. What is the difference between `break` and `return`?
12. What happens if you append to a list while iterating over it?
13. Is it true that a loop variable "leaks" and clobbers other variables in Python?
14. What does `case _:` do in a `match` statement?
15. What is O(n²), and when should you worry about it?

<details>
<summary>Answers</summary>

1. Python uses indentation to mark blocks, so an unindented body is a syntax error
   (`IndentationError`, or `expected an indented block`).
2. Exactly one. Python checks conditions top to bottom and stops at the first true one.
3. Because the first true branch wins. If `>= 90` came second, a score of 95 would match
   `>= 70` first and be labelled "B".
4. `(not A) or (not B)`. That is De Morgan's law.
5. `break` leaves the loop entirely; `continue` skips the rest of the current pass and moves
   to the next item.
6. `2, 4, 6`. The `stop` value of 8 is exclusive.
7. Because the last valid index of a list of length *n* is *n - 1*. Adding 1 produces an
   index that does not exist.
8. Only when the loop finished **without** hitting a `break`.
9. It silently stops at the shorter sequence and discards the extra items. Use
   `zip(..., strict=True)` to make it raise instead.
10. The index, alongside the value, without a manual counter.
11. `break` leaves the nearest loop; `return` leaves the entire function and hands a value
    back to the caller.
12. The loop picks up the newly added items, because `for` keeps asking for the next element
    until the sequence is exhausted.
13. No. Python has function-level scope, so a loop variable does not escape the function. It
    does keep its last value after the loop, and reusing a name inside the loop will
    overwrite a variable of the same name — but that is a naming mistake, not leaking.
14. It is the wildcard case: it matches anything that no earlier case matched.
15. Quadratic time — doing *n* × *n* work. Nested loops over large collections are the usual
    cause, and a set or dict can often turn it into a single pass.
</details>

---

## 🐛 Common mistakes

| Mistake | What you see | Fix |
|---|---|---|
| Forgetting the colon after `if` | `SyntaxError: invalid syntax` | Every `if`/`elif`/`else`/`for`/`while` header ends with `:` |
| Not indenting the body | `IndentationError: expected an indented block` | Indent the whole block 4 spaces; use an editor that shows guides |
| `range(stop)` including `stop` | `IndexError: list index out of range` | `stop` is exclusive — use `range(len(items))` |
| `zip()` silently truncating | Fewer pairs than expected, no error | Use `zip(a, b, strict=True)` and handle the `ValueError` |
| Infinite `while` loop | Program hangs, no output | Increment a counter, and add a `max_iterations` ceiling |
| Appending to a list while iterating over it | Loop visits items that did not exist when it started | Build a new list instead of mutating in place |
| Expecting `for ... else` to always run | `else` skipped when you used `break` | The `else` runs only when the loop ends **without** a `break` |
| `break` inside a nested loop | Only the inner loop stops | Use a flag, or restructure, or return from the function |
| Comparing with `==` when you meant `is` for `None` | Works by luck until a custom `__eq__` breaks it | Use `is None` / `is not None` |
| Unparenthesised `and`/`or` mix | Logic does not match your intent | Add parentheses — always |
| Reusing a variable name as a loop variable | Value silently overwritten after the loop | Give the loop variable a distinct name |
| Using `break` where `return` belongs | Function keeps running after you found the answer | `return` exits the whole function and is usually clearer |

---

## 🔗 Resources

- [Control Flow Tools — Python Tutorial](https://docs.python.org/3/tutorial/controlflow.html) —
  the official walkthrough of `if`, `for`, `while`, `break`, `continue` and the `else` clause.
- [Compound Statements — Python Language Reference](https://docs.python.org/3/reference/compound_stmts.html) —
  the precise rules for `if`, `for`, `while`, `try` and `match`.
- [The `for` Statement](https://docs.python.org/3/reference/compound_stmts.html#the-for-statement) —
  the specification of `for`, including how `else` and `break` interact.
- [The `match` Statement](https://docs.python.org/3/reference/compound_stmts.html#the-match-statement) —
  the full pattern-matching reference: literal, capture, sequence, mapping and class patterns.
- [What's New in Python 3.10](https://docs.python.org/3/whatsnew/3.10.html) — the release notes
  that introduced structural pattern matching.
- [range() — Built-in Functions](https://docs.python.org/3/library/functions.html#range) —
  the exact behaviour of `range`, including why it is lazy and why it rejects floats.
- [zip() — Built-in Functions](https://docs.python.org/3/library/functions.html#zip) —
  `zip` and its `strict=` argument.
- [enumerate() — Built-in Functions](https://docs.python.org/3/library/functions.html#enumerate) —
  `enumerate` and its `start=` argument.
- [Looping Techniques — Python HOWTO](https://docs.python.org/3/howto/functional.html#looping-techniques) —
  idiomatic ways to write loops, including the "sort by key" and "group into batches" patterns.
- [Truth Value Testing](https://docs.python.org/3/library/stdtypes.html#truth-value-testing) —
  the official rules for which values count as true.

---

## ➡️ Next

- [05 — Functions](05-functions.md) — you now have the vocabulary to make decisions. Next
  you learn to package blocks of logic into named, reusable, testable units — including the
  mutable-default-argument bug that has broken more Python code than any other.

**← Previous:** [03 — Data types and operators](03-data-types-and-operators.md)
