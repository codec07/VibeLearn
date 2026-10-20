# Data Structures

One variable holds one value. Real programs hold thousands of values: chat messages, tool results,
model names, prices, embeddings. Python gives you four containers for holding them, and each one has
different rules about order, duplicates and changeability. This file teaches you all four, and —
just as importantly — how to pick the right one in the first place.

> **⏱️ Time:** ~45 minutes
> **📚 Prereqs:** [05-functions.md](05-functions.md)
> **🎯 By the end you can:** choose between list, tuple, dict and set for any job, and manipulate all
> four of them without falling into the aliasing, sorting or single-element-tuple traps.

---

## Why this matters for AI engineering

AI code is mostly moving data around. A chat history is a list. A tool registry is a dictionary. A
set of model names you have already seen is a set. A configuration you must not accidentally change
is a tuple. When you pick the wrong container you get bugs that appear far away from the cause: a
tool registry that mutates under you, a duplicate message that gets billed twice, a config that
silently changes because two functions share one list.

The same reasoning applies to `pandas` columns, `numpy` arrays and the streaming token APIs that
OpenAI and Anthropic SDKs expose. Containers are not an academic topic here — they are the
vocabulary the rest of the course is written in.

---

## 1. Why one kind of container is not enough

Imagine you store a shopping list. Three different things are true about it at once:

- It has an order — bread, milk, eggs is not the same list as eggs, milk, bread.
- It changes — you add cheese, you drop the milk.
- It might contain the same item twice — two tins of beans.

Now imagine you store a date: `2026, 10, 20`. It has an order, but it must never change, and it
would be strange to have two Octobers.

Now imagine you store a user's settings:

```text
"theme"      -> "dark"
"model"      -> "gpt-5"
"temperature"-> 0.2
```

Here there is no meaningful order at all. What you have is a *mapping* from one thing (the key) to
another (the value).

Python gives you four containers, one for each of those shapes.

| Container | Ordered? | Changeable? | Duplicates allowed? | Use it for |
|---|---|---|---|---|
| **list** `[]` | yes | yes | yes | an ordered sequence of things |
| **tuple** `()` | yes | no | yes | a fixed, ordered sequence |
| **dict** `{}` | yes (since 3.7) | yes | keys: no, values: yes | key → value lookups |
| **set** `{}` | not meaningfully | yes | no | unique items, fast membership |

Read the table twice. The single most useful question when choosing is: **do I need to look things up
by name, or by position?**

- By position → **list** (or **tuple** if it is fixed).
- By name → **dict**.
- Do I only need "have I seen this before?" → **set**.

Here is the same idea as a runnable program, so you can see the four types side by side:

```python
# Four containers, four different jobs.
chat_messages = [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi there"},
]

model_config = ("gpt-5", 0.2, 1024)

tool_registry = {
    "search": "https://api.example.com/search",
    "calculator": "https://api.example.com/calc",
}

seen_models = {"gpt-5", "claude-opus-4", "gpt-5"}  # the duplicate collapses

print(type(chat_messages), len(chat_messages))
print(type(model_config), len(model_config))
print(type(tool_registry), len(tool_registry))
print(type(seen_models), len(seen_models))
print(sorted(seen_models))  # sets have no order, so sort before printing
```

```text
<class 'list'> 2
<class 'tuple'> 3
<class 'dict'> 2
<class 'set'> 2
['claude-opus-4', 'gpt-5']
```

Notice the last line: `seen_models` was created with three items but has length 2, because a set
refuses duplicates. That single behaviour is often the whole reason to reach for a set.

---

## 2. Lists — the workhorse

A **list** is an ordered, changeable sequence of items. Square brackets create one.

```python
fruits = ["apple", "banana", "cherry"]

print(fruits)
print(len(fruits))     # how many items
print(fruits[0])       # first item
print(fruits[2])       # third item
print(fruits[-1])      # last item
print(fruits[-2])      # second-to-last item
```

```text
['apple', 'banana', 'cherry']
3
apple
cherry
cherry
banana
```

### 2.1 Indexing is zero-based

This is the single most common beginner off-by-one mistake, so it gets its own diagram.

```text
  index:     0       1       2       3
  value:  apple  banana  cherry   date
  from end: -4      -3      -2      -1
```

Python counts from **zero**, so the first item is at index `0`, not `1`. The last item is at index
`len(fruits) - 1`. Negative indexes count backwards from the end, where `-1` is always the last
item. There is no "last index" property — you compute it, or you use `-1`.

### 2.2 Slicing — taking a piece of a list

A **slice** is written `sequence[start:stop:step]`. `start` is where you start, `stop` is where you
stop *before*, and `step` is how far to jump each time.

```text
letters = "abcdefgh"

  index:    0    1    2    3    4    5    6    7
  value:    a    b    c    d    e    f    g    h

  letters[2:5]  -> start at index 2 ('c'), stop before index 5 -> 'cde'
  letters[:3]   -> start at the beginning, stop before index 3  -> 'abc'
  letters[5:]   -> start at index 5, go to the end               -> 'fgh'
  letters[::2]  -> every second item                            -> 'aceg'
  letters[::-1] -> backwards                                     -> 'hgfedcba'
```

Here it is running:

```python
letters = list("abcdefgh")

print(letters[2:5])
print(letters[:3])
print(letters[5:])
print(letters[::2])
print(letters[::-1])
print(letters[-3:])   # last three, using a negative start
```

```text
['c', 'd', 'e']
['a', 'b', 'c']
['f', 'g', 'h']
['a', 'c', 'e', 'g']
['h', 'g', 'f', 'e', 'd', 'c', 'b', 'a']
['f', 'g', 'h']
```

The `stop` value is **exclusive** — it is the index of the first item you do *not* want. The
shortest slice is `lst[:]`, which is a copy of the whole list.

### 2.3 Slices never raise IndexError

Indexing out of range raises `IndexError`. Slicing out of range does not — it just returns
whatever exists. This is deliberate: it makes it safe to slice near the end without checking first.

```python
letters = list("abcdefgh")

print(letters[2:100])   # no error, stops at the end
print(letters[-100:3])   # no error, starts at the beginning
print(letters[50:60])    # empty list, no error

try:
    print(letters[100])
except IndexError as error:
    print("IndexError:", error)
```

```text
['c', 'd', 'e', 'f', 'g', 'h']
['a', 'b', 'c']
[]
IndexError: list index out of range
```

Note the asymmetry: slicing is forgiving, indexing is strict. Reach for a slice when you are
grabbing a window of unknown length; reach for an index when you are certain.

### 2.4 The list methods you will actually use

A **method** is a function that belongs to a value. `fruits.append("date")` means "ask this list to
append a date to itself".

```python
tasks = ["train model", "evaluate model"]

tasks.append("deploy model")             # add one item at the end
tasks.insert(0, "collect data")          # insert at a position, pushing others right
tasks.extend(["write docs", "add tests"])  # add many items at the end
print(tasks)

tasks.remove("deploy model")             # delete by value (first match only)
popped = tasks.pop()                     # remove and return the last item
print("popped:", popped)
print(tasks)

print("collect data" in tasks)            # membership test
print(tasks.count("train model"))        # how many times this value appears
print(tasks.index("evaluate model"))     # position of the first match
print(min([3, 1, 2]), max([3, 1, 2]), sum([3, 1, 2]))

tasks.reverse()                          # reverse the list in place
print("reversed:", tasks)

tasks.clear()                            # empty the list completely
print("cleared:", tasks)
```

```text
['collect data', 'train model', 'evaluate model', 'deploy model', 'write docs', 'add tests']
popped: add tests
['collect data', 'train model', 'evaluate model', 'write docs']
True
1
2
1 3 6
reversed: ['write docs', 'evaluate model', 'train model', 'collect data']
cleared: []
```

Two of those deserve a warning:

- `remove(x)` raises `ValueError` if `x` is not in the list. `pop()` raises `IndexError` on an
  empty list.
- `extend` takes another *iterable* (list, tuple, set…). `append` takes exactly one item. If you
  want to add a single list as one element, use `append`:
  `tasks.append(["a", "b"])` gives one nested list; `tasks.extend(["a", "b"])` gives two items.

There is also `clear()` to empty a list and `copy()` to duplicate it — we will meet `copy()` again
in section 8, because it is how you break the aliasing trap.

### 2.5 `sort()` versus `sorted()` — the classic bug

These two look identical and behave completely differently.

- `lst.sort()` sorts **the list in place** and returns `None`.
- `sorted(lst)` returns a **new sorted list** and leaves the original alone.

So this is a bug:

```python
numbers = [3, 1, 2]

result = numbers.sort()   # WRONG: sort() returns None
print(result)
print(numbers)
```

```text
None
[1, 2, 3]
```

The list *is* sorted — but `result` is `None`, because `sort()` does not hand the sorted list back.
Whenever you want the sorted value, use `sorted()`:

```python
numbers = [3, 1, 2]

result = sorted(numbers)
print(result)   # the new sorted list
print(numbers)  # the original is untouched

# Sorting strings is alphabetical, and case matters:
names = ["Zoe", "adam", "Bob"]
print(sorted(names))
print(sorted(names, key=str.lower))   # case-insensitive
```

```text
[1, 2, 3]
[3, 1, 2]
['Bob', 'Zoe', 'adam']
['adam', 'Bob', 'Zoe']
```

Rule of thumb: `sort()` when you are done with the original order and want to save memory.
`sorted()` when you want to keep the original — which is almost always.

The same pair exists for reversing. `lst.reverse()` reverses the list **in place** and returns
`None`; `reversed(lst)` returns a new reversed sequence and leaves the original alone. Use
`reversed()` when you want to loop backwards over something without disturbing it:

```python
steps = ["load", "chunk", "embed", "store"]

for step in reversed(steps):
    print(step)

print(steps)   # unchanged
```

```text
store
embed
chunk
load
['load', 'chunk', 'embed', 'store']
```

---

## 3. Tuples — ordered and unchangeable

A **tuple** is like a list that refuses to be modified. You create one with parentheses.

```python
point = (3, 7)
print(point)
print(point[0], point[1])
print(point[0:2])   # slicing works exactly like on lists
print(len(point))

try:
    point[0] = 99
except TypeError as error:
    print("TypeError:", error)
```

```text
(3, 7)
3 7
(3, 7)
2
TypeError: 'tuple' object does not support item assignment
```

