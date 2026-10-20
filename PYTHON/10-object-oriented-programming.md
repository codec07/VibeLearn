# Object-Oriented Programming

So far you have written Python that does things: read a file, transform some data, print a
result. That style of programming is called **procedural** programming, and it works
beautifully right up until you have twenty different kinds of "thing" and each one needs
its own behaviour.

This file is about **classes**: a way to bundle data and the functions that operate on
that data into a single unit, so you can have many similar things without writing the same
code twenty times. By the end you will be able to write a class from scratch, use
inheritance and composition correctly, and replace most hand-written boilerplate with
`dataclass`.

> **⏱️ Time:** ~45 minutes
> **📚 Prereqs:** [09 File I/O and errors](09-file-io-and-errors.md)
> **🎯 By the end you can:** Design and write classes that bundle data with behaviour, and use
> `dataclass` to write them without boilerplate.

---

## Why this matters for AI engineering

Real AI codebases are full of objects. An `LLMClient` holds a provider, a model name and
an API key, and knows how to send a message. A `Tool` knows its name, its JSON schema and
how to run itself. An `Agent` holds a list of tools and a client, and knows how to loop:
ask the model, see if it wants a tool, run the tool, feed the result back.

Each of those is a **class**. They share behaviour, they are passed around as values, and
they are swapped for fake versions in tests. The moment your code has a "provider" that
can be OpenAI, Anthropic or a mock, you are writing object-oriented code whether you
planned to or not.

---

## 1. The plain-language motivation

Imagine you are building a chatbot and you need to store conversations. Without classes,
you end up with a pile of parallel lists:

```python
# The procedural version: fragile, easy to get out of sync.
user_names = []
user_messages = []
user_timestamps = []


def add_message(name, message):
    user_names.append(name)
    user_messages.append(message)
    user_timestamps.append(0)


add_message("Ada", "hello")
add_message("Grace", "hi there")
print(user_names)
print(user_messages)
```

```text
['Ada', 'Grace']
['hello', 'hi there']
```

Now somebody adds a "language" field and you have to edit the lists, the function, and every
place that reads them. Nothing ties a name to its message.

A **class** fixes that. It is a blueprint that says: "a thing like this has *these* pieces
of data, and knows *these* things to do with them."

```text
    a CLASS is a blueprint                an OBJECT is one thing built from it

    +---------------------+                +---------------------------+
    |  class Message      |                |  Message                  |
    |---------------------|                |---------------------------|
    |  data:              |  --builds-->   |  sender = "Ada"           |
    |    sender           |                |  content = "hello"        |
    |    content          |                |  timestamp = 0            |
    |    timestamp        |                |                           |
    |                     |                |  .preview()               |
    |  behaviour:         |                |  .is_from("ada")          |
    |    preview()        |                +---------------------------+
    |    is_from(who)     |
    +---------------------+
```

The blueprint is the **class**. Each thing built from it is an **instance** (or
**object**). The data attached to an instance is an **attribute**. The functions attached
to a class are **methods**.

---

## 2. Your first class

```python
class Dog:
    """A dog with a name and an age."""

    def __init__(self, name, age):
        self.name = name
        self.age = age

    def bark(self):
        return f"{self.name} says: Woof!"

    def birthday(self):
        self.age += 1
        return self.name


rex = Dog("Rex", 3)
print(rex.name, rex.age)
print(rex.bark())
print(rex.birthday(), "is now", rex.age)
```

```text
Rex 3
Rex says: Woof!
Rex is now 4
```

Let's name the parts:

| Piece | What it is |
|---|---|
| `class Dog:` | starts the class definition |
| `"""A dog with a name and an age."""` | the class **docstring** — what the class is for |
| `def __init__(self, name, age):` | the **constructor**: runs when you create an instance |
| `self.name = name` | sets an **instance attribute** — data attached to this particular dog |
| `def bark(self):` | a **method** — a function that belongs to the class |
| `rex = Dog("Rex", 3)` | creates an **instance** of `Dog` |

`__init__` is a **dunder** (double-underscore) method. Python calls it automatically when
you write `Dog("Rex", 3)`, and it sets up the object's data. Notice it never returns
anything — `__init__` must not have a `return` statement with a value.

---

## 3. `self` means "this particular object"

`self` is the single most confusing word for beginners, so here is the plainest possible
explanation: **`self` is the object the method was called on.**

When you write `rex.bark()`, Python passes `rex` in as `self`. That is the whole trick.
`self` is not magic, and it is not a keyword you have to memorise as a formula — it is
just the name of the first parameter, and you could call it anything (`this` is a common
alternative). Python's convention is `self`, so use it.

```python
class Counter:
    def __init__(self):
        self.value = 0

    def increment(self, amount=1):
        self.value += amount
        return self        # returning self lets you chain calls

    def __repr__(self):
        return f"Counter({self.value})"


counter = Counter()
counter.increment().increment(5)     # the first call returns self, so we can call again
print(counter)
print(counter.value)
```

```text
Counter(6)
6
```

`counter.increment()` returns `self` (the same `Counter`), so `.increment(5)` can be applied
directly to the result. Chaining like this only works when a method returns `self`.

### `__init__` versus `__new__`

You will only ever need `__init__`. `__new__` is the lower-level hook that decides *what
object to create*; `__init__` then *initialises* it. Ignore `__new__` unless a tutorial
specifically asks for it.

