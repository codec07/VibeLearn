# Functions

A **function** is a named, reusable block of code. You define it once and call it as many
times as you like, passing it different data each time. Functions are how you stop writing
the same six lines in twelve places, how you give a piece of logic a name people can
understand, and how you make code testable. In AI systems, almost everything is a function:
a tool you call, a prompt you render, a chunk you split, a message you validate.

> **⏱️ Time:** ~40 minutes
> **📚 Prereqs:** [04 — Control flow](04-control-flow.md)
> **🎯 By the end you can:** define functions with flexible parameters, return values
> correctly, reason about where names live in memory, and write closures, higher-order
> functions and recursive algorithms.

---

## Why this matters for AI engineering

An agent is a loop of function calls: `plan()`, `select_tool()`, `call_tool()`,
`summarise()`. A pipeline is a row of transformation functions. A good AI codebase is
mostly small functions with clear names, clear inputs, and clear outputs — because that is
what makes a pipeline testable, a tool mockable, and a bug findable.

The single most important habit this file gives you is the `return` habit: a function that
*returns* a value can be checked, stored, logged, cached and asserted on. A function that
*prints* can do none of those things, and turning prints back into returns is a refactor
you will do many times in your career.

---

## Why functions exist

Four reasons, in the order you will notice them.

1. **Reuse.** Write the token-counting logic once; call it from every place that needs it.
2. **Naming.** `def calculate_token_cost(tokens, price_per_token):` says more in one line
   than twenty lines of inline arithmetic ever will.
3. **Testing.** You can call a function with known inputs and check the output. You cannot
   test a print statement without capturing stdout.
4. **Abstraction.** Once `chunk_text()` exists and works, you can forget how it works.
   That is the whole point of a *function* — it is a thing that hides detail.

---

## Defining and calling a function

You define a function with `def`, give it a name, list its **parameters** in parentheses,
end the header with a colon, and indent the body.

```python
def greet(name):
    """Return a greeting for name."""
    return f"Hello, {name}!"


print(greet("Ada"))
print(greet("Grace"))
```

```text
Hello, Ada!
Hello, Grace!
```

The pieces:

| Part | Name | Meaning |
|---|---|---|
| `def` | keyword | starts a function definition |
| `greet` | function name | how you call it |
| `name` | parameter | a name in the definition |
| `"Ada"` | argument | the actual value you pass in |
| `return` | keyword | sends a value back to the caller |

A **parameter** is the placeholder in the definition. An **argument** is the value you
actually pass. People say "parameter" and "argument" interchangeably; the distinction above
is the precise one.

### `return` ends the function immediately

Nothing after a `return` in the same block runs.

```python
def classify(number):
    if number < 0:
        return "negative"
    return "non-negative"      # <- this line is only reached if number >= 0


print(classify(-5))
print(classify(0))
print(classify(12))
```

```text
negative
non-negative
non-negative
```

### A function with no `return` returns `None`

```python
def shout(text):
    print(text.upper())


result = shout("hello")
print("the function returned:", result)
print("is it None?", result is None)
```

```text
HELLO
the function returned: None
is it None? True
```

---

## `return` versus `print`

This is the most important distinction in the file.

- `print()` writes text to the screen. It is for **showing** a human something.
- `return` hands a value back to whoever called the function. It is for **computing**.

A function that returns is testable. A function that prints is not, without extra work.

```python
# Hard to test: the answer is on the screen, not in your hands.
def add_prices_print(a, b):
    print(a + b)


# Easy to test: the answer is a value.
def add_prices(a, b):
    return a + b


print(add_prices(19.99, 5.00))

# With a return, you can assert, store and reuse.
total = add_prices(19.99, 5.00)
print("total is", total)
print("twice the total is", add_prices(total, total))
```

```text
24.99
total is 24.99
twice the total is 49.98
```

The rule to follow: **functions compute and return; the top level of your program prints.**
This is how you keep the "showing" part in one place, so the logic underneath can be reused
by a test, a web endpoint, a background job, or another function.

```python
def estimate_cost(prompt_tokens, completion_tokens, price_per_1k=0.0005):
    """Return the dollar cost of one API call."""
    return (prompt_tokens + completion_tokens) / 1000 * price_per_1k


cost = estimate_cost(prompt_tokens=1500, completion_tokens=800)
print(f"Estimated cost: ${cost:.4f}")
print(f"Cost of 10 calls: ${estimate_cost(1500, 800) * 10:.4f}")
```

```text
Estimated cost: $0.0011
Cost of 10 calls: $0.0115
```

---

## Parameters: positional, default, and keyword

Python gives you three ways to pass arguments.

### Positional arguments

The simplest: values are matched to parameters in order.

```python
def create_user(name, email, role="member"):
    return {"name": name, "email": email, "role": role}


print(create_user("Ada", "ada@example.com"))
```

### Default arguments

A parameter with a default value can be omitted. The default is used when it is missing.

```python
def create_user(name, email, role="member"):
    return {"name": name, "email": email, "role": role}


print(create_user("Ada", "ada@example.com"))
print(create_user("Ada", "ada@example.com", role="admin"))
```

```text
{'name': 'Ada', 'email': 'ada@example.com', 'role': 'member'}
{'name': 'Ada', 'email': 'ada@example.com', 'role': 'admin'}
```

### Keyword arguments

You can name the argument explicitly, in any order. This is the most readable form and you
should prefer it whenever a call has more than one argument.

