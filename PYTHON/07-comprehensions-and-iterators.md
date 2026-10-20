# Comprehensions and Iterators

Every time you write a loop that builds a list, you are doing the same three things: create an
empty container, loop over something, and append the interesting result. Python has a shorter
spelling for that pattern — a **comprehension** — and a lazier cousin of it called a
**generator**. This file teaches both, then shows you how Python's `for` loop really works under
the hood, so that streaming a million LLM tokens stops being magic.

> **⏱️ Time:** ~35 minutes
> **📚 Prereqs:** [06-data-structures.md](06-data-structures.md)
> **🎯 By the end you can:** write list, dict and set comprehensions fluently, build your own
> generators with `yield`, and explain what the iterator protocol is and why it powers streaming
> AI code.

---

## Why this matters for AI engineering

Two of the biggest problems in AI engineering are *memory* and *latency*. A 10 GB embedding
dataset will not fit in a list, and a chatbot that waits for the whole answer before printing a
single word feels broken.

Both problems are solved by the same mechanism: **lazy evaluation**, which is what generators
give you. The streaming mode of every major LLM SDK is built on generators — the SDK yields text
chunks as they arrive, and your `for` loop consumes them one at a time. The moment you understand
`yield`, you understand how to write a streaming chat UI, how to chunk a 500-page PDF without
loading it all into memory, and how `pandas` and `numpy` manage to process data larger than
memory.

---

## 1. The pattern you are about to replace

Here is the most common loop in all of programming: build a list from another sequence.

```python
# The long way
model_lengths = []
for model in ["gpt-5", "claude-opus-4", "gemini-3-pro"]:
    model_lengths.append(len(model))
print(model_lengths)

# The comprehension way
model_lengths = [len(model) for model in ["gpt-5", "claude-opus-4", "gemini-3-pro"]]
print(model_lengths)
```

```text
[5, 13, 12]
[5, 13, 12]
```

Same result, one line instead of three. The comprehension is not just shorter — it says *what you
want* ("the length of each model") rather than *how to get there* ("start empty, loop, append").

### 1.1 The exact syntax

A list comprehension has four optional parts, always in this order:

```text
[ expression   for  item   in  iterable   if  condition ]
     ^               ^          ^              ^
     |               |          |              +-- optional filter: keep only items
     |               |          |                  that satisfy this
     |               |          +-- where the items come from
     |               +-- the name you give each item (the loop variable)
     +-- what you want to produce for each item
```

Read it aloud in English, left to right: *"for each item in iterable, produce this expression, and
only if this condition holds."*

Two rules that trip people up:

- The `if` goes **after** the `for`, not before. `[x if x > 2 else 0 for x in data]`.
- You get one variable per `for` clause. `for x in a` gives you `x`.

---

## 2. List comprehensions in detail

### 2.1 Filtering with `if`

```python
scores = [88, 45, 72, 91, 30]

passing = [score for score in scores if score >= 70]
print(passing)

# The condition is applied BEFORE the expression, so the expression only
# ever sees the items that survived.
doubled_passing = [score * 2 for score in scores if score >= 70]
print(doubled_passing)
```

```text
[88, 72, 91]
[176, 144, 182]
```

### 2.2 Transforming with a conditional expression

Sometimes you want *both* branches in one expression. That is a **conditional expression**, which
looks like `value_if_true if condition else value_if_false`.

```python
scores = [88, 45, 72, 91, 30]

grades = ["pass" if score >= 70 else "fail" for score in scores]
print(grades)

# A conditional expression can also sit inside a filter.
salutes = [score for score in scores if (score >= 70 if score > 50 else False)]
print(salutes)
```

```text
['pass', 'fail', 'pass', 'pass', 'fail']
[88, 72, 91]
```

Read the conditional expression as a question: *"is this condition true? If yes use the value
before the `if`, if no use the value after the `else`."* It is the one-line version of a
`if`/`else` statement.

### 2.3 Nested `for` clauses

You can chain more than one `for` inside a single comprehension. Read them left to right, like
nested loops.

```python
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

flat = [value for row in matrix for value in row]
print(flat)

# The order of the for clauses matters: the first one is the outer loop.
pairs = [(row, value) for row in matrix for value in row if value % 2 == 0]
print(pairs)

# Filter on the OUTER loop with an if placed after the first for.
even_rows = [row for row in matrix if row[0] % 2 == 1]
print(even_rows)
```

```text
[1, 2, 3, 4, 5, 6, 7, 8, 9]
[([1, 2, 3], 2), ([4, 5, 6], 4), ([4, 5, 6], 6), ([7, 8, 9], 8)]
[[1, 2, 3], [7, 8, 9]]
```