---

## 4. Instance attributes vs class attributes

An attribute defined inside `__init__` with `self.` is an **instance attribute**: every
object gets its own copy. An attribute defined directly in the class body is a **class
attribute**: there is exactly one copy, shared by every instance.

```python
class ModelRegistry:
    """Tracks which models a process has loaded."""

    default_model = "gpt-4o-mini"    # class attribute: ONE shared copy

    def __init__(self, name):
        self.name = name
        self.loaded_models = []      # instance attribute: one per object


registry_a = ModelRegistry("worker-a")
registry_b = ModelRegistry("worker-b")
registry_a.loaded_models.append("gpt-4o")

print("a:", registry_a.loaded_models)
print("b:", registry_b.loaded_models)           # unaffected
print("default:", ModelRegistry.default_model)  # shared, read-only in practice
```

```text
a: ['gpt-4o']
b: []
default: gpt-4o-mini
```

### The classic bug

Put a **mutable** value (a list or a dict) in the class body and every instance shares it.
This is the single most common object-oriented bug in Python:

```python
class Cache:
    items = {}          # BUG: one shared dict for every Cache

    def put(self, key, value):
        self.items[key] = value


first = Cache()
second = Cache()
first.put("answer", "42")

print("second sees:", second.items)   # {'answer': '42'} -- not what you wanted!
```

```text
second sees: {'answer': '42'}
```

`second` was never given anything, yet it can see `first`'s data. The fix is to move the
assignment into `__init__` so each instance creates its own:

```python
class Cache:
    def __init__(self):
        self.items = {}          # FIX: every Cache gets its own dict

    def put(self, key, value):
        self.items[key] = value


first = Cache()
second = Cache()
first.put("answer", "42")

print("second sees:", second.items)   # {}
```

```text
second sees: {}
```

**Rule: if the class attribute is a list, a dict, a set or any other mutable object, put it in
`__init__` instead.** Immutable values (strings, numbers, tuples) are fine as class
attributes.

---

## 5. Methods, arguments, and lists of objects

Once you have a class, you can pass instances to functions, return them, and store them in
lists and dictionaries exactly like any other value.

```python
class Message:
    def __init__(self, sender, content):
        self.sender = sender
        self.content = content

    def preview(self, width=20):
        text = self.content
        if len(text) > width:
            return text[:width] + "..."
        return text


def summarise(messages):
    """Print a one-line summary of a list of Message objects."""
    for message in messages:
        print(f"{message.sender}: {message.preview()}")


conversation = [
    Message("Ada", "Can we talk about retrieval augmented generation?"),
    Message("Grace", "Yes, let us start with the basics."),
]
summarise(conversation)

# Objects work as dictionary values too.
by_sender = {message.sender: message for message in conversation}
print(by_sender["Ada"].preview(10))
```

```text
Ada: Can we talk about re...
Grace: Yes, let us start wi...
Can we tal...
```

---

## 6. `__str__` and `__repr__`

Python has two special methods for turning an object into text.

- `__str__` — the *friendly* version. Used by `print()` and by `str()`.
- `__repr__` — the *technical* version. Used by `repr()`, and shown in the interactive console and
  inside containers like lists. It is meant to be unambiguous and, ideally, valid Python
  that would recreate the object.

```python
class Document:
    def __init__(self, title, pages):
        self.title = title
        self.pages = pages

    def __str__(self):
        return f"Document('{self.title}', {self.pages} pages)"

    def __repr__(self):
        return f"Document(title={self.title!r}, pages={self.pages})"


doc = Document("Attention Is All You Need", 15)

print(doc)                 # uses __str__
print(repr(doc))           # uses __repr__
print(f"{doc}")            # uses __str__
print(f"{doc!r}")          # uses __repr__
```

```text
Document('Attention Is All You Need', 15 pages)
Document(title='Attention Is All You Need', pages=15)
Document('Attention Is All You Need', 15 pages)
Document(title='Attention Is All You Need', pages=15)
```

The `!r` inside the f-string means "use `repr()` on this value". `repr()` adds quotes
around strings, which is why `title={self.title!r}` shows `'Attention Is All You Need'`
with quotes.

If you define only `__repr__`, `print()` will use it too. If you define only `__str__`,
`repr()` will fall back to the ugly default `<Document object at 0x7f...>`. **Defining
`__repr__` is almost always worth it.**

---

## 7. `__eq__` — value comparison

By default, two objects are equal only if they are *the same object*. Two separately created
`Document`s with identical contents are **not** equal.

```python
class Document:
    def __init__(self, title, pages):
        self.title = title
        self.pages = pages


left = Document("RAG", 10)
right = Document("RAG", 10)

print(left == right)      # False -- they are different objects
print(left is right)      # False
print(left == left)       # True -- the same object
```

```text
False
False
True
```

Defining `__eq__` changes that so objects are compared by *value*:

```python
class Document:
    def __init__(self, title, pages):
        self.title = title
        self.pages = pages

    def __eq__(self, other):
        if not isinstance(other, Document):
            return NotImplemented
        return (self.title, self.pages) == (other.title, other.pages)


left = Document("RAG", 10)
right = Document("RAG", 10)

print(left == right)               # True
print(left == "RAG")               # False
print(left in [right])             # True
```

```text
True
False
True
```