```python
def create_user(name, email, role="member"):
    return {"name": name, "email": email, "role": role}


print(create_user(role="admin", email="ada@example.com", name="Ada"))
```

```text
{'name': 'Ada', 'email': 'ada@example.com', 'role': 'admin'}
```

### The order rule

**Parameters with defaults must come after parameters without defaults.** Otherwise Python
cannot tell which value belongs to which parameter.

```python
# This is a SyntaxError:
# def create_user(name="Ada", email):  ...
```

The reason is that positional arguments fill parameters left to right. If a defaulted
parameter came first, a positional argument would be ambiguous.

```python
def create_user(name, email, role="member", active=True):
    return {"name": name, "email": email, "role": role, "active": active}


print(create_user("Ada", "ada@example.com"))
print(create_user("Ada", "ada@example.com", "admin", False))
print(create_user("Ada", "ada@example.com", active=False))
```

```text
{'name': 'Ada', 'email': 'ada@example.com', 'role': 'member', 'active': True}
{'name': 'Ada', 'email': 'ada@example.com', 'role': 'admin', 'active': False}
{'name': 'Ada', 'email': 'ada@example.com', 'role': 'member', 'active': False}
```

---

## The mutable default argument trap

This is the classic Python bug. It is on nearly every interview, and it has shipped into
real production code at every company that uses Python. Read this section twice.

When you define a function, the default value is evaluated **once, at definition time** — not
once per call. If that default is a mutable object (a list, a dict, a set), every call that
uses the default shares the *same* object, and it keeps growing forever.

```python
def collect(item, bucket=[]):     # BUG: the default list is created once, here
    bucket.append(item)
    return bucket


print("first call :", collect("a"))
print("second call:", collect("b"))
print("third call :", collect("c"))
```

```text
first call : ['a']
second call: ['a', 'b']
third call : ['a', 'b', 'c']
```

The second call should have returned `['b']`. It returned `['a', 'b']` because the default
`[]` was created when the `def` line ran, and both calls appended to it.

### Why it happens

Python evaluates the `def` statement's default values **once**, when the function is
defined, and stores the resulting objects in the function. The default is not re-created
per call.

```text
Python starts, reads the def line
        |
        v
bucket = []          <-- ONE list object is created here, at definition time
        |
        v
def collect(item, bucket=<that list>)
        |
        +--> call 1: bucket is <that list>, append "a"  ->  ['a']
        +--> call 2: bucket is <that list>, append "b"  ->  ['a', 'b']
        +--> call 3: bucket is <that list>, append "c"  ->  ['a', 'b', 'c']
```

Every call that *omits* the argument gets that same list.

### The fix: use `None` as a sentinel

`None` means "no value was supplied", and you create a fresh object inside the function body
on each call.

```python
def collect(item, bucket=None):
    if bucket is None:          # a fresh list on every call
        bucket = []
    bucket.append(item)
    return bucket


print("first call :", collect("a"))
print("second call:", collect("b"))
print("third call :", collect("c"))
```

```text
first call : ['a']
second call: ['b']
third call : ['c']
```

**Never use a mutable value (`[]`, `{}`, `set()`) as a default argument.** Use `None` and
create the object inside the function. This one rule will save you hours.

Note that the *fix* creates a new list on every call, which means callers who pass their own
list still get that list modified — which is usually what you want:

```python
def collect(item, bucket=None):
    if bucket is None:
        bucket = []
    bucket.append(item)
    return bucket


my_bucket = ["existing"]
print(collect("new", my_bucket))   # ['existing', 'new']
print(my_bucket)                   # ['existing', 'new']  <- the caller's list was changed
```

---

## `*args` and `**kwargs`

Sometimes you do not know in advance how many arguments you will get — a wrapper around an
API, a logging decorator, a tool that forwards arbitrary parameters.

- `*args` collects extra **positional** arguments into a **tuple**.
- `**kwargs` collects extra **keyword** arguments into a **dict**.

```python
def log_call(name, *args, **kwargs):
    print("function:", name)
    print("positional extras:", args)
    print("keyword extras:", kwargs)


log_call("search", "retrieval", "reranker", top_k=5, threshold=0.72)
log_call("ping")
```

```text
function: search
positional extras: ('retrieval', 'reranker')
keyword extras: {'top_k': 5, 'threshold': 0.72}
function: ping
positional extras: ()
keyword extras: {}
```

`args` and `kwargs` are **conventions**, not keywords. You could name them `*things` and
`**options` and Python would behave identically. Use the conventional names so other people
read your code faster.

### `*` and `**` when *calling* a function

The same symbols do the opposite job at the call site: they **unpack** a collection into
separate arguments.

```python
def send_request(url, method, timeout, retries):
    return f"{method} {url} (timeout={timeout}, retries={retries})"


args = ["https://api.openai.com/v1/chat/completions", "POST"]
kwargs = {"timeout": 30, "retries": 3}

print(send_request(*args, **kwargs))
```

```text
POST https://api.openai.com/v1/chat/completions (timeout=30, retries=3)
```

`send_request(*args, **kwargs)` is how you write a function that forwards everything it was
given, unchanged. This pattern shows up in every decorator and every API-client wrapper you
will ever write.

---

## Keyword-only and positional-only parameters

Two extra markers let you lock down how a function may be called.

### Keyword-only parameters (`*`)