Note the rule for `if` placement: an `if` always applies to the `for` clause immediately before
it. So in `[value for row in matrix for value in row if value % 2 == 0]`, the filter applies to
the **inner** loop. To filter on the outer loop, you must put the `if` right after the first
`for`, as in the third example.

---

## 3. Dict comprehensions

A **dict comprehension** builds a dict. The syntax is `{key: value for item in iterable}` — the
colon replaces the brackets.

```python
tokens = ["hello", "world", "hello"]
token_ids = {token: index for index, token in enumerate(dict.fromkeys(tokens))}
print(token_ids)

# A word -> length map.
words = ["the", "quick", "brown", "fox"]
lengths = {word: len(word) for word in words}
print(lengths)

# A word -> count map, built in one expression.
text = "the quick brown fox jumps over the lazy dog the fox"
split_words = text.split()
counts = {word: split_words.count(word) for word in dict.fromkeys(split_words)}
print(counts)
```

```text
{'hello': 0, 'world': 1}
{'the': 3, 'quick': 5, 'brown': 5, 'fox': 3}
{'the': 3, 'quick': 1, 'brown': 1, 'fox': 2, 'jumps': 1, 'over': 1, 'lazy': 1, 'dog': 1}
```

`dict.fromkeys(tokens)` is a small trick worth learning: it builds a dict from a sequence, using
each item as a key, and **keeps the first occurrence of each one, in order**. It is the standard
way to de-duplicate a list while preserving order — and unlike `set`, the result is predictable.
(For counting, `collections.Counter` does the same job far more efficiently; you met it in
[06-data-structures.md](06-data-structures.md).)

That last example works but is inefficient: `list.count` scans the whole list once per word. The
idiomatic way to count is a small loop with `.get()`:

```python
text = "the quick brown fox jumps over the lazy dog the fox"
split_words = text.split()

counts = {}
for word in split_words:
    counts[word] = counts.get(word, 0) + 1
print(counts)
```

```text
{'the': 3, 'quick': 1, 'brown': 1, 'fox': 2, 'jumps': 1, 'over': 1, 'lazy': 1, 'dog': 1}
```

Same answer, linear time. When you already have a count, reach for `collections.Counter` (you met
it in [06-data-structures.md](06-data-structures.md)) — it does exactly this in one line.

---

## 4. Set comprehensions

Swap the braces for braces and drop the colon: `{expression for item in iterable}`.

```python
words = ["apple", "banana", "cherry", "apple", "date"]

lengths = {len(word) for word in words}
print(sorted(lengths))

vowels = {char for char in "the quick brown fox" if char in "aeiou"}
print(sorted(vowels))
```

```text
[4, 5, 6]
['e', 'i', 'o', 'u']
```

A set comprehension is the natural way to express "give me the *distinct* values of this
computation". Note that `"the quick brown fox"` contains no `a`, so `a` is not in the vowel set.

---

## 5. Generator expressions — the lazy cousin

Put the same expression in **round brackets** instead of square ones and you get a **generator
expression**. It looks almost identical but behaves completely differently: a list comprehension
computes every item immediately and stores them all; a generator expression computes each item
only when it is asked for.

```python
import sys

# A list comprehension builds all one million values right now.
squares = [n * n for n in range(1_000_000)]

# A generator expression computes them one at a time, on demand.
lazy_squares = (n * n for n in range(1_000_000))

print(type(squares))
print(type(lazy_squares))
print(f"list of 1,000,000 ints: {sys.getsizeof(squares):,} bytes")
print(f"generator object:        {sys.getsizeof(lazy_squares):,} bytes")
```

```text
<class 'list'>
<class 'generator'>
list of 1,000,000 ints: 8,448,728 bytes
generator object:        200 bytes
```

Eight megabytes versus two hundred bytes. That is the whole point of generators, in one number.

One important difference in *syntax*: a generator expression with more than one clause must be
written inside a single set of parentheses. A bare `n * n for n in range(10)` is a syntax error.

```python
# WRONG - SyntaxError
# squares = n * n for n in range(10)

# RIGHT - wrap it in extra parentheses
squares = (n * n for n in range(10))
print(sum(squares))
```

```text
285
```

---

## 6. `map`, `filter` and `lambda`

Before comprehensions there were three built-in functions that do similar jobs. You will meet
them in older code and in the standard library, so you need to recognise them.

- `map(function, iterable)` — apply a function to every item.
- `filter(function, iterable)` — keep only the items for which the function returns truthy.
- `lambda` — an anonymous function, written on one line with no `def`.