Returning `NotImplemented` for a wrong type is the correct thing to do: it tells Python "I
cannot compare myself to that", and Python then tries the other object's `__eq__`, and
finally falls back to identity. Do not return `False` directly — that breaks comparisons
in both directions.

---

## 8. `@property` — an attribute that is computed

A **property** lets you expose a method as if it were an attribute. The caller writes
`config.temperature`, and Python runs the getter behind the scenes.

The reason to do this: **validation**. If a value has rules, you can enforce them every
single time it is set, instead of hoping every caller remembers to check.

```python
class ModelConfig:
    def __init__(self, name, temperature):
        self.name = name
        self.temperature = temperature

    @property
    def temperature(self):
        """Read the value. Runs every time you access it."""
        return self._temperature

    @temperature.setter
    def temperature(self, value):
        """Validate and store the value. Runs every time you assign to it."""
        if not 0.0 <= value <= 2.0:
            raise ValueError(f"temperature must be between 0 and 2, got {value}")
        self._temperature = float(value)


config = ModelConfig("gpt-4o-mini", 0.7)
print(config.temperature)          # looks like a plain attribute read

config.temperature = 1.5
print(config.temperature)

try:
    config.temperature = 9
except ValueError as error:
    print("ValueError:", error)
```

```text
0.7
1.5
ValueError: temperature must be between 0 and 2, got 9
```

Notice the naming convention: the property is called `temperature`, and the real storage
is `self._temperature`. The single leading underscore is Python's way of saying "this is
internal — call the property instead". It is a convention, not enforcement.

---

## 9. `@staticmethod` and `@classmethod`

These are two special method decorators that change how the first argument works.

| Decorator | First argument | Use it for |
|---|---|---|
| plain method | `self` — the instance | behaviour that needs the object's data |
| `@classmethod` | `cls` — the class itself | alternative constructors, class-level factories |
| `@staticmethod` | none | a helper function that does not need the class or an instance |

```python
class LLMClient:
    DEFAULT_MODEL = "gpt-4o-mini"

    def __init__(self, api_key, model=DEFAULT_MODEL):
        self.api_key = api_key
        self.model = model

    @staticmethod
    def estimate_tokens(text):
        """A utility: it needs neither the instance nor the class."""
        return max(1, len(text) // 4)

    @classmethod
    def from_env(cls, env=None):
        """An alternative constructor: builds a client from a dictionary or environment."""
        import os
        source = env if env is not None else os.environ
        key = source.get("OPENAI_API_KEY")
        if not key:
            raise ValueError("OPENAI_API_KEY is not set")
        return cls(api_key=key)

    def chat(self, messages):
        return f"[{self.model}] {len(messages)} message(s)"


print(LLMClient.estimate_tokens("hello world, this is a test"))
print(LLMClient("sk-test").chat([{"role": "user", "content": "hi"}]))
print(LLMClient.from_env({"OPENAI_API_KEY": "sk-from-dict"}).model)
```

```text
6
[gpt-4o-mini] 1 message(s)
gpt-4o-mini
```

The difference in one line each:

- A **staticmethod** is really just a function that happens to live inside the class. Call it as
  `LLMClient.estimate_tokens(...)`. It cannot touch `self` or `cls`.
- A **classmethod** receives the class as `cls`, so it can build instances of *that* class. This is
  how `from_env` can return `cls(api_key=key)` and automatically stay correct if you later
  subclass `LLMClient`.

---

## 10. Inheritance

**Inheritance** means: "this new class is a special kind of that old class, and it gets
everything the old class had."

```python
class Tool:
    """Base class: every tool can be described and must be runnable."""

    def __init__(self, name):
        self.name = name

    def run(self, payload):
        raise NotImplementedError("subclasses must implement run()")

    def describe(self):
        return f"{self.name} -> {type(self).__name__}"


class EchoTool(Tool):
    def __init__(self, name, prefix="echo:"):
        super().__init__(name)      # call the parent's __init__ first
        self.prefix = prefix

    def run(self, payload):
        return self.prefix + payload


class UpperTool(Tool):
    def run(self, payload):
        return payload.upper()


tool = EchoTool("repeat", prefix=">> ")
print(tool.describe())
print(tool.run("hello"))
print(UpperTool("shout").run("hello"))
print(isinstance(tool, Tool), isinstance(tool, UpperTool))
print(issubclass(EchoTool, Tool))
```

```text
repeat -> EchoTool
>> hello
HELLO
True False
True
```

- `class EchoTool(Tool):` — `Tool` is the **base class** (or parent); `EchoTool` is the **subclass**
  (or child).
- `super().__init__(name)` — calls the parent's `__init__` so `self.name` gets set. **Always call
  it first** if the parent sets up data.
- **Overriding**: `EchoTool.run` replaces `Tool.run`. The subclass version wins.
- `isinstance(x, Tool)` — "is this object an instance of `Tool` (or a subclass)?" It returned
  `True` for `tool` even though `tool` is an `EchoTool`, because an `EchoTool` *is a*
  `Tool`.
- `issubclass(EchoTool, Tool)` — the same question about classes rather than objects.

`Tool.run` raising `NotImplementedError` is a common and good pattern: it documents that
every subclass must provide `run`, and it fails loudly if you forget.

---

## 11. The MRO and multiple inheritance

A class can inherit from more than one parent. Python then needs a rule for "which `who()`
do I call?" The answer is the **MRO** — the *method resolution order*.