A bare `*` after the parameter list means "everything after this point must be passed by
name".

```python
def create_user(name, email, *, role="member", send_welcome_email=False):
    return {
        "name": name,
        "email": email,
        "role": role,
        "send_welcome_email": send_welcome_email,
    }


print(create_user("Ada", "ada@example.com", role="admin"))
```

```python
def create_user(name, email, *, role="member", send_welcome_email=False):
    return {
        "name": name,
        "email": email,
        "role": role,
        "send_welcome_email": send_welcome_email,
    }


print(create_user("Ada", "ada@example.com", role="admin"))

try:
    create_user("Ada", "ada@example.com", "admin")
except TypeError as error:
    print("TypeError:", error)
```

```text
{'name': 'Ada', 'email': 'ada@example.com', 'role': 'admin', 'send_welcome_email': False}
TypeError: create_user() takes 2 positional arguments but 3 were given
```

This is great for flags: it makes `create_user("Ada", "ada@example.com", "admin")` a loud
error instead of a silent bug where `"admin"` lands in the wrong slot.

### Positional-only parameters (`/`)

A `/` before the parameter list means "everything after this point must be passed
positionally". This is less common, but it is how you protect a parameter whose name you
might want to change later without breaking callers.

```python
def render(template, /, *, strict=False):
    return f"{template} (strict={strict})"


print(render("Hello", strict=True))
```

```python
def render(template, /, *, strict=False):
    return f"{template} (strict={strict})"


print(render("Hello", strict=True))

try:
    render(template="Hello")
except TypeError as error:
    print("TypeError:", error)
```

```text
Hello (strict=True)
TypeError: render() got some positional-only arguments passed as keyword arguments: 'template'
```

Both markers are worth knowing, but you will use keyword-only (`*`) far more often than
positional-only (`/`).

---

## Returning multiple values

Python lets a function return several values at once by separating them with commas. Under
the hood it returns a **tuple** — an immutable, ordered collection.

```python
def summarize(text):
    words = text.split()
    return len(words), len(text), max(words, key=len)


count, characters, longest = summarize("the quick brown fox jumps")

print("word count :", count)
print("characters :", characters)
print("longest    :", longest)
```

```text
word count : 5
characters : 25
longest    : quick
```

The right-hand side of the assignment is a **tuple**, and the left-hand side unpacks it. If
the counts do not line up, you get a `ValueError` at once.

```python
try:
    a, b = (1, 2, 3)
except ValueError as error:
    print("ValueError:", error)
```

```text
ValueError: too many values to unpack (expected 2)
```

You can also index a returned tuple like any other tuple, or ignore parts of it with `_`:

```python
def parse_response(raw):
    return 200, "ok", {"tokens": 42}


status, message, meta = parse_response("...")
print(status, message, meta["tokens"])

status_code, _, _ = parse_response("...")
print("only the status:", status_code)
```

```text
200 ok 42
only the status: 200
```

---

## Scope: where names live

**Scope** is the region of a program where a name is visible. Python's rule is called
**LEGB**, and it is worth learning as four words:

| Letter | Meaning | Example |
|---|---|---|
| **L** | **Local** — inside the current function | a variable you assign in this function |
| **E** | **Enclosing** — inside the function that *contains* this one | a variable in an outer function |
| **G** | **Global** — at the top level of the module | a constant defined outside any function |
| **B** | **Built-in** — Python's own names | `print`, `len`, `str` |

When Python sees a name, it looks for it in those four places, **in that order**, and uses
the first one it finds.

```python
model_name = "gpt-4o-mini"          # G — global


def configure():
    model_name = "local-model"        # L — local, a different variable entirely
    temperature = 0.7                 # L — local
    return f"{model_name} @ temp={temperature}"


def show_global():
    return model_name                 # G — no local, so the global is used


print(configure())
print(show_global())
print("global is still:", model_name)
```

```text
local-model @ temp=0.7
gpt-4o-mini
global is still: gpt-4o-mini
```

The critical detail: assigning to a name inside a function creates a **new, local**
variable. It does not touch the global of the same name. Functions that read a global are
fine; functions that *write* to one are where the trouble starts.

### Why globals are a trap

```python
# The classic global counter — and the classic global bug.
counter = 0


def increment():
    global counter
    counter += 1


def decrement():
    global counter
    counter -= 1


increment()
increment()
print("after 2 increments:", counter)
decrement()
print("after 1 decrement:", counter)
```

It works, but it has three problems. The function cannot be called twice in parallel without
the two calls fighting over the same variable. It cannot be tested without carefully saving
and restoring the global. And any other code in the program can change it by accident.

The fix is to return the new value and let the caller decide:

```python
def increment(counter):
    return counter + 1


counter = 0
counter = increment(counter)
counter = increment(counter)
print("after 2 increments:", counter)
```

```text
after 2 increments: 2
```

Now the function is pure: same input, same output, no hidden state. That is worth a
paragraph in any code review.

**Treat globals as read-only constants.** `MAX_RETRIES = 3` at the top of a module is
perfectly good practice. A global that changes during the program is a design smell.

---

## `global` and `nonlocal`

- `global` tells Python to use the module-level variable of that name, not a local one.
- `nonlocal` tells Python to use the variable from the **enclosing function** scope, not
  the global and not a new local.

`global` is used when you genuinely need a module-level state, such as a lazily-created
cache. `nonlocal` is used when an inner function needs to update a counter in the function
that created it.