```python
models = ["gpt-5", "claude-opus-4", "gemini-3-pro"]

# map with a built-in function
print(list(map(len, models)))

# map with a lambda
print(list(map(lambda model: model.upper(), models)))

# filter with a lambda
print(list(filter(lambda model: len(model) > 10, models)))

# The comprehension versions, which read better:
print([len(model) for model in models])
print([model.upper() for model in models])
print([model for model in models if len(model) > 10])
```

```text
[5, 13, 12]
['GPT-5', 'CLAUDE-OPUS-4', 'GEMINI-3-PRO']
['claude-opus-4', 'gemini-3-pro']
[5, 13, 12]
['GPT-5', 'CLAUDE-OPUS-4', 'GEMINI-3-PRO']
['claude-opus-4', 'gemini-3-pro']
```

**When should you use which?** Almost always the comprehension. `map` and `filter` force you to
think in two steps (build the function, then apply it), while a comprehension reads as one
sentence. Use `map`/`filter` when you already have the function and want to reuse it, or when the
function is a complicated one you have defined elsewhere.

One more thing: `map()` and `filter()` return **lazy** objects in Python 3. They do not build a
list until you wrap them in `list(...)` or loop over them.

---

## 7. Generators and `yield` — the heart of this file

A **generator** is a function that can pause mid-execution and hand back a value, then resume
exactly where it left off later. You create one by putting a `yield` statement inside a function.

The word `yield` means "produce this value, then wait here until someone asks for the next one".

### 7.1 A generator in full

```python
def countdown(start):
    """Yield each number from start down to 1, one at a time."""
    while start > 0:
        yield start
        start -= 1


counter = countdown(3)
print("type of the object:", type(counter))

print("first: ", next(counter))
print("second:", next(counter))
print("third: ", next(counter))

try:
    next(counter)
except StopIteration:
    print("StopIteration: there are no more values")
```

```text
type of the object: <class 'generator'>
first:  3
second: 2
third:  1
StopIteration: there are no more values
```

Three things to notice:

1. Calling `countdown(3)` did **not** run the function body. It created a generator object.
2. Each call to `next()` ran the body a little further, and only a little.
3. When the function ran out of values, `next()` raised `StopIteration`.

### 7.2 Exactly what happens, step by step

The single most important thing in this file is understanding *when* each line runs. Here is the
same generator with print statements that show it.

```python
def traced_countdown(start):
    print("   [gen] generator function called - body has NOT started yet")
    value = start
    while value > 0:
        print(f"   [gen] running body, about to yield {value}")
        yield value
        print(f"   [gen] resumed after yielding {value}")
        value -= 1
    print("   [gen] function body finished")


print("STEP 1: create the generator object")
gen = traced_countdown(3)

print("STEP 2: call next() the first time")
print("   got:", next(gen))

print("STEP 3: call next() the second time")
print("   got:", next(gen))

print("STEP 4: call next() the third time")
print("   got:", next(gen))

print("STEP 5: call next() a fourth time")
try:
    next(gen)
except StopIteration:
    print("   StopIteration raised")
```

```text
STEP 1: create the generator object
STEP 2: call next() the first time
   [gen] generator function called - body has NOT started yet
   [gen] running body, about to yield 3
   got: 3
STEP 3: call next() the second time
   [gen] resumed after yielding 3
   [gen] running body, about to yield 2
   got: 2
STEP 4: call next() the third time
   [gen] resumed after yielding 2
   [gen] running body, about to yield 1
   got: 1
STEP 5: call next() a fourth time
   [gen] resumed after yielding 1
   [gen] function body finished
   StopIteration raised
```

Read that output slowly. It tells the whole story:

- Creating the generator runs **none** of the body.
- The first `next()` runs the body from the top until it hits `yield`, then freezes.
- Each later `next()` resumes **immediately after the `yield`** and runs until the next `yield`.
- When the body ends, `next()` raises `StopIteration`.

That is the entire model. A generator is a function with a pause button.

### 7.3 `return` versus `yield`

```python
def normal_function():
    return 42            # hands back a value and ends


def generator_function():
    yield 42             # hands back a value and WAITS
    yield 43             # there is more to come


print(normal_function())

generator = generator_function()
print(type(generator))
print(list(generator))    # forces it to produce everything
```

```text
42
<class 'generator'>
[42, 43]
```

Notice the difference in shape: calling `normal_function()` gives you the value `42` right away.
Calling `generator_function()` gives you a **generator object** — a little machine that will
produce `42` and `43` later, one at a time, when asked.

---