```python
class A:
    def who(self):
        return "A"


class B(A):
    def who(self):
        return "B"


class C(A):
    def who(self):
        return "C"


class D(B, C):
    def who(self):
        return "D"


print(D.__mro__)
print(D().who())
print(super(D, D()).who())
```

```text
(<class '__main__.D'>, <class '__main__.B'>, <class '__main__.C'>, <class '__main__.A'>, <class 'object'>)
D
B
```

```text
    D.__mro__  (method resolution order)

    D  ->  B  ->  C  ->  A  ->  object
    ^      ^      ^      ^
    |      |      |      +-- every class eventually reaches object
    |      |      +-- C comes before A
    |      +-- B comes before C
    +-- D is looked at first

    super() means: "go to the NEXT class in this list"
```

`super()` does not mean "my parent". It means "the next class in the MRO after me". In the
example above, `D().who()` runs `D.who`, and `super(D, D()).who()` runs `B.who` — the next
one along.

That is why `super().__init__(name)` works correctly even with multiple inheritance: it
follows the same cooperative chain.

**Keep this brief in your head: multiple inheritance is powerful, easy to misuse, and most Python
code that needs it is better off using composition (next section) instead.** You now know
enough to read code that uses it.

---

## 12. Composition over inheritance

This is the most practical advice in this chapter, and it is the advice most professional
Python teams follow.

**Composition** means "the object *has* another object", rather than "the object *is a* kind of
another object". When in doubt, use composition.

```text
    INHERITANCE ("is a")                 COMPOSITION ("has a")

    class Agent(Tool):                  class Agent:
        ...                                  def __init__(self, tool):
                                             self.tool = tool

    An Agent IS A Tool.                 An Agent HAS A Tool.
    If Tool changes, Agent changes.      If Tool changes, Agent does not.
    Tightly coupled.                    Loosely coupled.
```

Here is the AI example. Compare an agent that *inherits* from a tool, with one that *has*
a tool:

```python
class SearchTool:
    """A tool that searches a tiny in-memory index."""

    def __init__(self, index):
        self.index = index

    def run(self, query):
        return [doc for doc in self.index if query.lower() in doc.lower()]


class Agent:
    """An agent HAS-A search tool. It is not a SearchTool."""

    def __init__(self, name, tools):
        self.name = name
        self.tools = tools        # a list of tool objects

    def run(self, query):
        results = []
        for tool in self.tools:
            results.extend(tool.run(query))
        return results


index = ["python is a language", "rust is fast", "python is popular"]
agent = Agent("researcher", [SearchTool(index)])
print(agent.run("python"))
```

```text
['python is a language', 'python is popular']
```

Why this is better:

1. **The agent can hold several tools.** With inheritance, `Agent` could only ever be *one* kind of
   tool.
2. **You can swap the tool at runtime** — a real `SearchTool` in production, a `FakeSearchTool` in
   a test, without changing the agent.
3. **Nothing breaks when the tool changes.** The agent only depends on the tool's `run()` method.

---

## 13. `dataclass` — classes without boilerplate

Most of what a simple class does is: store a fixed set of values, print them nicely, and
compare them by value. That is exactly what `@dataclass` generates for you.

```python
from dataclasses import dataclass, field


@dataclass
class ToolSpec:
    name: str
    description: str
    parameters: dict[str, object] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)


spec = ToolSpec("search", "Search the knowledge base")
print(spec)
print(spec.parameters)                 # a fresh empty dict, not a shared one
print(ToolSpec("calc", "Add two numbers"))
```

```text
ToolSpec(name='search', description='Search the knowledge base', parameters={}, tags=[])
{}
ToolSpec(name='calc', description='Add two numbers', parameters={}, tags=[])
```

Compare that with the hand-written version it replaces: about 20 lines of `__init__`,
`__repr__` and `__eq__` collapse into 4.

The `field()` function controls the details:

| Argument | What it does |
|---|---|
| `field(default=...)` | a default value |
| `field(default_factory=list)` | a default that is **built fresh for every instance** |
| `field(default_factory=dict)` | same, for a dict |
| `field(init=False)` | not part of the constructor |
| `field(repr=False)` | hidden from `print()` / `__repr__` |

**Always use `default_factory` for lists, dicts and sets.** A bare `= []` as a dataclass default
raises a `ValueError` at class-creation time precisely because Python protects you from the
shared-mutable-default bug.

### `frozen=True` and `slots=True`

```python
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ModelConfig:
    name: str
    temperature: float = 0.2
    stop: tuple[str, ...] = field(default=("END",))


config = ModelConfig("gpt-4o-mini")
print(config)
print(config.temperature)

try:
    config.temperature = 0.9
except Exception as error:
    print(type(error).__name__, ":", error)
```

```text
ModelConfig(name='gpt-4o-mini', temperature=0.2, stop=('END',))
0.2
FrozenInstanceError : cannot assign to field 'temperature'
```

- `frozen=True` makes the object **immutable** — you cannot change a field after creation. Trying
  raises `FrozenInstanceError` (a subclass of `AttributeError`). Immutable objects are safe
  to share and make good dictionary keys and cache keys.
- `slots=True` removes the per-instance `__dict__`, which saves memory. It is the dataclass
  equivalent of `__slots__` (covered in section 15).

---

## 14. `Enum` — named constants

A **string constant** scattered across your code is a bug waiting to happen. `"completed"`
and `"complete"` and `"COMPLETED"` are three different strings, and a typo is invisible
until runtime.

