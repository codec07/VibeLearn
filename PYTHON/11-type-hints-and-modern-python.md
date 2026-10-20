# Type Hints and Modern Python

Python does not make you declare types — it figures them out at runtime. But you can
*write* the types down anyway, and modern Python has a full set of tools for doing it
well. This file is about those tools: the annotations, the type checker that reads them,
and the newer syntax that Python 3.10 through 3.14 added while you were busy.

The payoff is specific and practical: a type checker can find your bugs **before you run
the code**. By the end you will be able to annotate a function, run `mypy` on it, read
what it says, and use the modern syntax that makes Python shorter and clearer.

> **⏱️ Time:** ~30 minutes
> **📚 Prereqs:** [10 Object-oriented programming](10-object-oriented-programming.md)
> **🎯 By the end you can:** Annotate your code with type hints, run `mypy` to catch bugs before
> execution, and use the modern Python syntax from 3.10 to 3.14.

---

## Why this matters for AI engineering

AI code has a lot of data flowing between components: a raw API response becomes a dict,
becomes a typed model, becomes a list of messages, becomes a prompt string. When one link
in that chain has the wrong shape, the failure appears far away from the cause — a
`KeyError` three layers deep, or a model that mysteriously returns nothing.

Type hints let a checker verify those links **statically**, before the code ever runs.
Modern Python libraries (pydantic, FastAPI, LangChain, Pydantic AI) are built on them:
FastAPI reads your annotations and generates an OpenAPI schema from them; pydantic uses
them to validate incoming data. If you want to work on a modern AI codebase, you will meet
type hints on your first day.

---

## 1. Why bother, in a dynamic language?

Python is **dynamically typed**: the type of a value is checked when the code runs, not
when it is written. `1 + "two"` is a `TypeError` — but only once that line executes.

Adding **type hints** (also called *type annotations*) gives you four things:

1. **Self-documenting code.** `def load_config(path: str) -> dict:` tells you everything about the
   contract without reading the body.
2. **Bugs caught before you run.** A type checker reads the annotations and finds the mistakes.
3. **Better editor support.** Your editor can now autocomplete correctly and show real errors
   inline.
4. **Compatibility with modern libraries.** Many of them require or strongly prefer annotations.

The important caveat, and the one that trips everybody up: **annotations are not enforced at
runtime.** Python stores them, but never checks them while your program runs.

---

## 2. Basic annotations

An annotation is a type written after a name, followed by a colon.

```python
def greet(name: str) -> str:
    """Return a greeting. The annotations are documentation, not checks."""
    return f"Hello, {name}!"


count: int = 0
names: list[str] = []
prices: dict[str, float] = {}

print(greet("Ada"))
print(count, names, prices)

# Annotations are NOT enforced at runtime:
print(greet(123))   # works fine, no error
```

```text
Hello, Ada!
0 [] {}
Hello, 123!
```

That last line is the point. `greet(123)` returns `"Hello, 123!"` without complaint,
because Python never checks the annotation. The annotation is a **promise you make**, and
`mypy` is the tool that checks whether you kept it.

The two halves of a function signature:

```text
    def greet(name: str) -> str:
         ^^^^^^         ^^^^^^
         |               |
         |               +-- return type: what this function gives back
         +-- parameter type: what this function accepts
```

---

## 3. Built-in generics

Since Python 3.9, you can write `list[str]` and `dict[str, int]` directly instead of
importing `List` and `Dict` from the `typing` module. The lowercase versions are the
modern style.

```python
def first(items: list[str]) -> str | None:
    """Return the first item, or None if the list is empty."""
    if not items:
        return None
    return items[0]


scores: dict[str, int] = {"Ada": 98, "Grace": 95}
coords: tuple[int, int] = (3, 4)
tags: set[str] = {"ai", "agent"}

print(first(["a", "b"]))
print(scores["Ada"], coords, sorted(tags))
```

```text
a
98 (3, 4) ['agent', 'ai']
```

| Annotation | Meaning |
|---|---|
| `list[str]` | a list whose items are strings |
| `dict[str, int]` | a dictionary with string keys and integer values |
| `tuple[int, ...]` | a tuple of any length whose items are integers |
| `set[str]` | a set of strings |
| `dict[str, list[dict[str, str]]]` | yes, they nest. Keep them readable. |

---

## 4. `Optional[X]` versus `X | None`

These two mean **exactly the same thing**: "this value might be `None`".

```python
from typing import Optional, get_args


USERS = {1: "Ada", 2: "Grace"}


def find_name(user_id: int) -> Optional[str]:
    """Return the name, or None if the id is unknown."""
    return USERS.get(user_id)


def find_name_modern(user_id: int) -> str | None:
    """The same function, written with the 3.10+ pipe syntax."""
    return USERS.get(user_id)


print(find_name(1), find_name(99))
print(find_name_modern(1), find_name_modern(99))

# They really are the same type:
print(get_args(Optional[str]) == get_args(str | None))
```

```text
Ada None
Ada None
True
```

| | Use it when |
|---|---|
| `Optional[str]` | you must support Python 3.9 or older |
| `str \| None` | you are on Python 3.10+ (which this course targets) |

**Recommendation: use `X | None` on 3.10+.** It is shorter, it reads more naturally, and it is the
form the rest of the ecosystem has moved to. Keep `Optional[X]` only if you have to
support older Python.