## 8. `iter`, `next` and `StopIteration`

`iter()` takes a sequence and returns an **iterator** — an object that remembers where it is in
the sequence. `next()` pulls the next value out of an iterator.

```python
numbers = [10, 20, 30]

it = iter(numbers)
print(type(it))
print(next(it))
print(next(it))
print(next(it))

try:
    next(it)
except StopIteration:
    print("StopIteration: the iterator is exhausted")
```

```text
<class 'list_iterator'>
10
20
30
StopIteration: the iterator is exhausted
```

**`StopIteration` is not an error you need to handle.** It is the normal end-of-data signal. A
`for` loop catches it for you.

### 8.1 A `for` loop is this, in disguise

```python
numbers = [10, 20, 30]

# What you write:
for number in numbers:
    print("body got:", number)

# What actually happens:
it = iter(numbers)
while True:
    try:
        number = next(it)
    except StopIteration:
        break
    print("body got:", number)
```

```text
body got: 10
body got: 20
body got: 30
body got: 10
body got: 20
body got: 30
```

Same output. This is worth internalising, because it means **any** object that supports
`iter()` and `next()` can be used in a `for` loop — not just lists. Generators, file objects,
database cursors, `pandas` Series and `numpy` arrays all work because they follow this protocol.

---

## 9. Writing your own iterator

You can make any class work in a `for` loop by implementing two special methods:

- `__iter__()` — returns the iterator object (usually `self`).
- `__next__()` — returns the next value, or raises `StopIteration` when there are none.

Here is a working `Countdown` you can loop over:

```python
class Countdown:
    """Counts down from `start` to 1, one number at a time."""

    def __init__(self, start):
        self.current = start

    def __iter__(self):
        return self  # an iterator must return itself

    def __next__(self):
        if self.current <= 0:
            raise StopIteration      # tell the for loop we are finished
        self.current -= 1
        return self.current + 1


for number in Countdown(5):
    print(number)

print("---")

# It also works with next() directly, because it follows the protocol.
counter = Countdown(3)
print(next(counter))
print(next(counter))
print(next(counter))
```

```text
5
4
3
2
1
---
3
2
1
```

Note the pattern in `__next__`: check whether you are done **first**, raise `StopIteration` if
you are, otherwise produce the value. Forgetting the `StopIteration` gives you an infinite loop.

---

## 10. The iterator protocol, in plain English

An **iterator** is any object that knows how to produce its next value, and how to say "I am
finished". Python calls those two abilities `__iter__` and `__next__`. Every `for` loop in
Python, and every `next()` call, works by asking an object for its iterator and then repeatedly
asking that iterator for one more value until it says it is done. This shared contract is called
the **iterator protocol**.

Why should you care? Because the protocol is what makes **lazy** work. A generator does not
compute anything until the `for` loop asks for the next value, so you can write a loop over ten
billion items as long as you only consume a few of them. That single idea is what makes streaming
possible: LLM token streams, `pandas` chunked readers, `numpy` array operations over files larger
than RAM, and log processing all work the same way.

---

## 11. `key=` functions: `sorted`, `max`, `min`

You already met `sorted(..., key=...)` in the previous file. `max` and `min` accept the same
argument. The `key` argument takes a **function** that is applied to each item before comparing.

```python
models = [
    {"name": "gpt-5", "cost_per_1k": 0.02, "context": 400_000},
    {"name": "claude-opus-4", "cost_per_1k": 0.09, "context": 200_000},
    {"name": "gemini-3-pro", "cost_per_1k": 0.04, "context": 1_000_000},
]

cheapest = min(models, key=lambda model: model["cost_per_1k"])
biggest = max(models, key=lambda model: model["context"])
print("cheapest:", cheapest["name"])
print("biggest context:", biggest["name"])

ordered = sorted(models, key=lambda model: model["cost_per_1k"], reverse=True)
for model in ordered:
    print(f"{model['name']:16} {model['cost_per_1k']}")
```

```text
cheapest: gpt-5
biggest context: gemini-3-pro
claude-opus-4    0.09
gemini-3-pro     0.04
gpt-5            0.02
```

`max` and `min` return the **whole item**, not just the key — which is why you follow up with
`["name"]`.

### 11.1 `sum` does not have a `key` argument

`sum` works differently from `sorted`, `max` and `min`. It adds the items themselves, so you
need to convert them first:

```python
scores = ["88", "45", "72", "91"]

# sum() has no key= argument:
total = sum(map(int, scores))
print("total:", total)

# sum() does have a start argument, for adding a base value:
print("with a base:", sum([1, 2, 3], start=100))

# Binary floating point is not exact:
print("0.1 + 0.2 =", 0.1 + 0.2)
print("round it:  ", round(0.1 + 0.2, 10))
```