An **enum** (enumeration) gives you a fixed set of named values.

```python
from enum import Enum


class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


status = JobStatus.RUNNING
print(status)
print(status.value)
print(status == JobStatus.RUNNING)

# The bug a string constant would let through:
print("This is the bug:", status == "running")
```

```text
JobStatus.RUNNING
running
True
This is the bug: False
```

`JobStatus.RUNNING == "running"` is `False`, because an enum member is not a string. That
is a feature: it makes the mistake loud instead of silent.

If you *want* the enum members to behave like strings, use `StrEnum` (Python 3.11+):

```python
from enum import StrEnum


class JobStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


print(JobStatus.RUNNING == "running")     # True
print(f"status is {JobStatus.RUNNING}")    # status is running
```

```text
True
status is running
```

---

## 15. `__slots__` — memory saving

Every normal object carries a `__dict__` — a hidden dictionary holding its attributes.
That costs memory. Defining `__slots__` tells Python the attribute names up front, so no
`__dict__` is needed.

```python
import sys


class Record:
    def __init__(self, item_id):
        self.item_id = item_id


class SlottedRecord:
    __slots__ = ("item_id",)

    def __init__(self, item_id):
        self.item_id = item_id


plain = Record(1)
slotted = SlottedRecord(1)

print("plain instance :", sys.getsizeof(plain), "bytes")
print("plain __dict__ :", sys.getsizeof(plain.__dict__), "bytes")
print("slotted        :", sys.getsizeof(slotted), "bytes")
```

```text
plain instance : 48 bytes
plain __dict__ : 296 bytes
slotted        : 40 bytes
```

(The exact numbers depend on your Python version and platform, but the gap is real.) For a
handful of objects, who cares. For **100,000 records** loaded from a dataset, it is the
difference between a program that fits in memory and one that does not.

`__slots__` has one catch: you cannot add attributes that were not listed, and you cannot
have class attributes with the same name as a slot.

```python
class Point:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Point(x={self.x}, y={self.y})"


point = Point(1, 2)
print(point)

try:
    point.z = 3
except AttributeError as error:
    print("AttributeError:", error)
```

```text
Point(x=1, y=2)
AttributeError: 'Point' object has no attribute 'z' and no __dict__ for setting new attributes
```

In practice, `dataclass(slots=True)` gives you the same saving with one keyword argument.

---

## 16. `Protocol` — duck typing, with types

**Duck typing** is Python's philosophy: if an object has the methods you need, it is good enough,
no matter what class it is. A `Protocol` lets you *say that in a way a type checker
understands*.

```python
from typing import Protocol, runtime_checkable


@runtime_checkable
class SupportsChat(Protocol):
    """Anything with a chat() method of this shape can be used as a provider."""

    def chat(self, messages: list[dict]) -> str: ...


class RealProvider:
    def chat(self, messages: list[dict]) -> str:
        return f"real answer to {messages[0]['content']}"


class FakeProvider:
    def chat(self, messages: list[dict]) -> str:
        return "fake answer"


def ask(provider: SupportsChat, question: str) -> str:
    return provider.chat([{"role": "user", "content": question}])


print(ask(RealProvider(), "hello"))
print(ask(FakeProvider(), "hello"))
print(isinstance(RealProvider(), SupportsChat))
print(isinstance(42, SupportsChat))
```

```text
real answer to hello
fake answer
True
False
```

Note that `RealProvider` and `FakeProvider` do **not** inherit from `SupportsChat`. They
do not even know it exists. That is the whole point: a `Protocol` describes a *shape*, not
a
*heritage*. `@runtime_checkable` lets you use `isinstance` with it (it only checks that the methods
exist, not their types).

Full details on typing protocols live in
[11 Type hints and modern Python](11-type-hints-and-modern-python.md).

---

## 17. Do you need OOP?

Honest answer: **sometimes, and less often than you think.**

Plain functions plus `dataclass` records will carry you a very long way. That combination
is easier to test, easier to read, and easier to hand to another engineer. Many of the
largest Python codebases in the world — including a lot of AI tooling — are written that
way.

OOP earns its keep when you hit one of these:

| Situation | Why a class helps |
|---|---|
| Shared behaviour over shared data | many objects of the same kind need the same methods |
| You need to swap implementations | a `Provider` parameter can be the real API or a fake |
| You need polymorphism | one code path handles many concrete types |
| The object has real lifecycle | constructed, configured, used, closed |
| State that must stay consistent | the class can enforce the rules |

**Start with functions. Move to a dataclass when you need shared data. Move to a class when you
need shared behaviour.** That is a good order of escalation, and it means you never write an
inheritance tree you do not need.

---

## 18. Case study: an `LLMClient` and a `ToolRegistry`

Here is the pattern you will meet again and again. Two small classes, each with one job,
each swappable and testable.

```python
class FakeProvider:
    """Stands in for a real HTTP API so the example runs offline."""

    def send(self, payload):
        last = payload["messages"][-1]
        return f"[{payload['model']}] {last['role']} says: {last['content']}"


class LLMClient:
    """Sends chat requests to a model provider."""

    def __init__(self, provider, model, tools=None):
        self.provider = provider
        self.model = model
        self.tools = tools or []

    def chat(self, messages):
        payload = {
            "model": self.model,
            "messages": messages,
            "tools": self.tools,
        }
        return self.provider.send(payload)


client = LLMClient(FakeProvider(), "gpt-4o-mini")
print(client.chat([{"role": "user", "content": "Explain RAG in one sentence."}]))
```