---

## 5. The typing toolbox

Six annotations you will meet constantly. Each one has one job.

```python
from typing import Any, ClassVar, Final, Literal, TypeAlias, cast

MAX_RETRIES: Final = 3
MAX_TOKENS: Final = 4096

Mode: TypeAlias = Literal["fast", "accurate"]

settings: dict[str, Any] = {"model": "gpt-4o-mini", "retries": MAX_RETRIES}


class Agent:
    registry: ClassVar[dict[str, str]] = {}   # belongs to the class, not the instance

    def __init__(self, mode: Mode) -> None:
        self.mode = mode
        self.retries = MAX_RETRIES


def as_text(value: object) -> str:
    """cast() is a promise to the type checker: 'trust me, this is a str'."""
    return cast(str, value)


agent = Agent("fast")
print(agent.mode, agent.retries)
print(settings)
print(as_text("already a string"))
print(Agent.registry)
```

```text
fast 3
{'model': 'gpt-4o-mini', 'retries': 3}
already a string
{}
```

| Tool | One-line purpose | Real example |
|---|---|---|
| `Any` | "I do not care what this is" — turns off checking for that value | `settings: dict[str, Any]` |
| `cast(T, value)` | tell the checker to treat `value` as type `T` without checking | `cast(str, value)` |
| `Final` | this name will never change again | `MAX_RETRIES: Final = 3` |
| `Literal` | the value must be **exactly** one of these strings | `Literal["fast", "accurate"]` |
| `ClassVar` | this attribute belongs to the class, not to each instance | `registry: ClassVar[dict[str, str]]` |
| `TypeAlias` | this name is an alias for a whole type | `Mode: TypeAlias = Literal[...]` |

`Literal` is the one that saves the most bugs. Compare these two:

```python
from typing import Literal


# Without Literal: "accurate" is a perfectly legal string, and nothing catches a typo.
def set_mode(mode: str) -> None:
    print(mode)


# With Literal: mypy rejects "fastt" before the program ever runs.
def set_mode_strict(mode: Literal["fast", "accurate"]) -> None:
    print(mode)


set_mode("fastt")
set_mode_strict("fastt")
```

```text
fastt
fastt
```

Python is happy with both calls. mypy is not — see the exercise at the end of this file.

`cast()` deserves one warning: it **does not convert anything at runtime**. It only
changes what the type checker believes. If you `cast(str, 42)` and then call a string
method on it, you get an `AttributeError` at runtime. Use it when you know better than the
checker, not to silence it.

---

## 6. `Callable` and `Protocol` — swappable providers

These two are the reason type hints exist in AI code.

`Callable[[int, str], bool]` describes a **function**: what arguments it takes and what it
returns.

```python
from typing import Callable

RetryPolicy = Callable[[int, str], bool]


def should_retry(attempt: int, error: str) -> bool:
    return attempt < 3 and "timeout" in error


policy: RetryPolicy = should_retry
print(policy(1, "connection timeout"))
print(policy(3, "connection timeout"))
```

```text
True
False
```

The list in the brackets is the argument types; the thing after the comma is the return
type.

A **`Protocol`** describes an *interface* — "any object with this method is acceptable".
Nothing has to inherit from it.

```python
from typing import Protocol


class ChatProvider(Protocol):
    """Anything with this chat() method can be used as a provider."""

    def chat(self, model: str, prompt: str) -> str: ...


class RealProvider:
    def chat(self, model: str, prompt: str) -> str:
        return f"{model} answered: {prompt}"


class FakeProvider:
    def chat(self, model: str, prompt: str) -> str:
        return "fake answer"


def run(provider: ChatProvider, prompt: str) -> str:
    return provider.chat("gpt-4o-mini", prompt)


print(run(RealProvider(), "hi"))
print(run(FakeProvider(), "hi"))
```

```text
gpt-4o-mini answered: hi
fake answer
```

Look at what this buys you: `run()` works with either provider, the type checker
understands that both are acceptable, and swapping a real API for a fake in a test changes
**one line**. This is the single most useful typing pattern in AI engineering, and it is
covered in more depth in [10 Object-oriented
programming](10-object-oriented-programming.md).

---

## 7. `TypedDict` and `NewType`

**`TypedDict`** describes a dictionary with a known shape. It is a perfect fit for JSON payloads —
exactly what you get back from an API.

```python
from typing import TypedDict


class ChatResponse(TypedDict):
    id: str
    model: str
    content: str
    tokens: int


def render(response: ChatResponse) -> str:
    return f"{response['model']} said {response['content']} ({response['tokens']} tokens)"


payload: ChatResponse = {
    "id": "resp_123",
    "model": "gpt-4o-mini",
    "content": "RAG stands for retrieval-augmented generation.",
    "tokens": 12,
}

print(render(payload))
```

```text
gpt-4o-mini said RAG stands for retrieval-augmented generation. (12 tokens)
```

`TypedDict` is only a **description**. At runtime it is just a `dict`, so
`payload["tokens"]` works exactly as before. What you gain is that mypy will now catch a
missing key or a typo in a key name:

```python
from typing import TypedDict


class ChatResponse(TypedDict):
    id: str
    model: str
    content: str
    tokens: int


# mypy reports an extra key here:
bad: ChatResponse = {"id": "r1", "model": "m", "content": "c", "tokenz": 12}

# mypy reports a missing key here:
also_bad: ChatResponse = {"id": "r1", "model": "m", "content": "c"}

print(bad)
print(also_bad)
```