```text
total: 296
with a base: 106
0.1 + 0.2 = 0.30000000000000004
round it:   0.3
```

Two useful facts fall out of that. `sum` accepts a `start` value, which is how you add a base
number to a total. And floating-point addition is not exact — `0.1 + 0.2` is not `0.3` — because
binary cannot represent those fractions perfectly. This is normal in binary floating point, not a
Python bug, and it is why you should use `round()` (or the `decimal` module) when exact money
matters.

---

## 12. `any` and `all`

Two more built-ins that take a sequence of booleans:

- `any(...)` is `True` if **at least one** item is truthy.
- `all(...)` is `True` if **every** item is truthy.

```python
responses = [
    {"status": 200, "body": "ok"},
    {"status": 200, "body": "ok"},
    {"status": 500, "body": "server error"},
]

all_ok = all(response["status"] == 200 for response in responses)
any_failed = any(response["status"] >= 400 for response in responses)
print("all succeeded:", all_ok)
print("any failed:   ", any_failed)

# The "any" idiom: did the batch contain at least one empty result?
results = ["doc one", "", "doc three"]
print("has an empty result:", any(result == "" for result in results))

# "all" on an empty list is True, "any" on an empty list is False.
print("all of empty:", all([]))
print("any of empty:", any([]))
```

```text
all succeeded: False
any failed:    True
has an empty result: True
all of empty: True
any of empty: False
```

The `all([])` being `True` surprises people. Think of it as "there was no counter-example", which
is vacuously true. In practice, guard against empty batches before relying on `all`.

---

## 13. `functools.reduce` and a taste of `itertools`

### 13.1 `reduce`

`reduce` folds a function over a sequence, accumulating a running value.

```python
from functools import reduce

numbers = [1, 2, 3, 4, 5]

total = reduce(lambda accumulator, number: accumulator + number, numbers)
print("sum:", total)

product = reduce(lambda accumulator, number: accumulator * number, numbers)
print("product:", product)

# The third argument is the starting value of the accumulator (positional only):
shifted = reduce(lambda accumulator, number: accumulator + number, numbers, 100)
print("with a start:", shifted)
```

```text
sum: 15
product: 120
with a start: 115
```

Read `reduce` as: *"take the first item as the accumulator, then for each next item combine it with
the accumulator using my function."* In modern Python, `sum`, `min` and `max` cover most uses, and
`reduce` shows up mainly in older code and in the standard library. You will meet it properly in
[14-standard-library.md](14-standard-library.md).

### 13.2 `itertools` — a teaser

The `itertools` module is a toolbox of iterator functions. You will not need all of it, but five
of these turn up constantly:

```python
from itertools import chain, islice, groupby, product, zip_longest

# chain: glue several iterables end to end
print("chain:  ", list(chain([1, 2], [3, 4], [5])))

# islice: take a slice of an iterable without making a list first
print("islice: ", list(islice(range(100), 10, 15)))

# product: every combination of two iterables
print("product:", list(product([1, 2], ["a", "b"])))

# zip_longest: zip that does not stop at the shortest
print("zipped: ", list(zip_longest([1, 2, 3], ["a", "b"], fillvalue="?")))

# groupby: group consecutive items that share a key (input must be sorted)
words = ["ant", "ape", "bat", "bee", "cat"]
for first_letter, group in groupby(sorted(words), key=lambda word: word[0]):
    print("groupby:", first_letter, list(group))
```

```text
chain:   [1, 2, 3, 4, 5]
islice:  [10, 11, 12, 13, 14]
product: [(1, 'a'), (1, 'b'), (2, 'a'), (2, 'b')]
zipped:  [(1, 'a'), (2, 'b'), (3, '?')]
groupby: a ['ant', 'ape']
groupby: b ['bat', 'bee']
groupby: c ['cat']
```

`groupby` groups *consecutive* items that share a key, which is why the input must be sorted
first — otherwise items with the same key can end up in separate groups.

Full details of `itertools` and `collections` are in
[14-standard-library.md](14-standard-library.md).

---

## 14. Lazy versus eager, and infinite generators

Because a generator only computes what you ask for, it can produce an **infinite** stream without
running out of memory.

```python
from itertools import islice


def naturals():
    """An infinite generator: 0, 1, 2, 3, ... forever."""
    number = 0
    while True:
        yield number
        number += 1


stream = naturals()
print(next(stream))
print(next(stream))
print(next(stream))

# Taking just the first ten is safe, because only ten are ever produced.
first_ten = list(islice(naturals(), 10))
print(first_ten)

# But turning an infinite generator into a list will hang forever:
# list(naturals())     # DO NOT RUN THIS
```