```text
[gpt-4o-mini] user says: Explain RAG in one sentence.
```

Now the tool registry — a class that holds tools and hands them out by name:

```python
from dataclasses import dataclass
from typing import Callable


@dataclass
class Tool:
    name: str
    description: str
    func: Callable[..., str]

    def run(self, arguments):
        return str(self.func(**arguments))


class ToolRegistry:
    """Holds the tools an agent is allowed to call."""

    def __init__(self):
        self._tools = {}

    def register(self, tool):
        self._tools[tool.name] = tool

    def get(self, name):
        if name not in self._tools:
            raise KeyError(f"unknown tool: {name}")
        return self._tools[name]

    def specs(self):
        """The tool descriptions, in the shape an LLM API expects."""
        return [
            {"name": tool.name, "description": tool.description}
            for tool in self._tools.values()
        ]


def search(query):
    return f"3 results for {query!r}"


registry = ToolRegistry()
registry.register(Tool("search", "Search the web", search))

print(registry.specs())
print(registry.get("search").run({"query": "python"}))
```

```text
[{'name': 'search', 'description': 'Search the web'}]
3 results for 'python'
```

Look at what the classes bought you:

- `LLMClient` does not know how the provider works. Swapping `FakeProvider` for a real HTTP
  client changes one line.
- `ToolRegistry` owns the name → tool mapping, so the agent code never does dictionary juggling.
- `Tool` is a dataclass, so it prints nicely and compares by value.
- Everything is small, and every piece can be tested on its own.

That is what object-oriented design is *for*: not fewer lines, but fewer surprises.

---

## 19. The dunder methods cheat sheet

**Dunder** (short for "double underscore") methods are the special methods Python calls
implicitly. You never call them by name — you use the syntax they power.

| Dunder | Powers | Example |
|---|---|---|
| `__init__` | building the object | `Dog("Rex", 3)` |
| `__repr__` | debugging display | `repr(obj)` in the console |
| `__str__` | human-readable text | `print(obj)`, `f"{obj}"` |
| `__eq__` | value comparison | `a == b` |
| `__len__` | length | `len(obj)` |
| `__getitem__` | subscripting | `obj["key"]` |
| `__setitem__` | item assignment | `obj["key"] = value` |
| `__contains__` | membership test | `x in obj` |
| `__iter__` | iteration | `for x in obj` |
| `__call__` | making an object callable | `obj()` |
| `__enter__` / `__exit__` | the `with` statement | `with obj:` |
| `__bool__` | truthiness | `if obj:` |

Two you will meet very soon: `__enter__`/`__exit__` are what make `with open(...)` work, and
`__call__` is what makes a class instance usable like a function.

---

## 🧪 Try it yourself

### Exercise 1 — A `Document` class with the good bits

Write a class `Document` with `title` and `pages`. Give it:
- an `__init__`,
- an `__repr__` that shows `Document(title='...', pages=N)`,
- an `__eq__` that compares by value,
- a method `is_long()` that returns `True` when `pages` is more than 100.

<details>
<summary>Hint</summary>

`__eq__` should return `NotImplemented` when `other` is not a `Document`.

</details>

<details>
<summary>Solution</summary>

```python
class Document:
    def __init__(self, title, pages):
        self.title = title
        self.pages = pages

    def __repr__(self):
        return f"Document(title={self.title!r}, pages={self.pages})"

    def __eq__(self, other):
        if not isinstance(other, Document):
            return NotImplemented
        return (self.title, self.pages) == (other.title, other.pages)

    def is_long(self):
        return self.pages > 100


a = Document("Attention Is All You Need", 15)
b = Document("Attention Is All You Need", 15)
print(a)
print(a == b)
print(a.is_long(), Document("A Long Paper", 200).is_long())
```

```text
Document(title='Attention Is All You Need', pages=15)
True
False True
```

</details>

### Exercise 2 — A class attribute that bites

Write a class `Registry` with a class attribute `items = []` and a method `add(name)`.
Create two instances, add to the first, and print `second.items`. Then fix the class so
each instance has its own list.

<details>
<summary>Hint</summary>

The fix is to move `items = []` out of the class body and into `__init__` as `self.items =
[]`.

</details>

<details>
<summary>Solution</summary>

```python
class Registry:
    items = []          # the bug: one shared list

    def add(self, name):
        self.items.append(name)


first = Registry()
second = Registry()
first.add("gpt-4o")
print("shared bug:", second.items)


class Registry:
    def __init__(self):
        self.items = []      # the fix: one list per instance

    def add(self, name):
        self.items.append(name)


first = Registry()
second = Registry()
first.add("gpt-4o")
print("fixed:", second.items)
```

```text
shared bug: ['gpt-4o']
fixed: []
```

</details>

### Exercise 3 — A validating property

Write a class `Price` that stores `amount` and `currency`. Use a property so that
assigning a negative amount raises `ValueError`, and the currency must be one of `"usd"`,
`"eur"`, `"gbp"`.

<details>
<summary>Hint</summary>

Follow the `ModelConfig` example: a getter returning `self._amount` and a setter that
validates before storing.

</details>

<details>
<summary>Solution</summary>