```text
{'id': 'r1', 'model': 'm', 'content': 'c', 'tokenz': 12}
{'id': 'r1', 'model': 'm', 'content': 'c'}
```

Both dictionaries run perfectly. mypy says:

```text
chat.py:12: error: Missing key "tokens" for TypedDict "ChatResponse"  [typeddict-item]
chat.py:12: error: Extra key "tokenz" for TypedDict "ChatResponse"  [typeddict-unknown-key]
chat.py:15: error: Missing key "tokens" for TypedDict "ChatResponse"  [typeddict-item]
```

**`NewType`** creates a type that is *distinct* from its underlying type but still behaves
identically at runtime.

```python
from typing import NewType

UserId = NewType("UserId", int)


def load_user(user_id: UserId) -> str:
    return f"user #{user_id}"


uid = UserId(42)
print(uid + 1)                 # still an int at runtime
print(type(uid).__name__)      # 'int' -- NewType does not create a new runtime type
print(load_user(uid))
```

```text
43
int
user #42
```

The point is that mypy will now complain if you pass a plain `int` where a `UserId` is
expected — so you cannot accidentally swap a `UserId` with a `ChatId` (both are `int`
underneath). At runtime nothing changes: a `NewType` value is just an `int`.

---

## 8. `TYPE_CHECKING` and `from __future__ import annotations`

Annotations are evaluated at runtime **unless** you tell Python not to. That can create
circular imports: module A needs B's type, and B needs A's type.

Two tools solve it.

`from __future__ import annotations` makes **every** annotation in the file a lazy string.
Python never evaluates them, so the names do not need to exist at runtime.

`if TYPE_CHECKING:` is a block that is `True` only for type checkers (mypy, pyright) and
`False` at runtime, so imports inside it never execute.

```python
from __future__ import annotations   # makes all annotations lazy strings

from typing import TYPE_CHECKING

if TYPE_CHECKING:                     # only type checkers see this
    from pathlib import Path


def find_notes(folder: Path) -> list[Path]:
    """`Path` is only needed for the annotation, so it is imported under TYPE_CHECKING."""
    return sorted(folder.glob("*.txt"))


# The real import happens here, at runtime, outside the TYPE_CHECKING block.
from pathlib import Path
from tempfile import TemporaryDirectory

with TemporaryDirectory() as folder:
    root = Path(folder)
    (root / "b.txt").write_text("second", encoding="utf-8")
    (root / "a.txt").write_text("first", encoding="utf-8")
    for note in find_notes(root):
        print(note.name, "->", note.read_text(encoding="utf-8"))
```

```text
a.txt -> first
b.txt -> second
```

If you only need one of them, prefer `from __future__ import annotations` — it is one line
and it removes the whole problem. If you are on Python 3.14 or newer, you get deferred
evaluation of annotations for free (PEP 649), so you need neither.

---

## 9. Running `mypy`

**mypy** is the most widely used static type checker for Python. It reads your annotations, follows
your code, and reports the places where the types do not line up.

Install it:

```bash
pip install mypy
```

Now create a file called `greet.py`:

```python
def greet(name: str) -> str:
    return f"Hello, {name}!"


print(greet("Ada"))
print(greet(42))
```

Run the checker on it:

```bash
mypy greet.py
```

```text
greet.py:6: error: Argument 1 to "greet" has incompatible type "int"; expected "str"  [arg-type]
Found 1 error in 1 file (checked 1 source file)
```

Read that carefully:

- `greet.py:6` — the file and the line number.
- `error:` — the severity.
- `Argument 1 to "greet" has incompatible type "int"; expected "str"` — what is wrong, in plain
  English.
- `[arg-type]` — the machine-readable error code, useful for silencing one specific rule.

The bug at line 6 would have raised a `TypeError` **when you ran it**. mypy found it without
running anything.

### The three errors you will see most

Here is a file with three typical mistakes — all of which Python itself is perfectly happy
with:

```python
def summarise(items: list[str]) -> str:
    return ", ".join(items)


scores: list[str] = [1, 2, 3]
result: int = summarise(["a"])
summarise("abc")

print(scores)
print(result)
print(summarise("abc"))
```

```text
[1, 2, 3]
a
a, b, c
```

```bash
mypy errors.py
```

```text
errors.py:5: error: List item 0 has incompatible type "int"; expected "str"  [list-item]
errors.py:5: error: List item 1 has incompatible type "int"; expected "str"  [list-item]
errors.py:5: error: List item 2 has incompatible type "int"; expected "str"  [list-item]
errors.py:6: error: Incompatible types in assignment (expression has type "str", variable has type "int")  [assignment]
errors.py:7: error: Argument 1 to "summarise" has incompatible type "str"; expected "list[str]"  [arg-type]
errors.py:11: error: Argument 1 to "summarise" has incompatible type "str"; expected "list[str]"  [arg-type]
Found 6 errors in 1 file (checked 1 source file)
```

1. **`[list-item]`** — you put the wrong type inside a list.
2. **`[assignment]`** — you assigned a `str` to a variable declared as an `int`.
3. **`[arg-type]`** — you passed the wrong type to a function.

### The `reveal_type()` trick