```text
0
1
2
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
```

The warning at the bottom is real: `list(naturals())` never finishes. This is why you should
never wrap a large or infinite generator in `list()` unless you are certain it terminates.

The practical rule for choosing:

| You want | Use |
|---|---|
| a real, finite list you will index and reuse | list comprehension |
| items one at a time, and you might stop early | generator expression |
| a stream that never ends | generator function with `yield` |
| the smallest possible memory footprint | generator expression over a generator function |

---

## 15. This in real AI work

Here are three concrete places where everything above shows up.

### 15.1 Streaming LLM tokens

Every streaming chat API is a generator under the hood. This is what a streaming loop looks like,
written against a fake client so you can run it:

```python
def fake_llm_stream(prompt):
    """Pretend to be an LLM API that streams tokens back one at a time."""
    for token in ["The ", "answer ", "is ", "42."]:
        yield token


print("Assistant: ", end="")
for token in fake_llm_stream("What is the answer?"):
    print(token, end="", flush=True)
print()
```

```text
Assistant: The answer is 42.
```

With a real SDK it looks almost identical — `client.chat.completions.create(..., stream=True)`
returns an iterator, and you loop over it. The `yield` model you just learned is the same model.

### 15.2 Chunking a big document

A 500-page PDF should never be loaded whole. A generator that yields overlapping chunks lets you
embed and store each chunk as you go.

```python
def chunk_text(text, chunk_size=100, overlap=20):
    """Yield overlapping chunks of text instead of returning a list."""
    step = chunk_size - overlap
    for start in range(0, len(text), step):
        chunk = text[start:start + chunk_size]
        if chunk.strip():
            yield chunk


document = "Retrieval augmented generation grounds a language model in your own documents. " * 4

chunks = list(chunk_text(document, chunk_size=80, overlap=20))
print(f"document is {len(document)} characters -> {len(chunks)} chunks")
for number, chunk in enumerate(chunks, start=1):
    preview = chunk[:40].replace("\n", " ")
    print(f"{number}: {preview}...")
```

```text
document is 316 characters -> 6 chunks
1: Retrieval augmented generation grounds a...
2: our own documents. Retrieval augmented g...
3: language model in your own documents. Re...
4: neration grounds a language model in you...
5: rieval augmented generation grounds a la...
6:  own documents. ...
```

Notice that consecutive chunks overlap — chunk 2 starts before chunk 1 ends, so a sentence that
straddles a boundary is not lost. `chunk_size` is 80 and `overlap` is 20, so each chunk advances
by 60 characters.

Notice that a generator function (with `yield`) is what makes `chunk_text` lazy in the first
place. In production you would drop the `list(...)` and loop over `chunk_text(...)` directly, so
the document is never held in memory all at once.

### 15.3 Processing a large dataset lazily

Any dataset you can stream, you can process without filling your RAM:

```python
records = [
    {"id": 1, "tokens": 120},
    {"id": 2, "tokens": 340},
    {"id": 3, "tokens": 90},
    {"id": 4, "tokens": 510},
]

# Lazy: only cheap records survive, and nothing is built until you ask.
cheap_ids = (record["id"] for record in records if record["tokens"] < 400)
print("lazy object:", type(cheap_ids))
print("ids:", list(cheap_ids))

# The same thing with a comprehension, when you want a real list:
cheap_ids = [record["id"] for record in records if record["tokens"] < 400]
print("ids:", cheap_ids)
```

```text
lazy object: <class 'generator'>
ids: [1, 2, 3]
ids: [1, 2, 3]
```

For a file with a million rows, the difference between "one row in memory" and "a million rows in
memory" is the difference between a program that runs and a program that dies.

---

## 🧪 Try it yourself

### Exercise 1 — Rewrite the loop

Turn this loop into a comprehension:

```python
models = ["gpt-5", "claude-opus-4", "gemini-3-pro"]
long_names = []
for model in models:
    if len(model) > 10:
        long_names.append(model)
print(long_names)
```

<details>
<summary>Hint</summary>

The filter goes after the `for` clause, and the expression before it.
</details>

<details>
<summary>Solution</summary>

```python
models = ["gpt-5", "claude-opus-4", "gemini-3-pro"]
long_names = [model for model in models if len(model) > 10]
print(long_names)
```

```text
['claude-opus-4', 'gemini-3-pro']
```
</details>