```python
def make_counter():
    count = 0                 # lives in make_counter's scope

    def increment():
        nonlocal count         # use make_counter's count, not a new local
        count += 1
        return count

    def reset():
        nonlocal count
        count = 0

    return increment, reset


increment, reset = make_counter()

print(increment())   # 1
print(increment())   # 2
print(increment())   # 3
reset()
print(increment())   # 1 again — the count really was reset
```

```text
1
2
3
1
```

Without `nonlocal`, the line `count += 1` would create a *new local* `count` inside
`increment` and then fail with `UnboundLocalError` (because the local was never
assigned). Python's error message for this is famously good, but knowing the cause saves
you time.

---

## Closures

A **closure** is a function that remembers the variables from the scope where it was
created, even after that scope has finished. The inner function in the counter example
above is a closure: it keeps `count` alive.

Closures are how you build things without classes: a counter, a configuration wrapper, a
memoised cache, a decorator.

```python
def make_adder(n):
    """Return a function that adds n to whatever you give it."""
    def add(value):
        return value + n
    return add


add_five = make_adder(5)
add_ten = make_adder(10)

print(add_five(3))
print(add_ten(3))
print(add_five(100))
```

```text
8
13
105
```

Each call to `make_adder` creates a **new** `n`, and each returned function is bound to its
own `n`. The two functions are independent.

### The late-binding gotcha

Closures capture **variables**, not values. If the variable changes later, the closure sees
the new value. This bites when you create closures inside a loop.

```python
handlers = []

for name in ["weather", "search", "email"]:
    handlers.append(lambda: name)

print([handler() for handler in handlers])
```

```text
['email', 'email', 'email']
```

All three print `"email"`, not `"weather"`, `"search"`, `"email"`. The lambda refers to the
**variable** `name`, and by the time you call the lambdas the loop has finished and `name`
holds its final value. This is called **late binding**.

There are two standard fixes. The first is a default argument, which captures the value at
the moment the lambda is created:

```python
handlers = []

for name in ["weather", "search", "email"]:
    handlers.append(lambda name=name: name)

print([handler() for handler in handlers])
```

```text
['weather', 'search', 'email']
```

The second is `functools.partial`, which is a bit more explicit:

```python
import functools

handlers = []

for name in ["weather", "search", "email"]:
    handlers.append(functools.partial(lambda label: label, name))

print([handler() for handler in handlers])
```

```text
['weather', 'search', 'email']
```

The same bug appears with `for` loop variables generally, not just in lambdas — if you
capture `item` in a function defined inside a loop, you have the same problem.

---

## Docstrings

A **docstring** is a string literal as the very first statement inside a function (or a
class or a module). It is the built-in documentation for that function, and `help()` reads
it.

```python
def estimate_cost(prompt_tokens, completion_tokens, price_per_1k=0.0005):
    """Estimate the dollar cost of one API call.

    Args:
        prompt_tokens: Number of tokens in the request.
        completion_tokens: Number of tokens in the response.
        price_per_1k: Price in dollars per 1000 tokens.

    Returns:
        The estimated cost in dollars, as a float.

    Example:
        >>> estimate_cost(1000, 500)
        0.00075
    """
    return (prompt_tokens + completion_tokens) / 1000 * price_per_1k


print(estimate_cost(1000, 500))
```

```text
0.00075
```

The convention is: a one-line summary that **ends with a period**, a blank line, then
`Args:`, `Returns:` and `Raises:` sections if they apply. This is the **Google style** of
docstring, and it is the most common in the Python ecosystem. The
[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) has the full
specification.

The summary line should start with a capital letter and, ideally, with a verb phrase
("Estimate..." rather than "Estimates..." or "This function estimates...").

### Reading a docstring at runtime

```python
def chunk_text(text, size=100):
    """Split text into chunks of at most `size` characters.

    Args:
        text: The text to split.
        size: Maximum characters per chunk.

    Returns:
        A list of strings.
    """
    return [text[i:i + size] for i in range(0, len(text), size)]


print(chunk_text.__doc__)
print("---- name and defaults ----")
print(chunk_text.__name__)
import inspect
print(inspect.signature(chunk_text))
```

```text
Split text into chunks of at most `size` characters.

Args:
    text: The text to split.
    size: Maximum characters per chunk.

Returns:
    A list of strings.

---- name and defaults ----
chunk_text
(text, size=100)
```

### `help()` in the REPL

In the interactive Python prompt, typing `help(chunk_text)` prints the docstring along with
the signature, the description and the parameter list. It is the fastest way to remember
what a function does without leaving your terminal.

```python
def chunk_text(text, size=100):
    """Split text into chunks of at most `size` characters.

    Args:
        text: The text to split.
        size: Maximum characters per chunk.

    Returns:
        A list of strings.
    """
    return [text[i:i + size] for i in range(0, len(text), size)]


help(chunk_text)
```

```text
Help on function chunk_text in module __main__:

chunk_text(text, size=100)
    Split text into chunks of at most `size` characters.

    Args:
        text: The text to split.
        size: Maximum characters per chunk.

    Returns:
        A list of strings.
```

The real output is a touch longer — `help()` also prints a blank line and the module
the function came from — but this is the shape of it. The same information is available in
docstrings, in `help()`, and in your editor's autocomplete, which is why writing them pays
off immediately.

---

## Type hints: a first look