When you do not know what type mypy thinks something is, ask it. `reveal_type()` is a
special function that makes mypy print the type it inferred.

```python
from typing import reveal_type


def load_models() -> list[str]:
    return ["gpt-4o-mini"]


reveal_type(load_models())
reveal_type(load_models()[0])
```

```bash
mypy reveal.py
```

```text
reveal.py:8: note: Revealed type is "list[str]"
reveal.py:9: note: Revealed type is "str"
Success: no issues found in 1 source file
```

(If you *run* that file instead of checking it, `reveal_type` prints `Runtime type is
'list'` to stderr instead — that is its runtime behaviour. mypy replaces it with the
static type.)

`reveal_type` is a debugging tool for you, not for your code. Delete it before you commit.

### `--strict`

`mypy --strict` turns on a bundle of extra checks: no untyped functions, no implicit
`Any`, no missing type arguments on generic types. It is stricter than most teams need on
day one.

```bash
mypy --strict greet.py
```

```text
greet.py:6: error: Argument 1 to "greet" has incompatible type "int"; expected "str"  [arg-type]
Found 1 error in 1 file (checked 1 source file)
```

The same error, but now mypy will also complain about any function that has *no*
annotations at all. Start without `--strict`. Turn it on for new files once you are
comfortable.

---

## 10. Gradual typing: annotate the boundaries

You do not have to annotate everything. The idea is called **gradual typing**: you add
types where they buy the most, and leave the rest alone.

```text
    where to put your effort

    +--------------------------------------------------+
    |  INPUT      ->  annotated strictly                |
    |  your own functions  ->  annotated where it helps |
    |  INTERNAL   ->  left loose (Any is fine)          |
    |  OUTPUT     ->  annotated strictly                |
    +--------------------------------------------------+

    annotate the EDGES, not the middle
```

Concretely, in an AI pipeline you should annotate:

- **Function signatures** you call from elsewhere — the public surface of your module.
- **Data that crosses a boundary** — API responses, file contents, config values.
- **Return types** of anything whose result you rely on.

And you can safely leave alone:

- Local variables inside a function body. `total = 0` is fine; `total: int = 0` adds nothing.
- Tiny helper functions that never leave the module.
- Third-party objects you cannot control.

That is a real strategy, not a cop-out. A codebase where 100% of lines are annotated is
often a codebase where nobody annotates anything, because the cost is too high.

---

## 11. Runtime validation vs static typing

These are two different jobs, and confusing them is the biggest conceptual mistake in this
area.

```text
    STATIC TYPING (mypy)          RUNTIME VALIDATION (pydantic)
    ----------------------------   ---------------------------------
    reads your code, not your      inspects the actual data that
    actual data                    arrived

    catches: wrong types, wrong    catches: wrong values, missing
    argument counts, misspelled    fields, out-of-range numbers,
    attribute names                malformed JSON

    runs BEFORE your program        runs WHILE your program runs
    needs annotations              needs a schema
```

**Static typing cannot see the outside world.** mypy checks `def load(path: str) -> dict:` and
says "fine, you return a dict". It cannot tell you that the file contains `{"a": 1}` and
your code later expects `data["items"]`. Only runtime validation catches that.

Use `assert` for **internal invariants** — conditions your own code guarantees:

```python
def chunk(items: list[str], size: int) -> list[list[str]]:
    """Split a list into chunks of `size` items."""
    assert size > 0, "size must be positive"
    return [items[i:i + size] for i in range(0, len(items), size)]


print(chunk(["a", "b", "c", "d", "e"], 2))

try:
    chunk(["a"], 0)
except AssertionError as error:
    print("AssertionError:", error)
```

```text
[['a', 'b'], ['c', 'd'], ['e']]
AssertionError: size must be positive
```

`assert` is for "this should never happen". If it fires, your code has a bug — do not use
it to validate user input, because `python -O` disables assertions entirely.

For **data from outside your program**, use a validation library. **pydantic** is the
standard choice:

```bash
pip install pydantic
```

```python
from pydantic import BaseModel, ValidationError


class ChatRequest(BaseModel):
    model: str
    prompt: str
    temperature: float = 0.2


request = ChatRequest(model="gpt-4o-mini", prompt="Hello")
print(request.model, request.temperature)

try:
    ChatRequest(model="gpt-4o-mini")       # missing `prompt`
except ValidationError as error:
    print(type(error).__name__)
    print(error.error_count(), "problem(s)")
```

```text
gpt-4o-mini 0.2
ValidationError
1 problem(s)
```

pydantic uses the annotations you already wrote, checks the actual data against them at
runtime, and gives you a clear error listing every problem at once. You will meet it
properly in [17 Python for AI and data](17-python-for-ai-and-data.md).

The rule of thumb:

```text
    +--------------------------------+-------------------------+
    | Your OWN code, internal logic  | assert                  |
    | Data from outside (API, file,  | pydantic / manual checks|
    | user input, LLM output)        |                         |
    +--------------------------------+-------------------------+
```

---

## 12. Modern syntax you should know

### The walrus operator `:=`

Python 3.8 added the **assignment expression** operator, nicknamed the *walrus* because it
looks like a walrus peeking out of the water. It assigns **and** returns the value in one
go.

```python
import re

text = "order-123, order-456, order-789"
pattern = re.compile(r"order-\d+")

print(pattern.findall(text))

# The walrus operator assigns inside a condition, avoiding a second lookup.
if (found := pattern.search(text)):
    print("first match:", found.group())
```