### 3.1 Why tuples exist

Three good reasons to pick a tuple over a list:

1. **They cannot be changed by accident.** A function that receives a tuple cannot have its
   arguments corrupted by another function. This is why `return` values that must not be edited are
   often tuples.
2. **They are hashable** (see section 6.2), which means they can be used as dictionary keys and
   stored in sets. A list cannot.
3. **They are slightly cheaper** to create and read than a list.

### 3.2 The single-element tuple trap

This one catches nearly everyone. Parentheses with one item and no comma are just parentheses:

```python
not_a_tuple = (5)      # this is just the integer 5
print(type(not_a_tuple))

a_real_tuple = (5,)    # the trailing comma is what makes it a tuple
print(type(a_real_tuple))
print(a_real_tuple)
```

```text
<class 'int'>
<class 'tuple'>
(5,)
```

`not_a_tuple` has no `append`, no slicing to a list, no length beyond `TypeError`. If you write
`(5)` and expect a tuple, you get an `int`. **The rule: one element in a tuple always needs a
trailing comma.**

### 3.3 Unpacking and swapping

**Unpacking** takes a sequence and assigns its items to several names at once. It works on lists and
tuples alike.

```python
user_id, username, role = (42, "aarush", "engineer")
print(user_id, username, role)

# Unpacking works with lists too, and with fewer items than you might expect:
first, *rest = ["a", "b", "c", "d"]
print("first:", first)
print("rest:", rest)

# The classic swap, in one line, no temporary variable:
x, y = 10, 20
print("before:", x, y)
x, y = y, x
print("after: ", x, y)
```

```text
42 aarush engineer
first: a
rest: ['b', 'c', 'd']
before: 10 20
after:  20 10
```

The `*rest` form — "everything else" — is how you grab the first item and the remainder. It is very
handy when you know the first element is special and the rest is a variable-length tail.

---

## 4. Dictionaries — key to value

A **dict** stores *pairs*: a **key** and a **value**. You look things up by key, not by position.
Keys must be unique and hashable; values can be anything at all, including other dicts and lists.

```python
model = {
    "name": "gpt-5",
    "temperature": 0.2,
    "max_tokens": 1024,
}

print(model["name"])
print(model["max_tokens"])

model["top_p"] = 0.9        # add a new key
model["temperature"] = 0.7  # overwrite an existing key
print(model)
```

```text
gpt-5
1024
{'name': 'gpt-5', 'temperature': 0.7, 'max_tokens': 1024, 'top_p': 0.9}
```

### 4.1 `.get()` — the safe way to read a key

`d[key]` raises `KeyError` when the key is missing. `.get(key, default)` returns the default
instead. For code that talks to the outside world, `.get()` is usually what you want.

```python
settings = {"model": "gpt-5"}

print(settings.get("model"))
print(settings.get("temperature", 0.2))   # default used, key is absent
print(settings.get("temperature"))       # default used, key is absent -> None

try:
    print(settings["temperature"])
except KeyError as error:
    print("KeyError:", error)
```

```text
gpt-5
0.2
None
KeyError: 'temperature'
```

The `.get()` version never raised. That is the whole point: **`.get()` is for "might not be
there"; `d[key]` is for "I know it is there".** If the key must exist, `d[key]` is actually the
better choice, because it fails loudly instead of silently producing `None`.

### 4.2 Everything else a dict can do

```python
config = {"model": "gpt-5", "temperature": 0.2, "max_tokens": 1024}

print("model" in config)      # membership test
print("top_p" in config)

print(list(config.keys()))    # all the keys
print(list(config.values()))  # all the values
print(list(config.items()))   # (key, value) pairs

config.update({"temperature": 0.5, "seed": 7})   # merge in more pairs
print(config)

removed = config.pop("seed")  # remove a key and return its value
print("removed:", removed)
print("max_tokens" in config)

config.setdefault("stream", False)   # add the key only if it is missing
print("stream:", config["stream"])

del config["stream"]                  # delete a key without returning it
print("stream" in config)
```

```text
True
False
['model', 'temperature', 'max_tokens']
['gpt-5', 0.2, 1024]
[('model', 'gpt-5'), ('temperature', 0.2), ('max_tokens', 1024)]
{'model': 'gpt-5', 'temperature': 0.5, 'max_tokens': 1024, 'seed': 7}
removed: 7
True
stream: False
False
```

`setdefault(key, value)` is a one-liner for "create this if it does not exist yet, otherwise leave
it alone". It is most useful for counters and caches.

### 4.3 Iteration order is guaranteed

Since Python 3.7, a dict keeps its keys **in the order you inserted them**. This is a language
guarantee, not an accident of the implementation. Earlier versions did not promise it.

```python
tool_registry = {}
tool_registry["search"] = "search_web"
tool_registry["calculator"] = "calc"
tool_registry["summarise"] = "summarise_text"

print(list(tool_registry.keys()))
```

```text
['search', 'calculator', 'summarise']
```

You can therefore rely on "first key" and "last key" and "the order I added things in". But do not
rely on the *order of a set* — that one is not guaranteed.

### 4.4 Nested dicts and the dict comprehension preview

Dicts nest naturally, and a dict comprehension builds one in a single expression (you will meet the
full syntax in [07-comprehensions-and-iterators.md](07-comprehensions-and-iterators.md)):