### Exercise 2 — Build a token-to-id map

Write a dict comprehension that maps each unique token in the list to its position in the list of
unique tokens. Then print the map.

<details>
<summary>Hint</summary>

`enumerate(dict.fromkeys(tokens))` gives you `(index, token)` pairs — exactly what you need to
destructure. `dict.fromkeys` removes duplicates but keeps the original order.
</details>

<details>
<summary>Solution</summary>

```python
tokens = ["hello", "world", "hello", "there"]

token_to_id = {token: index for index, token in enumerate(dict.fromkeys(tokens))}
print(token_to_id)
```

```text
{'hello': 0, 'world': 1, 'there': 2}
```

If you use `set(tokens)` instead of `dict.fromkeys(tokens)` you get the same pairs, but the *order*
is not guaranteed — it can differ between runs. `dict.fromkeys` keeps the first-seen order, which
is what you want for stable token ids.
</details>

### Exercise 3 — Write a generator

Write a generator function `even_numbers(limit)` that yields the even numbers from 0 up to (but
not including) `limit`. Use `next()` to pull out the first three values.

<details>
<summary>Hint</summary>

A generator function uses `yield` instead of `return`. Return one value at a time.
</details>

<details>
<summary>Solution</summary>

```python
def even_numbers(limit):
    number = 0
    while number < limit:
        yield number
        number += 2


gen = even_numbers(10)
print(next(gen))
print(next(gen))
print(next(gen))
print("all of them:", list(even_numbers(10)))
```

```text
0
2
4
all of them: [0, 2, 4, 6, 8]
```
</details>

### Exercise 4 — Trace the generator

What does this print, and in what order?

```python
def counter():
    print("starting")
    yield 1
    print("middle")
    yield 2
    print("ending")


gen = counter()
print("created")
print(next(gen))
print(next(gen))
```

<details>
<summary>Hint</summary>

The body does not run until the first `next()`. Then it runs up to the first `yield`.
</details>

<details>
<summary>Solution</summary>

```text
created
starting
1
middle
2
```

`counter()` only creates the generator object — nothing is printed yet. The first `next()` runs
the body up to `yield 1` (printing "starting"), the second `next()` resumes after that yield and
prints "middle" before yielding 2. "ending" is never printed because a third `next()` is never
called.
</details>

### Exercise 5 — Write your own iterator

Write a class `Even` that iterates over the even numbers up to a limit, so that this loop prints
`0`, `2`, `4`:

```text
for number in Even(6):
    print(number)
```

<details>
<summary>Hint</summary>

You need `__iter__` (return `self`) and `__next__` (return the next value, or raise
`StopIteration`).
</details>

<details>
<summary>Solution</summary>

```python
class Even:
    """Iterates over even numbers from 0 up to limit."""

    def __init__(self, limit):
        self.limit = limit
        self.current = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.current >= self.limit:
            raise StopIteration
        value = self.current
        self.current += 2
        return value


for number in Even(6):
    print(number)
```

```text
0
2
4
```
</details>

### Exercise 6 — Use `key=` to find the outlier

Given a list of API responses with `"latency_ms"` values, find the slowest one and print its
`"endpoint"`. Use `max` with a `key` function.

<details>
<summary>Hint</summary>

`max(items, key=lambda item: item["latency_ms"])` returns the whole item.
</details>

<details>
<summary>Solution</summary>

```python
responses = [
    {"endpoint": "/search", "latency_ms": 210},
    {"endpoint": "/summarise", "latency_ms": 1840},
    {"endpoint": "/chat", "latency_ms": 640},
]

slowest = max(responses, key=lambda response: response["latency_ms"])
print("slowest:", slowest["endpoint"], slowest["latency_ms"], "ms")
```

```text
slowest: /summarise 1840 ms
```
</details>

---

## ✅ Checkpoint

**1. What is the exact order of the parts in a list comprehension?**

<details>
<summary>Answer</summary>

`[expression for item in iterable if condition]` — expression first, then `for item in iterable`,
then an optional `if` filter at the end.
</details>

**2. Why does `[x if x > 2 else 0 for x in data]` work but `[if x > 2 else 0 for x in data]` not?**

<details>
<summary>Answer</summary>

The `if` inside a comprehension is a *filter* and comes after the `for` clause. The
`value_if_true if condition else value_if_false` form is a conditional *expression* and belongs
where the expression goes — at the very front.
</details>

**3. What is the difference between a list comprehension and a generator expression?**

<details>
<summary>Answer</summary>

Square brackets versus round brackets. A list comprehension computes and stores every item
immediately; a generator expression computes each item only when it is requested, using far less
memory.
</details>