```text
['order-123', 'order-456', 'order-789']
first match: order-123
```

Without the walrus you would have to call `pattern.search(text)` twice — and the second call
might return something different.

The most useful pattern is reading a file until it runs out:

```python
from pathlib import Path
from tempfile import TemporaryDirectory

with TemporaryDirectory() as folder:
    path = Path(folder) / "lines.txt"
    path.write_text("alpha\nbeta\ngamma\n", encoding="utf-8")

    with open(path, "r", encoding="utf-8") as handle:
        while (line := handle.readline()):
            print("read:", line.strip())
```

```text
read: alpha
read: beta
read: gamma
```

`while (line := handle.readline()):` reads a line, assigns it to `line`, and uses the
assigned value as the loop condition. When the file is empty, `readline()` returns `""`,
which is falsy, and the loop stops.

Another common use — avoiding a double dictionary lookup:

```python
scores = {"Ada": 98, "Grace": 95}

# Without walrus: two lookups
if "Ada" in scores:
    print(scores["Ada"])

# With walrus: one lookup
if (ada_score := scores.get("Ada")) is not None:
    print(ada_score)
```

```text
98
98
```

### The `match` statement (Python 3.10+)

`match` is Python's **structural pattern matching** — a way to match on the *shape* of a
value rather than just its equality. You met simple `if`/`elif` chains in [04 Control
flow](04-control-flow.md); `match` handles the multi-branch cases more cleanly.

```python
def classify(status: str) -> str:
    match status:
        case "pending":
            return "waiting to start"
        case "running":
            return "in progress"
        case "done" | "completed":
            return "finished"
        case _:
            return "unknown"


for status in ["pending", "running", "done", "exploded"]:
    print(f"{status:>9} -> {classify(status)}")
```

```text
  pending -> waiting to start
  running -> in progress
     done -> finished
  exploded -> unknown
```

The `case _:` line is the catch-all — the same role as `else` in an `if` chain. The `|` in
`case "done" | "completed":` means "either of these".

### Merging dictionaries with `|`

Python 3.9 added the `|` operator for dictionaries. It creates a **new** dictionary; the
originals are untouched.

```python
defaults = {"model": "gpt-4o-mini", "temperature": 0.2}
overrides = {"temperature": 0.9, "max_tokens": 1024}

config = defaults | overrides
print(config)
print(defaults)                    # unchanged
print(defaults | {"temperature": 0.5})
```

```text
{'model': 'gpt-4o-mini', 'temperature': 0.9, 'max_tokens': 1024}
{'model': 'gpt-4o-mini', 'temperature': 0.2}
{'model': 'gpt-4o-mini', 'temperature': 0.5}
```

The right-hand side wins on conflicts. `{**defaults, **overrides}` does the same thing,
but `|` is clearer about what it means.

### `list +=` and positional-only parameters

```python
numbers = [1, 2, 3]
numbers += [4, 5]                 # the same as numbers.extend([4, 5])
print(numbers)


def only_positional(a, b, /, c):
    """Everything before the / is positional-only."""
    return a, b, c


print(only_positional(1, 2, c=3))
print(only_positional(1, 2, 3))
```

```text
[1, 2, 3, 4, 5]
(1, 2, 3)
(1, 2, 3)
```

The `/` marker (Python 3.8+) means "these parameters can only be given positionally". It
is how you write a function whose parameter names might change later without breaking
anyone.

### `functools.cache` (Python 3.9+)

`functools.cache` remembers the result of a function for each set of arguments it was
called with. Call it again with the same arguments and you get the cached answer for free.

```python
from functools import cache


@cache
def expensive_total(prices: tuple[int, ...]) -> int:
    print("computing...")
    return sum(prices)


print(expensive_total((10, 20, 30)))
print(expensive_total((10, 20, 30)))   # cached, no "computing..."
print(expensive_total.cache_info())
```

```text
computing...
60
60
CacheInfo(hits=1, misses=1, maxsize=None, currsize=1)
```

`cache_info()` is how you check whether the cache is actually helping. `hits` is the
number of calls that were served from the cache; `misses` is the number that were
computed.

Note that the arguments must be **hashable** — lists and dicts cannot be cache keys, but
tuples and strings can.

---

## 13. Dataclasses with type hints

The combination of `@dataclass` and annotations is the modern way to describe a piece of
data. This is the pattern you will use most in AI code.

```python
from dataclasses import dataclass, field


@dataclass
class Message:
    role: str
    content: str

    def as_dict(self) -> dict[str, str]:
        return {"role": self.role, "content": self.content}


@dataclass
class ChatRequest:
    model: str = "gpt-4o-mini"
    messages: list[Message] = field(default_factory=list)
    temperature: float = 0.2
    tools: list[str] = field(default_factory=list)


request = ChatRequest(messages=[Message("user", "Hi!")])
print(request)
print(request.messages[0].as_dict())
```

```text
ChatRequest(model='gpt-4o-mini', messages=[Message(role='user', content='Hi!')], temperature=0.2, tools=[])
{'role': 'user', 'content': 'Hi!'}
```

Everything about this is now checkable by mypy: if you pass a `Message` where a `str` is
expected, mypy says so before the program runs.

---

## 14. Practical rules