A **type hint** is an annotation that says what type a parameter or return value is
expected to be.

```python
def estimate_cost(prompt_tokens: int, completion_tokens: int, price_per_1k: float = 0.0005) -> float:
    """Estimate the dollar cost of one API call."""
    return (prompt_tokens + completion_tokens) / 1000 * price_per_1k


print(estimate_cost(1500, 800))
```

```text
0.00115
```

Type hints are **optional** and Python does **not** enforce them at runtime. `estimate_cost`
above will happily multiply strings if you ask it to. What they do is:

- give your editor real autocomplete and real error messages,
- let a **type checker** such as `mypy` catch wrong types before the code runs,
- and document the contract of the function to the next human.

That third point is the biggest one. A hint is executable documentation: it cannot go stale
the way a comment does, because a type checker compares it against the code.

We will go deep on this in [11 — Type hints and modern Python](11-type-hints-and-modern-python.md),
including generics, `Optional`, `TypedDict`, protocols and how to run `mypy` in CI. For
now, the rule is simple: add hints to the functions whose contracts you care about, and
start with the return type, because that is the one callers depend on.

---

## Functions are values

In Python, a function is an **object**. You can store it in a variable, put it in a list or
a dictionary, pass it to another function, and return it. This is what people mean when
they say functions are **first-class**.

```python
def double(number):
    return number * 2


def triple(number):
    return number * 3


operations = {"double": double, "triple": triple}

print(operations["double"](5))
print(operations["triple"](5))
print(callable(operations["double"]))
```

```text
10
15
True
```

This is exactly how a tool registry works in an agent. A dictionary maps a name to a
function, and the agent looks the name up and calls it.

```python
def get_weather(city):
    return f"It is 21 degrees and sunny in {city}."


def web_search(query):
    return f"Top result for '{query}': the Python tutorial."


TOOLS = {
    "get_weather": get_weather,
    "web_search": web_search,
}


def call_tool(name, argument):
    if name not in TOOLS:
        return f"Unknown tool: {name}"
    return TOOLS[name](argument)


print(call_tool("get_weather", "Lisbon"))
print(call_tool("web_search", "python loops"))
print(call_tool("send_email", "Ada"))
```

```text
It is 21 degrees and sunny in Lisbon.
Top result for 'python loops': the Python tutorial.
Unknown tool: send_email
```

### `lambda`

A **lambda** is a small anonymous function written in one line, with no name.

```python
square = lambda number: number ** 2

print(square(7))
print(list(map(square, [1, 2, 3])))
```

```text
49
[1, 4, 9]
```

A lambda can have any number of parameters, and it can only contain a single expression —
there is no `return` keyword; the value of that expression *is* the return value.

**Use `def` when** the function does anything non-trivial, when it needs a docstring, or
when it will be called in more than one place. **Use `lambda` when** it is a tiny,
single-expression function used immediately — typically as an argument to `sorted`,
`map`, `filter` or a key function.

```python
users = [
    {"name": "Alan", "tokens": 120},
    {"name": "Ada", "tokens": 340},
    {"name": "Grace", "tokens": 210},
]

# Lambda as a sort key: concise and obvious.
by_tokens = sorted(users, key=lambda user: user["tokens"])
print([user["name"] for user in by_tokens])

# The same thing with a def: more lines, but you can document it.
def token_count(user):
    """How many tokens this user has used."""
    return user["tokens"]


by_tokens = sorted(users, key=token_count)
print([user["name"] for user in by_tokens])
```

```text
['Alan', 'Grace', 'Ada']
['Alan', 'Grace', 'Ada']
```

A common style rule: if the lambda body needs more than one expression, write a `def`.

---

## Higher-order functions

A **higher-order function** is a function that takes a function as an argument, or returns
one as its result. `map`, `filter` and `sorted` are built-in higher-order functions, and
you will write your own constantly.

### `map()` — transform every item

```python
def to_celsius(fahrenheit):
    return (fahrenheit - 32) * 5 / 9


temperatures = [68, 77, 86, 95]

print(list(map(to_celsius, temperatures)))
```

```text
[20.0, 25.0, 30.0, 35.0]
```

`map()` is lazy in Python 3 — it produces values on demand. Wrap it in `list()` (or
`for` over it) when you want them all at once.

### `filter()` — keep only the items that pass a test

```python
def is_long(text):
    return len(text) > 4


words = ["the", "model", "is", "training", "well"]

print(list(filter(is_long, words)))
```

```text
['model', 'training']
```

Note the asymmetry: `map` takes a function that takes **one** argument and returns a
value; `filter` takes a function that takes **one** argument and returns a **boolean**.

### Writing your own

```python
def apply_to_all(values, function):
    """Call function on every value and return the results as a list."""
    return [function(value) for value in values]


def combine_all(values, function):
    """Fold values into a single result using function."""
    result = values[0]
    for value in values[1:]:
        result = function(result, value)
    return result


numbers = [1, 2, 3, 4, 5]

print(apply_to_all(numbers, lambda n: n * n))
print(combine_all(numbers, lambda a, b: a + b))
print(combine_all(numbers, lambda a, b: a * b))
```

```text
[1, 4, 9, 16, 25]
15
120
```

`combine_all` is a **reduce** operation, and the built-in `functools.reduce` does the same
thing. `map`, `filter` and `reduce` are the three functional patterns you will meet over
and over, and Python has a compact syntax for the first two that we will cover in
[07 — Comprehensions and iterators](07-comprehensions-and-iterators.md).