**4. What does `yield` actually do?**

<details>
<summary>Answer</summary>

It pauses the function, hands the value back to the caller, and remembers exactly where it
stopped. The next `next()` call resumes right after the `yield`.
</details>

**5. What happens when you call `next()` on an exhausted generator?**

<details>
<summary>Answer</summary>

It raises `StopIteration`. That is the normal end-of-data signal, and `for` loops catch it
automatically.
</details>

**6. What two methods must a class implement to work in a `for` loop?**

<details>
<summary>Answer</summary>

`__iter__` (which returns the iterator, usually `self`) and `__next__` (which returns the next
value or raises `StopIteration`).
</details>

**7. Does `sum()` accept a `key=` argument?**

<details>
<summary>Answer</summary>

No. `sum` adds the items themselves, so convert them first with `sum(map(int, values))`.
`sorted`, `max` and `min` all accept `key=`.
</details>

**8. Why is `list(my_generator)` a bad idea for an infinite generator?**

<details>
<summary>Answer</summary>

`list()` insists on consuming every value before it returns anything, so it would run forever.
</details>

---

## 🐛 Common mistakes

| Mistake | What you see | Fix |
|---|---|---|
| `if` before the `for` in a comprehension | `SyntaxError: invalid syntax` | The filter goes last: `[x for x in data if x > 2]` |
| Using `if` as the expression | `SyntaxError: invalid syntax` | Use a conditional expression: `[x if x > 2 else 0 for x in data]` |
| Generator expression with 2+ clauses and no extra brackets | `SyntaxError: Generator expression must be parenthesized` | Wrap the whole thing: `(x for x in a if x for y in b)` |
| `next(gen)` on an exhausted generator | `StopIteration` | Catch it, or just use a `for` loop, which handles it for you |
| Forgetting `raise StopIteration` in `__next__` | The `for` loop never ends | Check for the end condition *before* returning a value |
| `__iter__` returning something else | `TypeError: iter() returned non-iterator` | `__iter__` must return the iterator, normally `self` |
| Converting a huge generator with `list()` | Memory blow-up, or a hang | Consume it with a `for` loop and stop when you have enough |
| Using `map`/`filter` where a comprehension reads better | Harder to read, two steps | Prefer `[f(x) for x in data]` unless you are reusing `f` |
| Expecting `sum(values, key=int)` to work | `TypeError: sum() got an unexpected keyword argument 'key'` | Use `sum(map(int, values))` |
| Mutating a list inside a comprehension's source | Confusing results | Build a new list; never edit while iterating |

---

## 🔗 Resources

- [List comprehensions — Python Tutorial](https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions)
  — the official explanation, plus the `for`/`if` ordering rules.
- [Generator expressions](https://docs.python.org/3/reference/expressions.html#generator-expressions)
  — the formal syntax, and how it differs from a list comprehension.
- [Yield expressions](https://docs.python.org/3/reference/expressions.html#yield-expressions) —
  the language reference for `yield`, including what happens to the function's local state.
- [PEP 380 — Adding `yield from` to Python](https://peps.python.org/pep-0380/) — why the language
  grew a dedicated way to delegate to sub-generators.
- [PEP 234 — Generator expressions](https://peps.python.org/pep-0234/) — the original design
  rationale for lazy expressions.
- [Glossary: iterator, generator, iterable](https://docs.python.org/3/glossary.html) — the precise
  definitions Python uses, in one page.
- [Iterator types](https://docs.python.org/3/library/stdtypes.html#iterator-types) — the
  reference for `__iter__`, `__next__` and `StopIteration`.
- [`map`, `filter`, `sorted`, `min`, `max`](https://docs.python.org/3/library/functions.html) — the
  full signatures for every function that takes a `key=`.
- [`itertools`](https://docs.python.org/3/library/itertools.html) — the full catalogue of
  iterator tools; `chain`, `islice`, `groupby`, `product` and `zip_longest` are all here.
- [`functools`](https://docs.python.org/3/library/functools.html) — `reduce`, `partial`, `lru_cache`
  and the other higher-order function helpers.
- [How to use the `iter` protocol](https://docs.python.org/3/howto/functional.html) — the
  official "Functional Programming HOWTO", which goes deeper on laziness.
- [Real Python: Python Generators](https://realpython.com/python-generators/) — a long-form
  community walkthrough with more examples.

---

## ➡️ Next

- [08 Modules and packages](08-modules-and-packages.md) — split your code across files, import
  things, and install packages with `pip`.

**← Previous:** [06 Data structures](06-data-structures.md)