A checklist you can actually follow. Print it out.

- [ ] **Annotate public function signatures.** Parameters and return type, always.
- [ ] **Do not annotate every local variable.** `total = 0` is fine.
- [ ] **Use a `dataclass` or `TypedDict` for data crossing a boundary** — API responses, file
      contents, config.
- [ ] **Use `Literal` for fixed string options** instead of bare `str`.
- [ ] **Use `Protocol` for a dependency you might swap** — a provider, a client, a clock.
- [ ] **Use `X | None` on Python 3.10+**, not `Optional[X]`.
- [ ] **Use `Enum` for a fixed set of states**, not string constants.
- [ ] **Annotate the boundaries, leave the internals loose.** Gradual typing.
- [ ] **Run mypy in CI** once you have a project. It is far cheaper to fix errors than to hunt
      them later.

---

## 15. Modern Python cheatsheet

| Version | Feature you should know about |
|---|---|
| **3.9** | Built-in generics (`list[str]`, `dict[str, int]`), `dict \|` merge, `functools.cache` |
| **3.10** | `match` statement (PEP 634), `X \| Y` unions at runtime (PEP 604) |
| **3.11** | `ExceptionGroup` and `except*` (PEP 654), `StrEnum`, `Self` type, a noticeably faster `asyncio` |
| **3.12** | Type parameter syntax (PEP 695): `class Box[T]`, f-string improvements (PEP 701 — nested quotes, backslashes, arbitrary expressions), improved error messages, the `type` statement |
| **3.13** | Experimental free-threaded build (PEP 703 — the GIL can be disabled), experimental JIT compiler, a new colourised interactive shell, `copy.replace()`, `warnings.deprecated()` |
| **3.14** | Deferred evaluation of annotations (PEP 649/749), template string literals — "t-strings" (PEP 750), multiple interpreters in the standard library (PEP 734), free-threaded mode officially supported (PEP 779), Zstandard compression in the standard library (PEP 784) |

Two notes on that table:

- **3.12's type parameter syntax** removes the old `TypeVar` dance. Instead of
  `T = TypeVar("T")` plus `class Box(Generic[T])`, you write `class Box[T]:` and use `T`
  directly.
- **3.13's free-threaded build** is the big one for the future of AI workloads: it lets Python run
  truly in parallel across CPU cores, which matters a lot for CPU-bound work. In 3.13 it is
  experimental and opt-in; in 3.14 it is officially supported but still opt-in.

---

## 🧪 Try it yourself

### Exercise 1 — Annotate a function and break it on purpose

Write `def repeat(text: str, times: int) -> str:` that returns `text` repeated `times`
times. Then call it with `repeat("ha", 3)` and with `repeat(5, 3)`. Run both. Then install
mypy and run it on the file — note that mypy finds the second mistake even though the
first call is fine.

<details>
<summary>Hint</summary>

`pip install mypy`, then `mypy your_file.py`.

</details>

<details>
<summary>Solution</summary>

```python
def repeat(text: str, times: int) -> str:
    return text * times


print(repeat("ha", 3))
print(repeat(5, 3))
```

```text
hahaha
15
```

The second call does **not** fail at runtime — `5 * 3` is perfectly valid, it just returns
`15` instead of a repeated string. That is the perfect illustration of what type hints
add: mypy catches that you meant a `str` here, even though Python itself does not care.

```text
repeat.py:6: error: Argument 1 to "repeat" has incompatible type "int"; expected "str"  [arg-type]
Found 1 error in 1 file (checked 1 source file)
```

</details>

### Exercise 2 — Turn a `dict` into a `TypedDict`

Define a `TypedDict` called `ToolSpec` with keys `name: str`, `description: str` and
`parameters: dict`. Write a function `summarise(spec: ToolSpec) -> str` that returns the
name and the number of parameters. Call it with a valid spec and then with one that has a
typo in a key.

<details>
<summary>Hint</summary>

`TypedDict` lives in `typing`. A `TypedDict` instance is just a normal dict at runtime.

</details>

<details>
<summary>Solution</summary>

```python
from typing import TypedDict


class ToolSpec(TypedDict):
    name: str
    description: str
    parameters: dict


def summarise(spec: ToolSpec) -> str:
    return f"{spec['name']} takes {len(spec['parameters'])} parameter(s)"


good: ToolSpec = {
    "name": "search",
    "description": "Search the web",
    "parameters": {"query": "string"},
}
print(summarise(good))

bad: ToolSpec = {
    "name": "search",
    "description": "Search the web",
    "paramters": {},
}
```

```text
search takes 1 parameter(s)
```

At runtime the last dictionary is accepted happily — `TypedDict` does not validate. mypy
is the one that complains:

```text
tools.py:21: error: Missing key "parameters" for TypedDict "ToolSpec"  [typeddict-item]
tools.py:21: error: Extra key "paramters" for TypedDict "ToolSpec"  [typeddict-unknown-key]
Found 2 errors in 1 file (checked 1 source file)
```

`[typeddict-item]` means a required key is missing; `[typeddict-unknown-key]` means you
spelled a key name wrong.

</details>

### Exercise 3 — Use the walrus operator twice

Write a loop over the string `"a=1, b=2, c=3"` that uses the walrus operator to pull out
each key and value, and prints them as `a -> 1`. Then write the same loop *without* the
walrus operator, using `dict()` instead, and check you get the same output.