```python
users = {
    "u1": {"name": "Aarush", "plan": "pro"},
    "u2": {"name": "Meera", "plan": "free"},
}

print(users["u1"]["plan"])
print(users["u2"]["name"])

# Build a dict from two lists with a dict comprehension:
tokens = ["hello", "world", "hello"]
ids = [101, 102, 103]

token_to_id = {token: token_id for token, token_id in zip(tokens, ids)}
print(token_to_id)
```

```text
pro
Meera
{'hello': 103, 'world': 102}
```

Look closely at that last line: the duplicate key `"hello"` overwrote the earlier value, so the dict
now has **two** entries, not three. Duplicate keys silently collapse — a useful property, and
also a bug source when you meant to keep both.

---

## 5. Sets — unique items, fast lookups

A **set** is an unordered collection of unique items. You create one with braces or by calling
`set()`.

```python
tags = {"python", "ai", "rag"}

tags.add("llm")       # add one item
tags.discard("ai")    # remove if present, no error if not
tags.remove("rag")    # remove, but raises KeyError if not present

print(sorted(tags))   # sets have no order, so sort before printing
print("llm" in tags)
print(len(tags))
```

```text
['llm', 'python']
True
2
```

### 5.1 `remove` versus `discard`

- `remove(x)` — delete `x`; raise `KeyError` if it is not there.
- `discard(x)` — delete `x` if it is there; do nothing if it is not.

`discard` is the forgiving one. Use it when the item may or may not be present; use `remove` when
its absence is a bug you want to hear about.

### 5.2 Sets are fast at "am I in there?"

Checking whether an item is in a set is dramatically faster than checking a list, because a set
stores a hashed version of each item and can jump straight to it. The difference matters when you
are testing millions of items.

```python
import time

items = [f"item_{n}" for n in range(100_000)]
allowed = set(items[:2_000])


def time_misses(container, attempts=1_000):
    """Time 'is this missing item present?' - the worst case for a list."""
    start = time.perf_counter()
    for _ in range(attempts):
        "not_present" in container
    return time.perf_counter() - start


list_time = time_misses(items)
set_time = time_misses(allowed)

print(f"list lookup took {list_time:.4f}s")
print(f"set lookup took  {set_time:.4f}s")
print(f"the set was {list_time / set_time:.0f}x faster")
```

Representative output — the exact timings depend on your machine, but the ratio is always in the
thousands:

```text
list lookup took 1.6030s
set lookup took  0.0001s
the set was 27309x faster
```