```python
class Price:
    ALLOWED = ("usd", "eur", "gbp")

    def __init__(self, amount, currency):
        self.amount = amount
        self.currency = currency

    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, value):
        if value < 0:
            raise ValueError(f"amount cannot be negative, got {value}")
        self._amount = float(value)

    @property
    def currency(self):
        return self._currency

    @currency.setter
    def currency(self, value):
        if value.lower() not in self.ALLOWED:
            raise ValueError(f"unsupported currency: {value}")
        self._currency = value.lower()


price = Price(19.99, "USD")
print(price.amount, price.currency)

try:
    price.amount = -5
except ValueError as error:
    print("ValueError:", error)

try:
    price.currency = "XYZ"
except ValueError as error:
    print("ValueError:", error)
```

```text
19.99 usd
ValueError: amount cannot be negative, got -5
ValueError: unsupported currency: XYZ
```

</details>

### Exercise 4 — Turn a class into a dataclass

Rewrite this class as a `@dataclass`, keeping the same behaviour, and give the dataclass a
`default_factory` list field.

```python
class Prompt:
    def __init__(self, name, template, examples=None):
        self.name = name
        self.template = template
        self.examples = examples if examples is not None else []

    def render(self, value):
        return self.template.format(value=value)


demo = Prompt("summarise", "Summarise: {value}")
print(demo.render("a long document"))
```

```text
Summarise: a long document
```

<details>
<summary>Hint</summary>

`field(default_factory=list)` replaces the `examples if examples is not None else []` trick.

</details>

<details>
<summary>Solution</summary>

```python
from dataclasses import dataclass, field


@dataclass
class Prompt:
    name: str
    template: str
    examples: list[str] = field(default_factory=list)

    def render(self, value):
        return self.template.format(value=value)


one = Prompt("summarise", "Summarise: {value}")
two = Prompt("translate", "Translate: {value}")

print(one)
print(one.render("a long document"))
print(one.examples, two.examples)
one.examples.append("an example")
print(one.examples, two.examples)
```

```text
Prompt(name='summarise', template='Summarise: {value}', examples=[])
Summarise: a long document
[] []
['an example'] []
```

The last line shows why `default_factory` matters: the two prompts have **separate** lists.

</details>

### Exercise 5 — A tool registry with inheritance

Define a base class `Tool` with `name`, `description` and a `run` method that raises
`NotImplementedError`. Then define `EchoTool(Tool)` that returns the input, and
`ShoutTool(Tool)` that upper-cases it. Register both in a dict and call them by name.

<details>
<summary>Hint</summary>

Use `super().__init__(name, description)` in each subclass's `__init__`.

</details>

<details>
<summary>Solution</summary>

```python
class Tool:
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def run(self, payload):
        raise NotImplementedError("subclasses must implement run()")


class EchoTool(Tool):
    def __init__(self, name="echo", description="Returns the input"):
        super().__init__(name, description)

    def run(self, payload):
        return payload


class ShoutTool(Tool):
    def __init__(self, name="shout", description="Shouts the input"):
        super().__init__(name, description)

    def run(self, payload):
        return payload.upper()


tools = {tool.name: tool for tool in [EchoTool(), ShoutTool()]}
print(tools["echo"].run("hello"))
print(tools["shout"].run("hello"))

try:
    Tool("raw", "does nothing").run("x")
except NotImplementedError as error:
    print("NotImplementedError:", error)
```

```text
hello
HELLO
NotImplementedError: subclasses must implement run()
```

</details>

### Exercise 6 — Replace a string constant with an `Enum`

You have a pipeline whose job status is tracked as the strings `"pending"`, `"running"`
and `"done"`. Define a `JobStatus` enum, then write a function `label(status)` that maps
each status to a human label. Show that comparing an enum member to the raw string is
`False`.

<details>
<summary>Hint</summary>

`match`/`if` on the enum members works, or use a dictionary keyed by the enum.

</details>

<details>
<summary>Solution</summary>

```python
from enum import Enum


class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"


LABELS = {
    JobStatus.PENDING: "waiting to start",
    JobStatus.RUNNING: "in progress",
    JobStatus.DONE: "finished",
}


def label(status):
    return LABELS.get(status, "unknown")


for status in JobStatus:
    print(f"{status.value:>8} -> {label(status)}")

print("string comparison:", JobStatus.RUNNING == "running")
```

```text
 pending -> waiting to start
 running -> in progress
    done -> finished
string comparison: False
```

</details>

---

## ✅ Checkpoint

**1. In `def bark(self)`, what does `self` refer to?**

<details>
<summary>Answer</summary>

The particular object the method was called on. When you write `rex.bark()`, Python passes
`rex` as `self`. It is simply the name of the first parameter.

</details>

**2. What is the difference between an instance attribute and a class attribute?**

<details>
<summary>Answer</summary>

An instance attribute is set with `self.x = ...` inside a method and exists separately on
every object. A class attribute is defined directly in the class body and there is exactly
one shared copy of it.

</details>

**3. What bug happens if you put `items = {}` in the class body instead of in `__init__`?**

<details>
<summary>Answer</summary>

Every instance shares the same dict, so one object can see (and corrupt) another's data.
Fix it by creating the dict per instance in `__init__`.

</details>

**4. What is the difference between `__str__` and `__repr__`?**

<details>
<summary>Answer</summary>