<details>
<summary>Hint</summary>

`re.findall(r"(\w+)=(\w+)", text)` gives you a list of `(key, value)` tuples. The walrus
version assigns inside the `for` statement's condition.

</details>

<details>
<summary>Solution</summary>

```python
import re

text = "a=1, b=2, c=3"

# With the walrus operator
for match in re.finditer(r"(\w+)=(\w+)", text):
    if (key := match.group(1)):
        print(f"{key} -> {match.group(2)}")

# Without it
for key, value in re.findall(r"(\w+)=(\w+)", text):
    print(f"{key} -> {value}")
```

```text
a -> 1
b -> 2
c -> 3
a -> 1
b -> 2
c -> 3
```

The walrus version is not obviously better here — that is fine. Its real value is avoiding a
**second** lookup of the same expensive thing, as in the `re.search` example in the section above.

</details>

### Exercise 4 — A `Protocol` you can swap

Define a `Protocol` called `Embedder` with a method `embed(text: str) -> list[float]`.
Implement it twice: a `RealEmbedder` that returns a fake vector, and a `FakeEmbedder` that
returns a fixed one. Write `def cosine(a: Embedder, b: Embedder) -> float:` that uses
both.

<details>
<summary>Hint</summary>

A `Protocol` class body uses `...` (Ellipsis) for method bodies that have no implementation.

</details>

<details>
<summary>Solution</summary>

```python
from typing import Protocol


class Embedder(Protocol):
    def embed(self, text: str) -> list[float]: ...


class RealEmbedder:
    def embed(self, text: str) -> list[float]:
        return [float(len(text)), 1.0, 0.0]


class FakeEmbedder:
    def embed(self, text: str) -> list[float]:
        return [0.0, 1.0, 0.0]


def cosine(a: Embedder, b: Embedder) -> float:
    """Compare the first embedding of a and the first embedding of b."""
    va = a.embed("hello")
    vb = b.embed("hello")
    total = sum(x * y for x, y in zip(va, vb))
    return total


print(cosine(RealEmbedder(), RealEmbedder()))
print(cosine(RealEmbedder(), FakeEmbedder()))
```

```text
26.0
1.0
```

Neither `RealEmbedder` nor `FakeEmbedder` inherits from `Embedder`, and they do not need
to. That is the whole point of a `Protocol`.

</details>

### Exercise 5 — `Literal` catches a typo

Write `def set_mode(mode: Literal["fast", "accurate"]) -> str:` that returns a label. Call
it with `"fast"` and with `"fastt"`. Run it — no error. Then run mypy on it — one error.

<details>
<summary>Hint</summary>

`Literal` comes from `typing`. mypy compares the string against the allowed set exactly.

</details>

<details>
<summary>Solution</summary>

```python
from typing import Literal


def set_mode(mode: Literal["fast", "accurate"]) -> str:
    return "quick but rough" if mode == "fast" else "slower but precise"


print(set_mode("fast"))
print(set_mode("fastt"))
```

```text
quick but rough
slower but precise
```

Python does not care: any string is a string. mypy does:

```text
modes.py:9: error: Argument 1 to "set_mode" has incompatible type "Literal['fastt']"; expected "Literal['fast', 'accurate']"  [arg-type]
Found 1 error in 1 file (checked 1 source file)
```

</details>

### Exercise 6 — A dataclass with types, end to end

Write a `@dataclass` called `Chunk` with fields `index: int`, `text: str` and
`token_count: int = 0`. Write a function `split_text(text: str, size: int) -> list[Chunk]`
that splits a string into chunks and fills in `token_count` as the length of each chunk.
Print them.

<details>
<summary>Hint</summary>

`Chunk(index=0, text="hello")` — dataclasses take keyword arguments in field order.

</details>

<details>
<summary>Solution</summary>

```python
from dataclasses import dataclass


@dataclass
class Chunk:
    index: int
    text: str
    token_count: int = 0


def split_text(text: str, size: int) -> list[Chunk]:
    chunks = []
    for index, start in enumerate(range(0, len(text), size)):
        piece = text[start:start + size]
        chunks.append(Chunk(index=index, text=piece, token_count=len(piece)))
    return chunks


for chunk in split_text("RAG stands for retrieval augmented generation.", 12):
    print(chunk)
```

```text
Chunk(index=0, text='RAG stands f', token_count=12)
Chunk(index=1, text='or retrieval', token_count=12)
Chunk(index=2, text=' augmented g', token_count=12)
Chunk(index=3, text='eneration.', token_count=10)
```

</details>

---

## ✅ Checkpoint

**1. Are type hints enforced when your program runs?**

<details>
<summary>Answer</summary>

No. Python stores annotations but never checks them at runtime. They are enforced by
*static* type checkers such as mypy, before the program runs.

</details>

**2. What is the difference between `Optional[str]` and `str | None`?**

<details>
<summary>Answer</summary>

None — they describe the same type. Use `str | None` on Python 3.10+, and `Optional[str]`
only when you must support Python 3.9 or older.

</details>

**3. What does `Literal["fast", "accurate"]` do, and why is it better than `str`?**

<details>
<summary>Answer</summary>

It restricts the value to exactly those strings. With `str`, a typo like `"fastt"` is a
perfectly legal value that fails silently at runtime; with `Literal`, the type checker
rejects it.

</details>