Your exact numbers will differ — the ratio is the point. A list membership test has to walk the
list from the start every single time, so it is O(n) per question (O means "grows in proportion
to"). A set membership test is O(1): one hash, one lookup, done, no matter how big the set grows.

The practical rule: if you are about to write `"x" in some_big_list` inside a loop, and you will
do it many times, convert the list to a set first.

### 5.3 Set algebra

Sets support the four classic operations, and each one solves a real problem.

| Operation | Meaning | Name |
|---|---|---|
| `a \| b` | items in either | union |
| `a & b` | items in both | intersection |
| `a - b` | items in `a` but not `b` | difference |
| `a ^ b` | items in exactly one | symmetric difference |

Here is the realistic use case: deduplicating tags coming from several sources.

```python
tags_from_pdf = {"ai", "python", "pdf"}
tags_from_web = {"ai", "blog", "python"}
tags_from_email = {"ai", "urgent"}

all_tags = tags_from_pdf | tags_from_web | tags_from_email
shared = tags_from_pdf & tags_from_web
only_pdf = tags_from_pdf - tags_from_web
in_but_not_both = tags_from_pdf ^ tags_from_web

print("all:     ", sorted(all_tags))
print("shared:  ", sorted(shared))
print("only pdf:", sorted(only_pdf))
print("either:  ", sorted(in_but_not_both))
```

```text
all:      ['ai', 'blog', 'pdf', 'python', 'urgent']
shared:   ['ai', 'python']
only pdf: ['pdf']
either:   ['blog', 'pdf']
```

The same operations exist as *methods* — `a.union(b)`, `a.intersection(b)`, `a.difference(b)`,
`a.symmetric_difference(b)` — and those also accept any iterable. The `|` operator requires both
sides to be sets.

---

## 6. Mutable versus immutable — and the aliasing trap

A container is **mutable** if you can change its contents after creating it. Lists, dicts and sets
are mutable. Tuples, strings and numbers are **immutable** — trying to change one raises an error.

### 6.1 The aliasing trap

Assigning a list to a second name does **not** copy it. Both names now point at the *same* list
object in memory.

```python
original = ["gpt-5"]
alias = original          # NO copy happens here

alias.append("claude-opus-4")

print("original:", original)
print("alias:   ", alias)
print("same object?", original is alias)
```

```text
original: ['gpt-5', 'claude-opus-4']
alias:    ['gpt-5', 'claude-opus-4']
same object? True
```

`original` changed even though you never touched it. This is called **aliasing**, and it causes
bugs that look impossible: a function mutates a list and the caller's list mysteriously changes.

The fixes are `.copy()`, `list(...)` and `a[:]` — all three make a shallow copy.

```python
original = ["gpt-5"]

copy_a = original.copy()
copy_b = list(original)
copy_c = original[:]

copy_a.append("claude-opus-4")
print("original:", original)
print("copy_a:  ", copy_a)
print("copy_b:  ", copy_b)
print("copy_c:  ", copy_c)
```

```text
original: ['gpt-5']
copy_a:   ['gpt-5', 'claude-opus-4']
copy_b:   ['gpt-5']
copy_c:   ['gpt-5']
```

### 6.2 Deep copy for nested structures

A shallow copy only copies the outer container. If the values *inside* are themselves mutable, they
are still shared.

```python
import copy

config = {"model": "gpt-5", "options": {"temperature": 0.2}}

shallow = config.copy()
shallow["options"]["temperature"] = 0.9
print("after shallow copy, config is:", config)

deep = copy.deepcopy(config)
deep["options"]["temperature"] = 0.1
print("after deep copy, config is:", config)
print("deep copy's options:", deep["options"])
```

```text
after shallow copy, config is: {'model': 'gpt-5', 'options': {'temperature': 0.9}}
after deep copy, config is: {'model': 'gpt-5', 'options': {'temperature': 0.9}}
deep copy's options: {'temperature': 0.1}
```

The shallow copy shared the inner `options` dict, so changing it changed the original. The deep
copy built fresh inner objects, so the original stayed untouched. Use `copy.deepcopy` whenever the
structure nests more than one level deep and you need genuine independence.

### 6.3 Why a list is not hashable

A **hash** is a fixed-size number Python computes from a value so it can look it up quickly. Some
values cannot be hashed because they can change while Python is trying to use them as a key. A list
can change, so it is **unhashable** and cannot be a dict key or a set member. A tuple can never
change, so it is hashable.

```python
pair = ("a", "b")
print(hash(pair) == hash(("a", "b")))   # same value -> same hash

try:
    {("a", "b"): 1}
    print("tuple works as a dict key")
except TypeError as error:
    print("TypeError:", error)

try:
    {["a", "b"]: 1}
except TypeError as error:
    print("TypeError:", error)
```

```text
True
tuple works as a dict key
TypeError: unhashable type: 'list'
```

This is exactly why tuples are the right choice for things like a coordinate pair or a fixed
`(key, value)` option you want to store in a set.

---

## 7. Nested structures, and how to read them

Real data nests. A chat message has metadata, a metadata block has a list of tags. When you `print`
a nested structure, Python shows you its shape — read it like a tree.

```text
chat
├── id .............. "chat_01"
├── model ........... "gpt-5"
├── messages ........ a LIST of 2 dicts
│   ├── [0]  role "user"       content "Summarise the news"
│   └── [1]  role "assistant"  content "Here is the summary"
│                          └── sources .... a LIST of 2 strings
│                              ├── [0] "bbc"
│                              └── [1] "reuters"
└── usage ............ a dict
    ├── input_tokens  42
    └── output_tokens 180
```

```python
chat = {
    "id": "chat_01",
    "model": "gpt-5",
    "messages": [
        {"role": "user", "content": "Summarise the news"},
        {"role": "assistant", "content": "Here is the summary",
         "sources": ["bbc", "reuters"]},
    ],
    "usage": {"input_tokens": 42, "output_tokens": 180},
}

# Read it step by step, one level at a time.
print(chat["model"])
print(chat["messages"][0]["content"])
print(chat["messages"][1]["sources"][0])
print(chat["usage"]["output_tokens"])

# Two ways to walk every message.
for message in chat["messages"]:
    print(message["role"], "->", message["content"][:20])

for role, message in zip(chat["messages"], chat["messages"]):
    print(role["role"], "->", message["content"][:20])
```

```text
gpt-5
Summarise the news
bbc
180
user -> Summarise the news
assistant -> Here is the summary
user -> Summarise the news
assistant -> Here is the summary
```

The last loop is deliberately silly — it zips the list with itself — to show a shape you will meet
later: `zip` pairs items from two sequences, so it is a natural way to pull a key and a value out
of two parallel lists.

---

## 8. `del` — and the classic delete-while-looping bug

`del` removes an item by position. `del lst[0]` deletes the first item and shifts everything left.

```python
tasks = ["a", "b", "c", "d"]
del tasks[1]
print(tasks)

del tasks[0]
print(tasks)

fruits = ["apple", "banana"]
del fruits
try:
    print(fruits)
except NameError as error:
    print("NameError:", error)
```

```text
['a', 'c', 'd']
['c', 'd']
NameError: name 'fruits' is not defined
```

That last `NameError` is worth understanding: `del fruits` removes the *name* entirely, so the
variable no longer exists. `del fruits[0]` removes only the item.

### 8.1 Never delete while iterating

This is a genuine trap. If you delete items from a list while a `for` loop is walking over it, the
loop's position moves forward while your deletion moves the remaining items backward — so some
items get skipped.

Here is a case where the bug is visible. The list holds three `1`s, and we want to remove all of
them:

```python
numbers = [1, 1, 2, 3, 1]

for number in numbers:
    if number == 1:
        numbers.remove(number)   # WRONG: removes the FIRST '1' it can find

print(numbers)
```

```text
[2, 3, 1]
```

One `1` survived. The first `remove` took out the *first* `1`, not the one the loop was looking
at, so the loop's next step landed on a different element and stepped over the remaining `1`s.

The correct way is to build a new list of what you want to keep:

```python
numbers = [1, 1, 2, 3, 1]
survivors = [number for number in numbers if number != 1]
print(survivors)

# Or, if you must edit the original in place, iterate over a copy.
numbers = [1, 1, 2, 3, 1]
for number in numbers[:]:
    if number == 1:
        numbers.remove(number)
print(numbers)
```

```text
[2, 3]
[2, 3]
```

Both give the right answer. The comprehension version is the pattern you should actually use —
and you will meet it properly in the next file.

---

## 9. `enumerate` and `zip` — pairing things up

### 9.1 `enumerate` gives you the index for free

When you need both the item and its position, `enumerate` saves you from writing
`for i in range(len(lst))`.

```python
models = ["gpt-5", "claude-opus-4", "gemini-3-pro"]

for index, model in enumerate(models):
    print(f"{index}: {model}")

# start=1 is handy when you want human-friendly numbering
for number, model in enumerate(models, start=1):
    print(f"{number}. {model}")
```

```text
0: gpt-5
1: claude-opus-4
2: gemini-3-pro
1. gpt-5
2. claude-opus-4
3. gemini-3-pro
```

### 9.2 `zip` walks two sequences in parallel

```python
prompts = ["Translate to French", "Translate to German"]
models = ["gpt-5", "claude-opus-4"]

for prompt, model in zip(prompts, models):
    print(f"{model} -> {prompt}")

# zip stops at the shortest sequence
print(list(zip([1, 2, 3], ["a", "b"])))
```

```text
gpt-5 -> Translate to French
claude-opus-4 -> Translate to German
[(1, 'a'), (2, 'b')]
```

That last line matters: `zip` **truncates** to the shorter one. If you need every element, use
`itertools.zip_longest` (see [14-standard-library.md](14-standard-library.md)).

### 9.3 Ranking with `sorted(d.items(), key=...)`

This is the idiom for "sort a dictionary by its values" — for example, ranking tools by how often
they were called.

```python
usage = {
    "search": 120,
    "calculator": 45,
    "summarise": 300,
    "translate": 12,
}

# Sort by the value (the second element of each (key, value) pair).
ranked = sorted(usage.items(), key=lambda pair: pair[1], reverse=True)
print(ranked)

for name, count in ranked:
    print(f"{name:12} {count}")

# Sorting by key instead:
print(sorted(usage.items(), key=lambda pair: pair[0]))
```

```text
[('summarise', 300), ('search', 120), ('calculator', 45), ('translate', 12)]
summarise    300
search       120
calculator   45
translate    12
[('calculator', 45), ('search', 120), ('summarise', 300), ('translate', 12)]
```

Note the `key=lambda pair: pair[1]`: `sorted` needs to know *what* to compare. By default it
compares the whole tuple, which for `(key, value)` pairs means it compares keys first. The `key`
argument lets you choose the value instead.

---

## 10. Which container should I use?

Here is the decision table, with AI-shaped examples you will actually meet.

| Your data | Use | Why | Example |
|---|---|---|---|
| An ordered sequence of chat messages | **list** | order matters, it grows | `messages = [{"role": "user", ...}]` |
| A fixed set of parameters that must not change | **tuple** | immutable, hashable | `config = ("gpt-5", 0.2, 1024)` |
| A tool registry: name → function | **dict** | lookup by name | `tools = {"search": search_fn}` |
| Unique model names you have already used | **set** | uniqueness, fast membership | `seen = {"gpt-5", "claude-opus-4"}` |
| A JSON object from an API response | **dict** | it is already key → value | `response.json()` |
| A `(name, score)` pair you want to store in a set | **tuple** | hashable, immutable | `{( "gpt-5", 0.91 )}` |
| A transcript split into paragraphs | **list** | ordered, will be re-read | `paragraphs = text.split("\n\n")` |
| The tags on a document | **set** | dedupe and compare | `tags = {"ai", "rag"}` |

If you are still unsure, ask two questions in order:

1. Do I look things up **by name**? → **dict**.
2. Do I only care **whether something is present**? → **set**.
3. Otherwise → **list**, or **tuple** if it must never change.

---

## 11. A taste of `collections`

Python's built-in containers cover most needs, but the standard library ships specialised versions
in the `collections` module. Worth knowing they exist now; you will use them properly in
[14-standard-library.md](14-standard-library.md).

```python
from collections import Counter, defaultdict, deque

# Counter: count how often each item appears.
words = ["a", "b", "a", "c", "a", "b"]
print(Counter(words))
print(Counter(words).most_common(2))

# defaultdict: a dict that creates missing keys for you.
inventory = defaultdict(int)
for item in ["apple", "apple", "pear"]:
    inventory[item] += 1
print(dict(inventory))

# deque: a list with cheap add/remove at BOTH ends.
queue = deque(["job1", "job2"])
queue.append("job3")
queue.appendleft("job0")
print(list(queue))
```

```text
Counter({'a': 3, 'b': 2, 'c': 1})
[('a', 3), ('b', 2)]
{'apple': 2, 'pear': 1}
['job0', 'job1', 'job2', 'job3']
```

`Counter` replaces a lot of hand-rolled counting code, `defaultdict` replaces a lot of
`if key not in dict` code, and `deque` is the right queue for a streaming agent.

---

## 🧪 Try it yourself

### Exercise 1 — Read the trace

What does this print?

```python
data = [10, 20, 30, 40, 50]
print(data[1:4])
print(data[::2])
print(data[-2:])
```

<details>
<summary>Hint</summary>

Remember: `stop` is exclusive, `step` of 2 skips every other item, and a negative start counts
from the end.
</details>

<details>
<summary>Solution</summary>

```text
[20, 30, 40]
[10, 30, 50]
[40, 50]
```

`data[1:4]` takes indices 1, 2, 3. `data[::2]` takes indices 0, 2, 4. `data[-2:]` starts at
index -2 (which is `40`) and runs to the end.
</details>

### Exercise 2 — Fix the aliasing bug

This function is supposed to add a tag to the document, but it changes the caller's list. Fix it.

```python
def add_tag(document, tag):
    document["tags"].append(tag)
    return document

doc = {"title": "RAG basics", "tags": ["ai"]}
result = add_tag(doc, "rag")
print(doc)
print(result is doc)
```

<details>
<summary>Hint</summary>

Find the line that mutates a shared object. You need a copy that does not share its inner list.
</details>

<details>
<summary>Solution</summary>

```python
import copy

def add_tag(document, tag):
    updated = copy.deepcopy(document)   # deep copy: inner list is independent too
    updated["tags"].append(tag)
    return updated

doc = {"title": "RAG basics", "tags": ["ai"]}
result = add_tag(doc, "rag")
print(doc)
print(result is doc)
```

```text
{'title': 'RAG basics', 'tags': ['ai']}
False
```

A shallow `document.copy()` is not enough: `updated["tags"]` would still be the same list object
as `document["tags"]`. This is the nested case that `deepcopy` exists for.
</details>

### Exercise 3 — The single-element tuple

Predict the output, then run it:

```python
result = (42)
print(type(result))
result = (42,)
print(type(result))
```

<details>
<summary>Hint</summary>

Parentheses around a single value are just grouping. What does the trailing comma change?
</details>

<details>
<summary>Solution</summary>

```text
<class 'int'>
<class 'tuple'>
```

Without the comma `(42)` is an ordinary integer. With it, `(42,)` is a one-element tuple.
</details>

### Exercise 4 — Rank the tools

You have a dictionary of tool usage counts. Write code that prints the tool names from most used
to least used, one per line, and only for tools used more than 50 times.

<details>
<summary>Hint</summary>

`sorted(d.items(), key=lambda pair: pair[1], reverse=True)` sorts by value. Then filter.
</details>

<details>
<summary>Solution</summary>

```python
usage = {"search": 120, "calculator": 45, "summarise": 300, "translate": 12}

ranked = sorted(usage.items(), key=lambda pair: pair[1], reverse=True)

for name, count in ranked:
    if count > 50:
        print(f"{name}: {count}")
```

```text
summarise: 300
search: 120
```

You could also filter first and sort after — the order of those two steps does not change the
result here, because sorting is stable and the filter keeps the relative order.
</details>

### Exercise 5 — Dedup and compare tags

Two documents have tags. Write code that prints: the tags used by *both* documents, and the tags
used by *exactly one* of them. Use set operations, not loops with `in`.

<details>
<summary>Hint</summary>

`&` is intersection, `^` is symmetric difference.
</details>

<details>
<summary>Solution</summary>

```python
doc_a_tags = {"ai", "rag", "python"}
doc_b_tags = {"ai", "agents", "python"}

print("both:      ", sorted(doc_a_tags & doc_b_tags))
print("exactly one:", sorted(doc_a_tags ^ doc_b_tags))
```

```text
both:       ['ai', 'python']
exactly one: ['agents', 'rag']
```
</details>

### Exercise 6 — Summarise a chat history

Write a function `summarise(messages)` that returns a dict with three keys: `"count"` (number of
messages), `"roles"` (a list of the roles in order) and `"total_chars"` (the total number of
characters across all message contents). Use a loop, then try again with a comprehension if you
can.

<details>
<summary>Hint</summary>

`messages` is a list of dicts like `{"role": "user", "content": "Hello"}`.
</details>

<details>
<summary>Solution</summary>

```python
messages = [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi there, how can I help?"},
    {"role": "user", "content": "Summarise the news"},
]

def summarise(messages):
    return {
        "count": len(messages),
        "roles": [message["role"] for message in messages],
        "total_chars": sum(len(message["content"]) for message in messages),
    }

print(summarise(messages))
```

```text
{'count': 3, 'roles': ['user', 'assistant', 'user'], 'total_chars': 48}
```
</details>

---

## ✅ Checkpoint

**1. What does `fruits[-1]` return, and why is there no `fruits[-0]`?**

<details>
<summary>Answer</summary>

It returns the last item. Negative indexes count from the end, and `-0` is the same as `0`, so it
returns the *first* item instead. There is no separate "last index" — it is `len(fruits) - 1`.
</details>

**2. What is the difference between `lst.sort()` and `sorted(lst)`?**

<details>
<summary>Answer</summary>

`lst.sort()` sorts in place and returns `None`. `sorted(lst)` returns a new sorted list and leaves
the original untouched.
</details>

**3. Why does `(5)` behave differently from `(5,)`?**

<details>
<summary>Answer</summary>

`(5)` is just the integer 5 in parentheses — parentheses are grouping, not a tuple marker.
`(5,)` has a trailing comma, which is what makes it a one-element tuple.
</details>

**4. When should you use `d.get(key)` instead of `d[key]`?**

<details>
<summary>Answer</summary>

When the key might be missing. `d[key]` raises `KeyError`; `d.get(key)` returns `None` (or a
default you supply) instead.
</details>

**5. What does `b = a` do when `a` is a list? How do you get a real copy?**

<details>
<summary>Answer</summary>

It creates a second name for the *same* list — no copy happens, so changes to either are visible
through both. Use `a.copy()`, `list(a)` or `a[:]` for a shallow copy, and `copy.deepcopy(a)` when
the structure nests.
</details>

**6. Why can a tuple be a dictionary key but a list cannot?**

<details>
<summary>Answer</summary>

Tuples are immutable, so their hash value never changes and Python can trust it. Lists are
mutable, so they are unhashable and rejected with `TypeError: unhashable type: 'list'`.
</details>

**7. Why is deleting from a list inside a `for` loop a bug?**

<details>
<summary>Answer</summary>

Each deletion shifts the remaining items one place to the left, but the loop's index keeps moving
right, so items get skipped. Build a new list of what you want to keep instead.
</details>

**8. You need a mapping from tool name to tool function. Which container, and why not a list?**

<details>
<summary>Answer</summary>

A dict — you look the tool up by name, not by position. A list would need you to scan for the name
every time, and would allow duplicate names.
</details>

---

## 🐛 Common mistakes

| Mistake | What you see | Fix |
|---|---|---|
| `result = lst.sort()` | `result` is `None` even though `lst` is sorted | Use `sorted(lst)` when you want the value back |
| `(5)` instead of `(5,)` | `TypeError: object of type 'int' has no len()` | Add the trailing comma for a one-element tuple |
| `d[key]` on a missing key | `KeyError: 'temperature'` | Use `d.get(key, default)` when the key may be absent |
| `b = a` then mutating `a` | `b` changes too | Use `a.copy()`, `list(a)`, `a[:]` or `copy.deepcopy(a)` |
| `for x in lst: del lst[i]` inside the loop | Some items silently survive | Build a new list: `[x for x in lst if keep(x)]` |
| `lst.remove(x)` on a missing value | `ValueError: list.remove(x): x not in list` | Use `lst.discard(x)` on a set, or check `x in lst` first |
| `a.extend(b)` when you wanted one item | The items of `b` land in `a` individually | Use `a.append(b)` to add `b` as a single element |
| Slicing with an inclusive `stop` | You get one item fewer than expected | `stop` is exclusive: `lst[0:3]` is the first three items |
| `set` items assumed to be ordered | Printing order changes between runs | Sort before printing: `sorted(my_set)` |
| `dict` built from a list with duplicate keys | Later values silently overwrite earlier ones | Check for duplicates, or use a list of pairs |

---

## 🔗 Resources

- [Data Structures — Python Tutorial](https://docs.python.org/3/tutorial/datastructures.html) — the
  official tutorial section on lists, tuples, dicts and sets; the clearest official intro.
- [Built-in Types](https://docs.python.org/3/library/stdtypes.html) — the reference for every
  method on lists, tuples, dicts and sets, including exact behaviour of edge cases.
- [Sequence Types](https://docs.python.org/3/library/stdtypes.html#sequence-types) — the shared
  behaviour of list, tuple, str and `range`, including the slice grammar.
- [Slicings](https://docs.python.org/3/reference/expressions.html#slicings) — the formal rules for
  `sequence[start:stop:step]`, including how out-of-range values behave.
- [`sorted()`](https://docs.python.org/3/library/functions.html#sorted) — the full signature,
  including the `key` and `reverse` arguments you will use constantly.
- [`copy` — Shallow and deep copy operations](https://docs.python.org/3/library/copy.html) — what
  "shallow" and "deep" actually mean, with the exact list of what gets copied.
- [`collections`](https://docs.python.org/3/library/collections.html) — `Counter`, `deque`,
  `defaultdict`, `OrderedDict` and friends.
- [PEP 468 — Preserving keyword argument order](https://peps.python.org/pep-0468/) and
  [PEP 520](https://peps.python.org/pep-0520/) — why dicts are guaranteed to keep insertion
  order from Python 3.7 onwards.
- [PEP 484 — Type hints](https://peps.python.org/pep-0484/) — the origin of `dict[str, int]` style
  annotations, which you will meet in
  [11-type-hints-and-modern-python.md](11-type-hints-and-modern-python.md).
- [The Python Tutorial: Sorting HOW TO](https://docs.python.org/3/howto/sorting.html) — how
  `key=` and `reverse=` interact, with worked examples.
- [Real Python: Python Lists and Tuples](https://realpython.com/python-lists-tuples/) — a
  community article with more examples of the same ideas.

---

## ➡️ Next

- [07 Comprehensions and iterators](07-comprehensions-and-iterators.md) — write loops in one
  expression, and meet generators, `yield` and the iterator protocol.

**← Previous:** [05 Functions](05-functions.md)