`__str__` is the friendly version used by `print()` and `str()`. `__repr__` is the
technical, unambiguous version used by `repr()`, the interactive console and containers.
In an f-string, `!r` forces `__repr__`.

</details>

**5. Why do you have to define `__eq__` to compare two objects by value?**

<details>
<summary>Answer</summary>

By default Python compares objects by identity — "are these the same object?". `__eq__`
lets you define what "equal" means for your data.

</details>

**6. What does `@property` buy you over a plain method?**

<details>
<summary>Answer</summary>

It lets callers use attribute syntax (`config.temperature`) while you keep full control —
most importantly, validation in the setter, so an invalid value can never be stored.

</details>

**7. When would you use a `@classmethod` instead of a `@staticmethod`?**

<details>
<summary>Answer</summary>

When the method needs the class itself, usually to build an instance — an alternative
constructor like `from_env`. A `@staticmethod` needs neither the class nor an instance.

</details>

**8. What does `super().__init__(name)` do, and why call it first?**

<details>
<summary>Answer</summary>

It calls the parent class's `__init__` so the parent's data is set up. Calling it first
means the subclass's own attributes are added on top of a fully initialised base.

</details>

**9. What does the MRO decide?**

<details>
<summary>Answer</summary>

The order in which Python looks for a method when a class inherits from several parents.
`super()` walks to the next class in that order.

</details>

**10. Why is composition usually better than inheritance?**

<details>
<summary>Answer</summary>

Composition ("has a") keeps the parts loosely coupled, lets one object hold several of
another kind, and lets you swap implementations (a real provider versus a fake) at
runtime. Inheritance ("is a") ties the two together permanently.

</details>

**11. What do `frozen=True` and `slots=True` do in a `@dataclass`?**

<details>
<summary>Answer</summary>

`frozen=True` makes the instance immutable — assigning to a field raises
`FrozenInstanceError`. `slots=True` removes the per-instance `__dict__`, which saves
memory.

</details>

---

## 🐛 Common mistakes

| Mistake | What you see | Fix |
|---|---|---|
| Forgetting `self` on an attribute (`self.name` written as `name`) | `NameError: name 'name' is not defined` | always prefix instance data with `self.` |
| Forgetting `self` as the first parameter of a method | `TypeError: bark() takes 1 positional argument but 2 were given` | `def bark(self):` |
| Calling `__init__` yourself after creating an object | the object is re-initialised and any state is wiped | let `Dog("Rex", 3)` do it |
| A mutable class attribute (`items = {}` in the class body) | one instance sees another instance's data | move it into `__init__` |
| `__init__` returning a value | `TypeError: __init__() should return None` | `__init__` sets up, it does not return |
| Writing `self.temperature = ...` inside a `@property` setter | infinite recursion | store in a different name, e.g. `self._temperature` |
| Using `self` in a `@staticmethod` | `NameError: name 'self' is not defined` | a staticmethod takes no first argument |
| Forgetting `super().__init__(...)` in a subclass | `AttributeError: 'EchoTool' object has no attribute 'name'` | call `super().__init__(...)` first |
| Comparing objects with `==` and expecting value equality | `False` for two identical-looking objects | define `__eq__` |
| Sharing one `list` as a default argument (`def f(items=[])`) | the list grows across calls and never resets | use `None` as the default, or `field(default_factory=list)` |
| Using inheritance where composition belongs | an agent that can only ever be one kind of tool | give the object the thing it needs as an attribute |
| Adding an attribute not listed in `__slots__` | `AttributeError: 'Point' object has no attribute 'z'` | list every attribute in `__slots__`, or use `dataclass(slots=True)` |

---

## 🔗 Resources

- [Classes — Python Tutorial](https://docs.python.org/3/tutorial/classes.html) — the official
  introduction to classes, inheritance and method resolution.
- [Python Data Model](https://docs.python.org/3/reference/datamodel.html) — the reference for every
  dunder method, including `__slots__`.
- [dataclasses — Dataclasses](https://docs.python.org/3/library/dataclasses.html) — `field()`,
  `default_factory`, `frozen`, `slots`, `InitVar` and inheritance rules.
- [Enum — How to support enumerated types](https://docs.python.org/3/library/enum.html) — `Enum`,
  `IntEnum`, `StrEnum` and when to use each.
- [typing.Protocol](https://docs.python.org/3/library/typing.html#typing.Protocol) — structural
  typing: define an interface without inheritance.
- [abc — Abstract Base Classes](https://docs.python.org/3/library/abc.html) — the other way to
  define a base class: one that cannot be instantiated on its own.
- [collections.abc — Abstract Base Classes for Containers](https://docs.python.org/3/library/collections.abc.html)
  — read-only versions of `list`, `dict` and `set` used for typing.
- [Descriptor HowTo](https://docs.python.org/3/howto/descriptor.html) — how Python actually
  implements properties, methods and class attributes.
- [types — Dynamic type creation](https://docs.python.org/3/library/types.html) — how `type()` and
  `namedtuple` work under the hood.
- [Python 3.12+ typing documentation](https://docs.python.org/3/library/typing.html) — the full
  reference for `Protocol`, `Callable`, `TypeVar` and the rest of the typing toolbox.

---

## ➡️ Next

- [11 Type hints and modern Python](11-type-hints-and-modern-python.md) — annotate your code so a
  type checker can find bugs before you run it.

**← Previous:** [09 File I/O and errors](09-file-io-and-errors.md)