**4. What does `cast(str, value)` actually do?**

<details>
<summary>Answer</summary>

It changes what the **type checker** believes, and nothing else. No conversion happens at
runtime. Use it when you know better than the checker, never to silence an error.

</details>

**5. What problem does `if TYPE_CHECKING:` solve?**

<details>
<summary>Answer</summary>

It lets you import a module only for type checkers, so a type-only import cannot create a
circular import at runtime.

</details>

**6. What does mypy's `[arg-type]` error mean?**

<details>
<summary>Answer</summary>

You passed an argument of the wrong type to a function — for example an `int` where a
`str` was declared.

</details>

**7. What is the difference between static typing and runtime validation?**

<details>
<summary>Answer</summary>

Static typing (mypy) checks your *code* against your annotations before the program runs;
it cannot see the actual data. Runtime validation (pydantic, manual checks) inspects the
real data that arrived — wrong values, missing fields, out-of-range numbers.

</details>

**8. What is the walrus operator `:=` for?**

<details>
<summary>Answer</summary>

It assigns a value **and** evaluates to it in one expression, so you can avoid a second
lookup or a duplicated call. The classic use is `while (line := handle.readline()):`.

</details>

**9. When should you use `assert`, and when should you use pydantic?**

<details>
<summary>Answer</summary>

`assert` for internal invariants in your own code (and never for user input — `python -O`
disables assertions). pydantic for data arriving from outside your program: API responses,
file contents, user input, LLM output.

</details>

**10. What does "gradual typing" mean in practice?**

<details>
<summary>Answer</summary>

Annotate the boundaries — public function signatures and data crossing a boundary — and
leave the internals loose. You do not need 100% coverage to get most of the benefit.

</details>

---

## 🐛 Common mistakes

| Mistake | What you see | Fix |
|---|---|---|
| Assuming annotations are checked at runtime | `greet(42)` runs happily and returns `"Hello, 42!"` | run mypy; annotations are a static contract |
| Annotating every local variable | noisy code, no extra safety | annotate signatures and boundaries only |
| `Optional[str]` on Python 3.10+ when you meant `str \| None` | works, but inconsistent with modern code | prefer `X \| None` on 3.10+ |
| Using `Literal` values as bare `str` | a typo sails through to runtime | `Literal["fast", "accurate"]` |
| Using `cast()` to silence an error | the error was right; you just hid it | fix the code, or annotate properly |
| Importing a type at runtime when it is only needed for an annotation | circular import at startup | `if TYPE_CHECKING:` or `from __future__ import annotations` |
| Using `dict[str, Any]` where `Any` swallows everything | no errors are reported inside that value | use a `TypedDict` or `dataclass` for a known shape |
| `assert` for validating user input | `python -O` removes the check and the bad data flows through | validate with pydantic or explicit `if`/`raise` |
| Forgetting `default_factory` in a dataclass | `ValueError: mutable default ... for field ...` | `field(default_factory=list)` |
| Confusing `TypedDict` with validation | a bad dict is accepted at runtime | `TypedDict` describes; pydantic validates |
| Leaving `reveal_type()` in committed code | mypy noise in everyone else's runs | it is a debugging tool; remove it |

---

## 🔗 Resources

- [Typing — Python Documentation](https://docs.python.org/3/library/typing.html) — the full
  reference for `Optional`, `Literal`, `Final`, `ClassVar`, `TypeAlias`, `Callable`,
  `Protocol`, `TypedDict` and `NewType`.
- [mypy documentation](https://mypy.readthedocs.io/en/stable/index.html) — the official docs for
  the checker, including the error-code list.
- [mypy error code list](https://mypy.readthedocs.io/en/stable/error_code_list.html) — every
  `[arg-type]`, `[assignment]` and `[list-item]` code, explained.
- [mypy common issues](https://mypy.readthedocs.io/en/stable/common_issues.html) — the problems
  people actually hit, and how to solve them.
- [PEP 484 — Type Hints](https://peps.python.org/pep-0484/) — the proposal that started all of
  this.
- [PEP 634 — Structural Pattern Matching](https://peps.python.org/pep-0634/) — the `match`
  statement, explained by its authors.
- [PEP 695 — Type Parameter Syntax](https://peps.python.org/pep-0695/) — the new generic syntax
  in Python 3.12.
- [PEP 703 — Making the GIL Optional](https://peps.python.org/pep-0703/) — what free-threaded
  Python means and why it matters for AI workloads.
- [What's New in Python 3.10](https://docs.python.org/3/whatsnew/3.10.html) ·
  [3.11](https://docs.python.org/3/whatsnew/3.11.html) ·
  [3.12](https://docs.python.org/3/whatsnew/3.12.html) ·
  [3.13](https://docs.python.org/3/whatsnew/3.13.html) ·
  [3.14](https://docs.python.org/3/whatsnew/3.14.html) — the release notes, one page per
  version.
- [pydantic documentation](https://docs.pydantic.dev/latest/) — the runtime validation library
  you will meet again in [17 Python for AI and data](17-python-for-ai-and-data.md).

---

## ➡️ Next

- [12 Environments and tooling](12-environments-and-tooling.md) — set up `venv`, `pyproject.toml`,
  `ruff` and `mypy` so your project installs and checks cleanly from day one.

**← Previous:** [10 Object-oriented programming](10-object-oriented-programming.md)