---

## Recursion

A **recursive** function is one that calls itself. Every recursive function needs two
parts:

1. a **base case** — the condition under which it returns immediately, and
2. a **recursive case** — the part that calls itself with a smaller problem.

```python
def factorial(number):
    """Return the product of all integers from 1 to number."""
    if number <= 1:          # base case
        return 1
    return number * factorial(number - 1)   # recursive case


print(factorial(0))
print(factorial(5))
print(factorial(10))
```

```text
1
120
3628800
```

### The call stack, in plain words

Every time a function calls another function, Python puts a **frame** — a record of that
call — on a **call stack**. When the function returns, its frame is popped off. Recursion
is just a function whose frame contains another call to itself.

```text
factorial(4)
  |
  +-- frame: factorial(4)  -> 4 * factorial(3)
         |
         +-- frame: factorial(3)  -> 3 * factorial(2)
                |
                +-- frame: factorial(2)  -> 2 * factorial(1)
                       |
                       +-- frame: factorial(1)  -> base case, returns 1
                       |
                       +-- returns 1
                +-- returns 2 * 1 = 2
         +-- returns 3 * 2 = 6
  +-- returns 4 * 6 = 24
```

The stack has a maximum depth. Exceed it and you get a `RecursionError`.

```python
def infinite(n):
    return infinite(n + 1)


try:
    infinite(0)
except RecursionError as error:
    print("RecursionError:", error)
```

```text
RecursionError: maximum recursion depth exceeded
```

The default limit is 1000 frames. You can change it with `sys.setrecursionlimit()`, but
almost always you should fix the algorithm instead of raising the limit.

### Is recursion the right tool?

Recursion is the natural shape for problems that are defined in terms of themselves:
trees, directories, divide-and-conquer algorithms, parsing. For a straight sequence, a loop
is simpler, faster and has no stack limit.

```python
def factorial(number):
    """Return the product of all integers from 1 to number, recursively."""
    if number <= 1:
        return 1
    return number * factorial(number - 1)


def factorial_loop(number):
    """Return the same result as the recursive version, using a loop."""
    result = 1
    for value in range(2, number + 1):
        result *= value
    return result


print(factorial_loop(5))
print(factorial_loop(5) == factorial(5))
```

```text
120
True
```

Both are correct. The recursive one is closer to the mathematical definition; the loop
one is faster and has no depth limit. Learn both, and pick per problem.

---

## Function or class?

Use a **function** when the job is "take these inputs, give me that output" and the
behaviour does not need to carry state between calls. Use a **class** when you need
behaviour *plus* state, or when you need many objects that share the same behaviour but
hold different data.

| Reach for a function | Reach for a class |
|---|---|
| Pure transformation of inputs | Objects with state that changes over time |
| Stateless helpers | Behaviour that belongs to a thing (a `Document`, a `Tool`) |
| One-off logic | Many instances of the same kind of thing |
| Easy to test in isolation | Needs identity, lifecycle, comparison or serialisation |

A common practical rule: write it as a function first. If you find yourself passing the
same three related values around together, that is a sign they want to be an object.

```python
# A function: no state, easy to test.
def word_count(text):
    return len(text.split())


print(word_count("hello there world"))
```

```text
3
```

The full treatment — classes, instances, methods, `__init__`, inheritance, `dataclasses`
and protocols — is in [10 — Object-oriented programming](10-object-oriented-programming.md).

---

## 🧪 Try it yourself

### Exercise 1 — A temperature converter that returns

Write a function `to_fahrenheit(celsius)` that **returns** the converted value, and a
wrapper `report(celsius)` that calls it and **prints** a formatted sentence.

Then write `convert_all(values)` that returns a list of converted values, and check it
against an expected list with `==`.

<details>
<summary>Hint</summary>

The point of the exercise is the split: `to_fahrenheit` computes, `report` presents,
`convert_all` composes. Only `report` should print.
</details>

<details>
<summary>Solution</summary>

```python
def to_fahrenheit(celsius):
    """Convert degrees Celsius to degrees Fahrenheit."""
    return celsius * 9 / 5 + 32


def report(celsius):
    """Print a sentence about a Celsius temperature."""
    fahrenheit = to_fahrenheit(celsius)
    print(f"{celsius}C is {fahrenheit:.1f}F")


def convert_all(values):
    """Convert every Celsius value in the list to Fahrenheit."""
    return [to_fahrenheit(value) for value in values]


report(21.5)
print(convert_all([0, 100]))
print(convert_all([0, 100]) == [32.0, 212.0])
```

```text
21.5C is 70.7F
[32.0, 212.0]
True
```
</details>

### Exercise 2 — Fix the mutable default

The function below is buggy. Fix it in two ways: once with a `None` sentinel, and once by
making the default an immutable value. Then explain, in a sentence, why the second fix
works when the first one is needed at all.

```python
def log_event(event, history=[]):
    history.append(event)
    return history
```

<details>
<summary>Hint</summary>

The second fix works because a `tuple` is immutable — appending to it is not possible, so
the "shared default" problem cannot bite. Use `history + (event,)` to build a new tuple.
</details>

<details>
<summary>Solution</summary>

```python
# Fix 1: None sentinel. Every call gets a fresh list.
def log_event(event, history=None):
    if history is None:
        history = []
    history.append(event)
    return history


# Fix 2: immutable default. A tuple cannot be mutated, so the shared
# default object can never change, and `history + (event,)` builds a new one.
def log_event_tuple(event, history=()):
    return history + (event,)


print(log_event("a"))
print(log_event("b"))
print(log_event_tuple("a"))
print(log_event_tuple("b"))
```

```text
['a']
['b']
('a',)
('b',)
```

Notice that `log_event_tuple` also returns the same thing on every call. The default tuple
is still shared, but because tuples are immutable the function *cannot* change it — it
builds a brand-new tuple every time. That is why fix 2 is safe and fix 1 is not.
</details>

### Exercise 3 — A closure factory

Write `make_multiplier(factor)` that returns a function which multiplies its argument by
`factor`. Then build `double`, `triple` and `ten_x` from it, and show that they are
independent.

Then write the same thing with a lambda and check the results are identical.

<details>
<summary>Hint</summary>

The inner function needs to reference `factor` from the enclosing scope. That reference is
what makes it a closure.
</details>

<details>
<summary>Solution</summary>

```python
def make_multiplier(factor):
    """Return a function that multiplies by factor."""
    def multiply(value):
        return value * factor
    return multiply


double = make_multiplier(2)
triple = make_multiplier(3)
ten_x = make_multiplier(10)

print(double(5), triple(5), ten_x(5))
print(double(5) + triple(5))   # 25 — they really are independent

make_multiplier_lambda = lambda factor: lambda value: value * factor
double_again = make_multiplier_lambda(2)
print(double_again(5), double_again is double)
```

```text
10 15 50
25
10 False
```

Each call to `make_multiplier` creates a fresh `factor` in its own scope, so the three
functions do not interfere with each other.
</details>

### Exercise 4 — Higher-order function of your own

Write `repeat(times, function, value)` that calls `function` on `value` `times` times and
returns the final result. Use it to build a function that doubles a number repeatedly.

Then write `pipeline(value, *functions)` that applies a list of functions in order, and
use it to normalise a raw model score into a final answer.

<details>
<summary>Hint</summary>

`pipeline` should start with `value` and reassign it on each pass. `*functions` lets you
accept any number of them.
</details>

<details>
<summary>Solution</summary>

```python
def repeat(times, function, value):
    """Call function on value `times` times, returning the final result."""
    for _ in range(times):
        value = function(value)
    return value


def pipeline(value, *functions):
    """Apply each function in order, passing the result to the next."""
    for function in functions:
        value = function(value)
    return value


double = lambda n: n * 2
add_ten = lambda n: n + 10
squeeze = lambda n: max(0.0, min(1.0, n))

print(repeat(3, double, 1))
print(pipeline(0.95, double, add_ten, squeeze))
print(pipeline(50.0, double, add_ten, squeeze))
```

```text
8
1.0
1.0
```

`pipeline` is a very common shape in AI code: raw model output goes through a chain of
cleaning, parsing and clamping steps, each one a small named function.
</details>

### Exercise 5 — Recursion, twice

Write `count_down(n)` recursively — it should print `n`, then `n - 1`, down to `1` — and
then write the same function with a `while` loop. Compare them.

Then write `flatten(nested)` recursively: given a list that may contain lists, return a
flat list of all the non-list items. The recursive version is much nicer here — try the
loop version and see how much worse it gets.

<details>
<summary>Hint</summary>

For `flatten`, ask: "is this item a list? If yes, flatten it and extend the result. If no,
append it." The recursive case naturally handles lists nested to any depth.
</details>

<details>
<summary>Solution</summary>

```python
def count_down_recursive(n):
    if n <= 0:
        return
    print(n)
    count_down_recursive(n - 1)


def count_down_loop(n):
    while n > 0:
        print(n)
        n -= 1


count_down_recursive(4)
print("---")
count_down_loop(4)

print("---")


def flatten(nested):
    """Flatten a list of arbitrary depth into a flat list."""
    result = []
    for item in nested:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result


print(flatten([1, [2, 3], [[4, 5], 6], 7]))
```

```text
4
3
2
1
---
4
3
2
1
---
[1, 2, 3, 4, 5, 6, 7]
```

`flatten` is recursion's best case: the problem is defined in terms of a smaller version of
itself, and the code is four lines. A loop version would need an explicit stack and would
be much harder to read.
</details>

---

## ✅ Checkpoint

1. What is the difference between a parameter and an argument?
2. What does a function return if it has no `return` statement?
3. Why should functions return values instead of printing them?
4. Why must parameters with defaults come after parameters without defaults?
5. What is the mutable default argument bug, and what is the fix?
6. At what moment is a default argument value evaluated?
7. What do `*args` and `**kwargs` collect?
8. What does `*` do when it appears in a *call*, such as `f(*args)`?
9. What does a `/` in a parameter list mean?
10. What does a function return when it returns two values?
11. What do the four letters of LEGB stand for?
12. What happens when you assign to a name inside a function that also exists globally?
13. What is the difference between `global` and `nonlocal`?
14. What is a closure?
15. What is late binding, and how do you avoid it?
16. Where does a docstring go, and what is the usual convention?
17. Do type hints change how Python behaves at runtime?
18. What is a higher-order function?
19. What are the two required parts of a recursive function?
20. When is a class a better choice than a function?

<details>
<summary>Answers</summary>

1. A parameter is the placeholder in the definition; an argument is the actual value passed
   at the call site.
2. `None`. Python returns `None` implicitly.
3. Because a returned value can be stored, asserted on, logged, cached, or passed to
   another function. A printed value can only be read by a human.
4. Because positional arguments fill parameters left to right, so a defaulted parameter in
   front would be ambiguous. Python raises a `SyntaxError`.
5. The default is a mutable object (`[]`, `{}`) that is created **once** at definition time
   and shared by every call, so it accumulates state between calls. Fix: default to `None`
   and create the object inside the function.
6. Once, when the `def` statement executes — not on each call.
7. `*args` collects extra positional arguments into a tuple; `**kwargs` collects extra
   keyword arguments into a dict.
8. It unpacks a sequence into separate positional arguments at the call site.
9. It marks the parameters before it as **positional-only**: they cannot be passed by name.
10. A tuple. The caller can unpack it with `a, b = f()`.
11. Local, Enclosing, Global, Built-in — the order Python searches for a name.
12. It creates a **new local** variable. The global is untouched. Reading a global is fine;
    writing one is the problem.
13. `global` refers to a module-level name. `nonlocal` refers to a name in the enclosing
    function scope.
14. A function that remembers the variables from the scope where it was created, even after
    that scope has finished.
15. A closure captures a **variable**, not a value, so it sees the variable's latest value.
    Fix it with a default argument (`lambda name=name: ...`) or `functools.partial`.
16. As the first statement in the function body. The convention is a one-line summary ending
    in a period, then `Args:`, `Returns:` and `Raises:` sections.
17. No. They are not enforced at runtime; they power editor tooling and static type checkers
    like `mypy`.
18. A function that takes a function as an argument, or returns one. `map`, `filter` and
    `sorted` are built-in examples.
19. A base case (when to stop) and a recursive case (the call to itself on a smaller
    problem).
20. When you need state that changes over time, many instances of the same kind of thing, or
    behaviour that belongs to an object.
</details>

---

## 🐛 Common mistakes

| Mistake | What you see | Fix |
|---|---|---|
| Mutable default argument (`bucket=[]`) | The list grows across calls; results depend on call order | Default to `None` and build the object inside the function |
| Using `print` instead of `return` | The function's result cannot be stored, tested or reused | Return the value; print at the top level of your program |
| No `return` statement | The function gives back `None` and you get `TypeError` on the result | Add an explicit `return` on every path, or a clear `return None` |
| Arguments out of order | Silent wrong behaviour when two parameters have the same type | Use keyword arguments for calls with more than one or two arguments |
| Default before non-default parameter | `SyntaxError: non-default argument follows default argument` | Put all defaulted parameters last |
| `global` for a counter or a cache | State shared across the whole program; untestable and not thread-safe | Return the new value and let the caller store it; use a closure instead |
| Missing `nonlocal` in a closure | `UnboundLocalError` on `count += 1` | Add `nonlocal count` to the inner function |
| Lambda capturing a loop variable | Every function returns the *last* value | Bind it now: `lambda name=name: ...` |
| Confusing `*args` and `**kwargs` at the call site | `TypeError: argument after ** must be a mapping` | `*` unpacks a sequence, `**` unpacks a dict |
| Recursion without a base case | `RecursionError: maximum recursion depth exceeded` | Always check the base case *before* the recursive call |
| Mutating a list while iterating it | Unexpected items visited or skipped | Build a new list instead |
| Forgetting that a function's default is evaluated once | Shared state between unrelated calls | Use `None` as the sentinel |

---

## 🔗 Resources

- [Defining Functions — Python Tutorial](https://docs.python.org/3/tutorial/controlflow.html#defining-functions) —
  the official introduction to `def`, parameters, defaults and keyword arguments.
- [Function Definitions — Language Reference](https://docs.python.org/3/reference/compound_stmts.html#function-definitions) —
  the precise rules for `*args`, `**kwargs`, keyword-only and positional-only parameters.
- [Naming and Binding — Execution Model](https://docs.python.org/3/reference/executionmodel.html#naming-and-binding) —
  the official explanation of scopes, locals, globals and closures.
- [Scopes and Names — Ned Batchelder](https://nedbatchelder.com/text/names.html) —
  the clearest written explanation of Python's scoping rules you will find anywhere.
- [functools — Python documentation](https://docs.python.org/3/library/functools.html) —
  `partial`, `reduce`, `wraps` and the other tools that make higher-order functions
  comfortable.
- [inspect — Python documentation](https://docs.python.org/3/library/inspect.html) — how to
  introspect a function at runtime: `inspect.signature`, `inspect.getsource` and friends.
- [pydoc — Python documentation](https://docs.python.org/3/library/pydoc.html) — how
  `help()` works, and how to generate documentation from your own docstrings.
- [typing — Python documentation](https://docs.python.org/3/library/typing.html) — the full
  type-hint vocabulary, for when you want more than file 11's introduction.
- [mypy documentation](https://mypy.readthedocs.io/en/stable/index.html) — the static type
  checker that turns your hints into real errors before the code runs.
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) — the
  authoritative style reference, including the docstring convention used above.

---

## ➡️ Next

- [06 — Data structures](06-data-structures.md) — functions are how you *do* things; data
  structures are how you *hold* things. Lists, dicts, sets and tuples, when to use each,
  and how mutability changes the way you write code.

**← Previous:** [04 — Control flow](04-control-flow.md)
