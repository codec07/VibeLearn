# Concurrency and Async

Your programs so far have done one thing at a time. When your script calls a weather API
and then a database and then a language model, it sits and waits — three times — and most
of the CPU does nothing at all. That waiting is the single biggest source of slowness in
AI applications. This file is about overlapping those waits: threads, processes, and
`asyncio`. It also explains the one piece of Python folklore you must understand before
you write any of it — the **GIL**, the Global Interpreter Lock — and gives you a decision
table for choosing between the tools.

> **⏱️ Time:** ~45 minutes
> **📚 Prereqs:** [14 — Standard library](14-standard-library.md)
> **🎯 By the end you can:** Tell whether a piece of work is CPU-bound or I/O-bound, then
> speed it up correctly — with a `ThreadPoolExecutor`, a `ProcessPoolExecutor`, or
> `asyncio` and `httpx` — and know exactly which mistakes (blocking the event loop,
> sharing mutable state) will undo your work.

---

## Why this matters for AI engineering

Almost every interesting AI program is a **waiting** program. Calling an LLM takes 1-3
seconds. Generating an embedding for a document chunk takes 100-500 milliseconds. Writing
100 vectors to a vector database takes as long as writing them one at a time — unless you
write them concurrently. A RAG pipeline that retrieves 10 chunks and re-ranks them can be
five times faster with the same code, if the calls overlap.

The skills in this file are the difference between a demo that takes 30 seconds and a
product that takes 6. They are also the difference between a chatbot that feels sluggish
and one that feels instant. And they are what a hiring interviewer means when they ask
"how would you speed up this pipeline?"

---

## 1. The problem: waiting

Here is a program that fetches three web pages, one after the other. Each call takes one
second (a realistic number for a slow API).

```python
import time


def fetch_page(page_id: int) -> str:
    """Pretend to fetch a page over the network. Takes one second."""
    time.sleep(1.0)
    return f"page {page_id}"


if __name__ == "__main__":
    start = time.perf_counter()
    results = [fetch_page(i) for i in range(1, 4)]
    elapsed = time.perf_counter() - start

    print(results)
    print(f"took {elapsed:.2f} seconds")
```

```text
['page 1', 'page 2', 'page 3']
took 3.00 seconds
```

Three seconds of work, of which about 0.001 seconds was actual computation. The other
2.999 seconds was the program sitting there, doing nothing, waiting for a network packet
to come back.

Now the same thing, with the waits overlapped:

```python
import time
from concurrent.futures import ThreadPoolExecutor


def fetch_page(page_id: int) -> str:
    """Pretend to fetch a page over the network. Takes one second."""
    time.sleep(1.0)
    return f"page {page_id}"


if __name__ == "__main__":
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(fetch_page, [1, 2, 3]))
    elapsed = time.perf_counter() - start

    print(results)
    print(f"took {elapsed:.2f} seconds")
```

```text
['page 1', 'page 2', 'page 3']
took 1.00 seconds
```

Same code, same results, three times faster. That is the whole idea.

---

## 2. Concurrency versus parallelism

Two words that get used interchangeably and should not be.

- **Concurrency** means *structuring* a program as many independent tasks that make
  progress over overlapping periods of time. It is about **how** you organise work.
- **Parallelism** means *actually executing* multiple things at the same instant, on
  different cores. It is about **what is physically happening**.

```text
CONCURRENCY - overlapping tasks                PARALLELISM - simultaneous execution

Task A:  ████░░░░████░░░░░░░░                  Core 1:  ████████░░░░░░░░░░░░
Task B:  ░░░░░░██████░░░░░░░░                  Core 2:  ░░░░░░░██████████████
Task C:  ░░░░░░░░░░░░████░░░░
                                                 time →                        2
time →                2

Only ONE task runs at any instant,            Two cores run at the same instant.
but the task switches happen fast.
```

A single-core laptop can be **concurrent** but not **parallel**. A multi-core machine can
be both. You can write concurrent code in Python that never uses more than one core — and
that is usually what you want, because your work is waiting on the network, not
calculating.

---

## 3. The GIL — the Global Interpreter Lock

CPython — the Python you are running — has a mechanism called the **Global Interpreter
Lock**. It is a single lock, held by exactly one thread at a time, that guards the
interpreter itself. Only one thread can be executing Python bytecode at any moment.

```text
   Thread 1  ──►  ┌────────────────────────┐  ──►  releases the GIL
   Thread 2  ──►  │  executing Python      │  ──►  waits for it
   Thread 3  ──►  │  bytecode              │  ──►  waits for it
                   └────────────────────────┘
                        exactly one at a time
```

**What the GIL prevents:** true CPU parallelism between Python threads. If you have ten
threads each doing pure calculation, they do not run ten times faster — they take turns,
and you get no speedup at all (often a slowdown, from the overhead of switching).

**What the GIL does NOT prevent:** threads still overlap I/O waits. When a thread makes a
network call, Python releases the GIL while it waits for the response, so another thread
runs in the meantime. This is exactly the case that matters for AI applications, which
spend nearly all their time waiting for an API to answer.

**Free-threaded builds:** Python 3.13 shipped an experimental build (the "no-GIL" or
free-threaded build, `python3.13t`) where the GIL can be disabled, allowing real
CPU parallelism in threads. It is not the default yet, and most production systems still
run the normal build. The practical advice for 2026 is unchanged: use threads for
I/O-bound work, use processes for CPU-bound work.

---

## 4. CPU-bound or I/O-bound? The most important question

This is the decision that determines everything else. Look at where your program spends
its time.

- **I/O-bound** work spends its time *waiting*: network requests, reading files, waiting
  for a database, waiting for a lock. The CPU is idle. This is where threads and `asyncio`
  shine.
- **CPU-bound** work spends its time *calculating*: parsing a huge JSON file, resizing
  images, running a model forward pass, compressing data, crunching numbers. The CPU is
  busy and more CPU would help. This is where processes shine.

| | I/O-bound (waiting) | CPU-bound (calculating) |
|---|---|---|
| Examples | LLM API calls, embedding batches, vector store reads/writes, downloading a model, reading a file | Tokenising a huge corpus, image resizing, training, simulations, zipping a directory |
| What is idle | the CPU | nothing — the CPU is saturated |
| Use | **threads** or **asyncio** | **processes** (`ProcessPoolExecutor`) |
| Why it works | the GIL is released while waiting | each process gets its own interpreter and can use its own core |
| Speedup ceiling | number of network connections, not cores | number of CPU cores |

**Rule of thumb:** if you are waiting on the internet, use threads or asyncio. If you are
squeezing numbers, use processes. If in doubt, measure — and remember that most "AI"
work is waiting.

---

## 5. Threads: `threading.Thread`

A **thread** is a separate flow of execution inside one process. Threads share memory,
so they can share data directly — which is both their convenience and their danger.

```python
import threading
import time


def worker(name: str, seconds: float) -> None:
    """Do some (pretend) work, then report."""
    print(f"{name} starting")
    time.sleep(seconds)
    print(f"{name} finished")


if __name__ == "__main__":
    start = time.perf_counter()

    threads = [
        threading.Thread(target=worker, args=("worker-1", 1.0)),
        threading.Thread(target=worker, args=("worker-2", 1.0), daemon=True),
    ]

    for thread in threads:
        thread.start()          # start it running in the background

    for thread in threads:
        thread.join()           # wait for it to finish

    print(f"all done in {time.perf_counter() - start:.2f} seconds")
```

```text
worker-1 starting
worker-2 starting
worker-1 finished
worker-2 finished
all done in 1.00 seconds
```

The three methods that matter:

| Method | What it does |
|---|---|
| `thread.start()` | begins running the thread in the background. Returns immediately. |
| `thread.join()` | **blocks** the calling thread until this thread finishes. |
| `daemon=True` | the thread is killed abruptly when the main thread exits |

**You must call `join()`.** A common beginner bug is to start threads and immediately
print something else, then find that the program exits before the threads finish. In the
example above, `join()` is what guarantees both workers are done before "all done" is
printed.

Daemon threads are killed when the main program ends, so they are useful for
"background housekeeping" but dangerous for work you actually need finished.

---

## 6. `ThreadPoolExecutor` — the practical way to use threads

Creating a `Thread` by hand is fine for a handful of tasks. For "run this function over
100 URLs", use a **thread pool**: a fixed set of worker threads that pull tasks off a
queue. `concurrent.futures` is in the standard library.

```python
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


def fetch(url: str) -> str:
    """Pretend to download a URL. Later pages answer faster."""
    delay = 1.0 - int(url.rsplit("/", 1)[1]) * 0.15
    time.sleep(delay)
    return f"content of {url}"


if __name__ == "__main__":
    urls = [f"https://example.com/page/{i}" for i in range(5)]

    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=5) as executor:
        for future in as_completed(executor.submit(fetch, url) for url in urls):
            print(future.result())
    elapsed = time.perf_counter() - start

    print(f"5 downloads in {elapsed:.2f} seconds")
```

```text
content of https://example.com/page/4
content of https://example.com/page/3
content of https://example.com/page/2
content of https://example.com/page/1
content of https://example.com/page/0
5 downloads in 1.00 seconds
```

Note the order: the fastest page is printed first. That is the whole difference between
`as_completed` and `map`.

Two ways to collect the results, and the difference matters:

```python
from concurrent.futures import ThreadPoolExecutor, as_completed


def fetch(url: str) -> str:
    return f"content of {url}"


with ThreadPoolExecutor(max_workers=5) as executor:
    # 1. executor.map: results in the SAME ORDER as the inputs.
    #    It waits for every result before yielding any of them.
    ordered = list(executor.map(fetch, ["a", "b", "c"]))
    print(ordered)

    # 2. as_completed: results as they FINISH, in completion order.
    #    Use this when you want to process each result as soon as it is ready.
    futures = [executor.submit(fetch, url) for url in ["a", "b", "c"]]
    for future in as_completed(futures):
        print(future.result())
```

A **future** is a placeholder for a result that may not exist yet. It has
`.result()` (wait and return the value, re-raising any exception), `.done()` and
`.exception()`.

The `with` block is important: when it exits, the executor waits for all its threads to
finish, and then shuts them down cleanly.

---

## 7. Processes for CPU-bound work: `ProcessPoolExecutor`

A **process** is a separate copy of the interpreter with its own memory. Processes are
not restricted by the GIL, so they can truly run on different CPU cores at the same time.

```python
import time
from concurrent.futures import ProcessPoolExecutor


def crunch(numbers: list[int]) -> int:
    """CPU-bound work: run in a separate process."""
    total = 0
    for _ in range(8_000_000):
        total += 1
    return total


if __name__ == "__main__":
    start = time.perf_counter()
    with ProcessPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(crunch, [[1], [2], [3], [4]]))
    parallel = time.perf_counter() - start

    start = time.perf_counter()
    serial = [crunch([1]) for _ in range(4)]
    serial_time = time.perf_counter() - start

    print(results)
    print(f"parallel: {parallel:.2f} seconds")
    print(f"serial:   {serial_time:.2f} seconds")
```

```text
[8000000, 8000000, 8000000, 8000000]
parallel: 0.88 seconds
serial:   1.91 seconds
```

The exact numbers depend on how many cores your machine has, but the shape is the point:
four chunks of arithmetic finish in roughly half the time of the same four chunks run one
after another. Threads could never do this, because the GIL would serialise them.

### The pickling constraint

To send work to another process, Python must **pickle** (serialise) the function and its
arguments, send them over, and unpickle them on the other side. That means only
**picklable** objects can cross the process boundary:

| Picklable | Not picklable |
|---|---|
| ints, floats, strings, bytes | open file handles |
| lists, tuples, dicts, sets | database connections |
| ordinary classes defined at module level | sockets, threads, locks |
| dataclasses and NamedTuples | lambdas and locally-defined functions |
| most plain Python objects | generators, coroutines |

A `lambda` cannot be sent to another process. A class defined *inside* a function
cannot either. If you get `AttributeError: Can't pickle local object` or
`Can't pickle <function ...>`, this is why.

Also note: on Windows and macOS, the new process is **spawned** fresh rather than
forked, so the code that creates the pool must be protected by
`if __name__ == "__main__":` — exactly as in the example above.

### `multiprocessing` briefly

`multiprocessing` is the lower-level module that `ProcessPoolExecutor` is built on. Its
most famous feature is the **pool**:

```python
import multiprocessing


def square(n: int) -> int:
    return n * n


if __name__ == "__main__":
    with multiprocessing.Pool(processes=4) as pool:
        print(pool.map(square, [1, 2, 3, 4, 5]))
        print(pool.apply_async(square, (10,)).get())
```

```text
[1, 4, 9, 16, 25]
100
```

`pool.map` works like `executor.map`; `apply_async` returns an `AsyncResult` whose `.get()`
waits for the value. In new code, prefer `concurrent.futures` — it has a cleaner API and
the same interface for threads and processes.

---

## 8. Thread safety: the shared mutable state trap

Threads share memory. If two threads change the same object at the same time, you get a
**race condition** — a bug whose behaviour depends on timing, and which therefore passes
in testing and fails in production.

Here is a race, made deterministic by putting a tiny sleep between the read and the
write:

```python
import threading
import time

shared = {"count": 0}
lock = threading.Lock()


def increment_unsafe() -> None:
    """Read, pause, then write - two threads can interleave here."""
    for _ in range(100):
        current = shared["count"]
        time.sleep(0.0001)
        shared["count"] = current + 1


def increment_safe() -> None:
    """The same thing, but only one thread may be inside the critical section."""
    for _ in range(100):
        with lock:
            current = shared["count"]
            time.sleep(0.0001)
            shared["count"] = current + 1


if __name__ == "__main__":
    threads = [threading.Thread(target=increment_unsafe) for _ in range(4)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    print(f"unsafe: expected 400, got {shared['count']}")

    shared["count"] = 0
    threads = [threading.Thread(target=increment_safe) for _ in range(4)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    print(f"safe:   expected 400, got {shared['count']}")
```

```text
unsafe: expected 400, got 101
safe:   expected 400, got 400
```

Updates were lost. Your own number will differ — a race condition is
non-deterministic, which is exactly what makes it dangerous. The fix is a **lock**: a
mutual-exclusion device that lets only one thread into the critical section at a time.

```python
import threading

shared = {"count": 0}
lock = threading.Lock()

with lock:          # acquire on entry, release automatically on exit
    shared["count"] += 1

print(shared)
```

```text
{'count': 1}
```

Other synchronisation tools you will meet:

| Tool | Use it for |
|---|---|
| `threading.Lock` | protecting one piece of shared state |
| `threading.RLock` | a lock that the same thread may re-enter |
| `threading.Event` | telling one thread that something happened |
| `threading.Condition` | waiting for a condition to become true |
| `threading.Semaphore` | limiting how many threads may run at once |

**The best lock is no shared state.** If each thread works on its own data and you
combine the results at the end, you have no locks and no race conditions. Prefer that
design.

---

## 9. `queue.Queue` — passing data safely between threads

When threads need to hand work to each other, do not use a shared list — use a
**queue**. `queue.Queue` is thread-safe: it handles the locking for you.

```python
import queue
import threading
import time


def producer(q: queue.Queue) -> None:
    """Put five items on the queue, then a sentinel saying 'I am done'."""
    for i in range(5):
        q.put(f"item {i}")
        time.sleep(0.05)
    q.put(None)


def consumer(q: queue.Queue) -> None:
    """Take items off the queue until the sentinel arrives."""
    while True:
        item = q.get()
        if item is None:
            q.task_done()
            break
        print("consumed", item)
        time.sleep(0.1)
        q.task_done()


if __name__ == "__main__":
    q: queue.Queue[str] = queue.Queue()

    p = threading.Thread(target=producer, args=(q,))
    c = threading.Thread(target=consumer, args=(q,))
    p.start()
    c.start()

    p.join()
    q.join()   # block until every item has been processed
    c.join()
    print("queue drained")
```

```text
consumed item 0
consumed item 1
consumed item 2
consumed item 3
consumed item 4
queue drained
```

The `None` value is a **sentinel**: it tells the consumer "no more work is coming" so it
knows to stop. `q.task_done()` marks one item as finished, and `q.join()` waits until
every item has been marked.

---

## 10. `asyncio` — one thread, many tasks

`asyncio` is a different model from threads. Instead of the operating system switching
between threads at arbitrary moments, you write **coroutines** that explicitly hand
control back to an **event loop** whenever they need to wait.

```python
import asyncio


async def work(name: str, seconds: float) -> str:
    """Pretend to do some I/O."""
    await asyncio.sleep(seconds)
    return f"{name} finished after {seconds}s"


async def main() -> None:
    # asyncio.gather runs many coroutines concurrently and waits for all of them
    results = await asyncio.gather(
        work("task-a", 1.0),
        work("task-b", 0.5),
        work("task-c", 0.25),
    )
    for result in results:
        print(result)

    # create_task starts something now, and you collect the result later
    task = asyncio.create_task(work("task-d", 0.5))
    print("task-d started, doing something else first")
    print(await task)


asyncio.run(main())
```

```text
task-a finished after 1.0s
task-b finished after 0.5s
task-c finished after 0.25s
task-d started, doing something else first
task-d finished after 0.5s
```

```text
THREADS (preemptive)                    ASYNCIO (cooperative)

Thread 1: ──────work──────┐             Task A: ──await──┐
Thread 2: ──┐─────work─────┘             Task B: ─await─┐  │
Thread 3: ──┴──────work──────             Task C: ──┐────┴──┘
                                          ┌────────────────────┐
The OS decides when to switch            │   ONE event loop    │
threads. They may interleave            │   one thread only   │
anywhere.                               └────────────────────┘
                                          It switches ONLY at `await` points.
```

### The vocabulary

| Piece | What it is |
|---|---|
| `async def` | defines a **coroutine**: a function that can be paused and resumed |
| `await` | "pause me until this finishes, then give me the result" |
| `asyncio.run(coro)` | the entry point: creates an event loop, runs the coroutine, closes the loop |
| `asyncio.create_task(coro)` | schedules a coroutine to run in the background, returns a `Task` |
| `asyncio.gather(*coros)` | runs them concurrently and returns their results in order |
| `asyncio.sleep(n)` | the async way to wait (never use `time.sleep` in async code) |
| `asyncio.wait_for(coro, timeout)` | gives up after `timeout` seconds |

### Timeouts

```python
import asyncio


async def slow() -> str:
    await asyncio.sleep(5)
    return "done"


async def main() -> None:
    # The classic way: wait_for raises TimeoutError
    try:
        await asyncio.wait_for(slow(), timeout=0.5)
    except asyncio.TimeoutError:
        print("wait_for: gave up after 0.5 seconds")

    # The modern way (Python 3.11+): asyncio.timeout is a context manager
    try:
        async with asyncio.timeout(0.5):
            await slow()
    except TimeoutError:
        print("timeout: gave up after 0.5 seconds")


asyncio.run(main())
```

```text
wait_for: gave up after 0.5 seconds
timeout: gave up after 0.5 seconds
```

### `TaskGroup` — structured concurrency (Python 3.11+)

`asyncio.gather` is convenient, but if one task fails, the others keep running and you
may not notice. `asyncio.TaskGroup` is the safer, modern approach: it runs a group of
tasks, waits for all of them, and if any fail it cancels the rest and raises an
`ExceptionGroup`.

```python
import asyncio


async def step(name: str, seconds: float) -> str:
    await asyncio.sleep(seconds)
    return f"{name} ok"


async def main() -> None:
    async with asyncio.TaskGroup() as group:
        for name in ("a", "b", "c"):
            group.create_task(step(name, 0.2))
    print("all three finished, no errors")


asyncio.run(main())
```

```text
all three finished, no errors
```

---

## 11. The one rule: never block the event loop

Inside `async def`, the event loop is running your code. If your code blocks, *everything*
blocks — every other task, every connection, the whole program.

`time.sleep()` blocks. `requests.get()` blocks. A synchronous database driver blocks.
`asyncio.sleep()` does not block; it hands control back to the loop.

```python
import asyncio
import time


async def blocking_task() -> str:
    time.sleep(1.0)             # WRONG: freezes the entire event loop
    return "blocking done"


async def quick_task() -> str:
    await asyncio.sleep(0.1)    # RIGHT: yields control to the loop
    return "quick done"


async def main() -> None:
    start = time.perf_counter()
    results = await asyncio.gather(blocking_task(), quick_task())
    elapsed = time.perf_counter() - start

    print(results)
    print(f"total {elapsed:.2f} seconds")


asyncio.run(main())
```

```text
['blocking done', 'quick done']
total 1.11 seconds
```

The quick task should have finished after 0.1 seconds, but it had to wait for the blocking
task to release the event loop. Here is the fixed version:

```python
import asyncio
import time


async def blocking_task() -> str:
    await asyncio.sleep(1.0)    # RIGHT: yields control to the loop
    return "blocking done"


async def quick_task() -> str:
    await asyncio.sleep(0.1)
    return "quick done"


async def main() -> None:
    start = time.perf_counter()
    results = await asyncio.gather(blocking_task(), quick_task())
    elapsed = time.perf_counter() - start

    print(results)
    print(f"total {elapsed:.2f} seconds")


asyncio.run(main())
```

```text
['blocking done', 'quick done']
total 1.00 seconds
```

Now the quick task finished after 0.1 seconds and the total is 1 second, not 1.2.

**The checklist:** inside `async def`, use `await asyncio.sleep()` not `time.sleep()`;
use an async HTTP client not `requests`; use `asyncio.to_thread(...)` to call a blocking
library safely:

```python
import asyncio
import time


def blocking_read() -> str:
    time.sleep(0.5)
    return "read from a blocking library"


async def main() -> None:
    # to_thread runs a blocking function in a worker thread, so the loop stays free
    result = await asyncio.to_thread(blocking_read)
    print(result)


asyncio.run(main())
```

```text
read from a blocking library
```

---

## 12. Async HTTP with `httpx`

`requests` is the classic HTTP library, and it is **blocking**. For async code you want
`httpx`, whose `AsyncClient` is the modern standard.

```bash
python -m pip install httpx
```

Here is a fully runnable example that uses the real `httpx` API but makes **no network
calls** — `httpx.MockTransport` lets you run the exact same code offline:

```python
import asyncio

import httpx


async def fetch_document(client: httpx.AsyncClient, doc_id: int) -> str:
    """Fetch one document and return its title."""
    response = await client.get(f"/documents/{doc_id}")
    response.raise_for_status()
    return response.json()["title"]


async def main() -> None:
    # MockTransport replies locally, so this example needs no internet and no API key.
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"title": f"Document {request.url.path[-1]}"})

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(
        transport=transport, base_url="https://api.example.com"
    ) as client:
        titles = await asyncio.gather(
            *[fetch_document(client, doc_id) for doc_id in range(1, 4)]
        )

    for title in titles:
        print(title)


asyncio.run(main())
```

```text
Document 1
Document 2
Document 3
```

The real thing looks like this. **This one needs internet access and an API key** — it
will print a message and exit cleanly if `OPENAI_API_KEY` is not set:

```python
import asyncio
import os

import httpx

MODEL = "gpt-4o-mini"


async def summarise(client: httpx.AsyncClient, text: str) -> str:
    """Ask the model for a summary."""
    response = await client.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"},
        json={
            "model": MODEL,
            "messages": [{"role": "user", "content": f"Summarise: {text}"}],
        },
        timeout=30.0,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


async def main() -> None:
    if not os.environ.get("OPENAI_API_KEY"):
        print("OPENAI_API_KEY is not set - skipping the live API call.")
        return

    texts = [f"Document number {i}" for i in range(1, 6)]

    async with httpx.AsyncClient() as client:
        summaries = await asyncio.gather(*[summarise(client, text) for text in texts])

    for summary in summaries:
        print(summary)


asyncio.run(main())
```

```text
OPENAI_API_KEY is not set - skipping the live API call.
```

Three things to notice in the real version:

- **One client for all requests.** Creating an `AsyncClient` per request throws away the
  connection pool and costs a TCP and TLS handshake every time. Create it once, use the
  `async with` block.
- **Always set a timeout.** Without one, a hung server hangs your program forever.
- **`asyncio.gather` for the batch**, so the five calls overlap.

### `aiohttp`

`aiohttp` is the other popular async HTTP library, and it also provides a web *server*.
If you only need an async HTTP client, `httpx` is the modern recommendation: it has a
synchronous API too (`httpx.get(...)`), so the same library works in both styles.
`aiohttp` is a good choice when you also want to build an async web service.

---

## 13. Cancellation

In `asyncio`, tasks can be cancelled — that is how a timeout or a shutdown works.

```python
import asyncio


async def worker() -> None:
    try:
        await asyncio.sleep(10)
        print("finished - you will never see this")
    except asyncio.CancelledError:
        print("worker: I was cancelled, cleaning up")
        raise


async def main() -> None:
    task = asyncio.create_task(worker())
    await asyncio.sleep(0.2)     # let it get going
    task.cancel()                # ask it to stop

    try:
        await task
    except asyncio.CancelledError:
        print("main: the task was cancelled")


asyncio.run(main())
```

```text
worker: I was cancelled, cleaning up
main: the task was cancelled
```

`CancelledError` inherits from `BaseException`, not `Exception`, so a bare
`except Exception:` will not catch it. Catch it explicitly, do your cleanup, and
**re-raise** it — swallowing a cancellation leaves the task in a broken state.

---

## 14. Which tool should you use?

| Situation | Use | Why |
|---|---|---|
| One or two simple HTTP calls | plain synchronous code with `httpx` | simplest possible code; the latency difference is seconds |
| Many independent I/O calls (10+ LLM calls, embedding batches) | `asyncio` + `httpx.AsyncClient` | one thread, thousands of concurrent connections, lowest overhead |
| A few calls, or you are using a blocking library | `ThreadPoolExecutor` | much easier to write, and fast enough |
| CPU-heavy work (parsing a huge file, image processing, a model forward pass) | `ProcessPoolExecutor` | real parallelism across cores; the GIL is not in the way |
| Code you cannot make async (a synchronous SDK) | `asyncio.to_thread()` | runs the blocking call in a thread without freezing the loop |
| You are not sure | start synchronous, measure, then optimise | premature concurrency is a bug factory |

A rough decision tree:

```text
Is the work waiting (network, disk, database)?
  |
  +-- YES  ->  How many calls at once?
  |            |
  |            +-- 1-2          ->  plain synchronous code
  |            +-- 3-10         ->  ThreadPoolExecutor
  |            +-- 10 or more   ->  asyncio + httpx.AsyncClient
  |
  +-- NO (pure calculation)
            |
            +--  ->  ProcessPoolExecutor
```

And the three rules that override everything else:

1. **Measure before you optimise.** A single `time.perf_counter()` around the slow part
   tells you whether concurrency is even the problem.
2. **Never block the event loop.** Use `await asyncio.sleep`, async clients, and
   `asyncio.to_thread` for blocking libraries.
3. **Do not share mutable state between threads.** Use a queue, or give each thread its
   own data.

---

## 15. The AI-engineer angle: cutting latency by batching

LLM calls are I/O-bound: the model is thinking while your program does nothing. Sending
ten prompts one at a time costs ten round-trip latencies. Sending them concurrently
costs roughly one.

```python
import asyncio
import time


async def call_model(prompt: str, latency: float = 0.5) -> str:
    """Pretend to call an LLM API: one network round trip."""
    await asyncio.sleep(latency)
    return f"summary of {prompt}"


async def main() -> None:
    prompts = [f"document {i}" for i in range(1, 11)]

    # 1. The slow way: one call at a time
    start = time.perf_counter()
    serial = [await call_model(prompt) for prompt in prompts]
    serial_time = time.perf_counter() - start

    # 2. The fast way: all the calls overlap
    start = time.perf_counter()
    concurrent = await asyncio.gather(*[call_model(prompt) for prompt in prompts])
    concurrent_time = time.perf_counter() - start

    print(f"serial:     {serial_time:.2f} s")
    print(f"concurrent: {concurrent_time:.2f} s")
    print(f"speedup:    {serial_time / concurrent_time:.1f}x")
    print(f"same results: {serial == concurrent}")


asyncio.run(main())
```

```text
serial:     5.04 s
concurrent: 0.52 s
speedup:    9.8x
same results: True
```

The same trick applies everywhere in an AI system:

- **Embedding batches**: embed 500 chunks concurrently instead of in a loop.
- **Vector store writes**: write embeddings in parallel.
- **Retrieval**: search several indexes or collections at once.
- **Evaluation harnesses**: score 200 test cases concurrently, so a CI run takes minutes
  instead of an hour.
- **Multi-agent systems**: when an agent's plan has three independent research steps,
  run them together rather than one after another.

Two cautions:

1. **Respect the rate limits.** Most providers cap requests per second. Concurrency
   without a limit will get you a `429 Too Many Requests`. Use a semaphore to cap how
   many calls are in flight at once:

   ```python
   semaphore = asyncio.Semaphore(5)

   async def call_model(prompt: str) -> str:
       async with semaphore:
           ...
   ```

2. **Do not lose failures.** `asyncio.gather` without `return_exceptions=True` cancels the
   others when one fails. For batch jobs where you want every result, use
   `asyncio.gather(..., return_exceptions=True)` or a `TaskGroup`, and handle each
   failure individually.

---

## 🧪 Try it yourself

**Exercise 1 — Prove that waiting is the bottleneck.**
Write a function `slow_double(n)` that sleeps for one second and returns `n * 2`. Call it
for `n` in 1..5 serially, then with a `ThreadPoolExecutor` of 5 workers. Print both
timings and the speedup.

<details>
<summary>Hint</summary>

`executor.map` returns an iterator; wrap it in `list(...)` to force it to wait for all
results. Use `time.perf_counter()` around each section.
</details>

<details>
<summary>Solution</summary>

```python
import time
from concurrent.futures import ThreadPoolExecutor


def slow_double(n: int) -> int:
    """Pretend to do a slow round trip, then double the number."""
    time.sleep(1.0)
    return n * 2


if __name__ == "__main__":
    start = time.perf_counter()
    serial = [slow_double(n) for n in range(1, 6)]
    serial_time = time.perf_counter() - start

    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=5) as executor:
        concurrent = list(executor.map(slow_double, range(1, 6)))
    concurrent_time = time.perf_counter() - start

    print(serial)
    print(concurrent)
    print(f"serial:     {serial_time:.2f} s")
    print(f"concurrent: {concurrent_time:.2f} s")
    print(f"speedup:    {serial_time / concurrent_time:.1f}x")
```

```text
[2, 4, 6, 8, 10]
[2, 4, 6, 8, 10]
serial:     5.00 s
concurrent: 1.00 s
speedup:    5.0x
```
</details>

**Exercise 2 — Find and fix a race condition.**
Write a function that increments a shared counter from four threads, 1000 times each, but
first reads the counter and then sleeps before writing the new value back. Show that you
lose increments, then fix it with a `threading.Lock`.

<details>
<summary>Hint</summary>

```python
import time

shared = {"count": 0}

current = shared["count"]         # read
time.sleep(0.0001)                # another thread can slip in here
shared["count"] = current + 1     # write

print(shared)
```

The sleep is what lets another thread slip in between the read and the write, so two
threads can read the same value and write back the same result — losing one increment.
</details>

<details>
<summary>Solution</summary>

```python
import threading
import time

lock = threading.Lock()
shared = {"count": 0}


def increment_unsafe() -> None:
    for _ in range(1000):
        current = shared["count"]
        time.sleep(0.0001)
        shared["count"] = current + 1


def increment_safe() -> None:
    for _ in range(1000):
        with lock:
            current = shared["count"]
            time.sleep(0.0001)
            shared["count"] = current + 1


if __name__ == "__main__":
    threads = [threading.Thread(target=increment_unsafe) for _ in range(4)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    print(f"unsafe: expected 4000, got {shared['count']}")

    shared["count"] = 0
    threads = [threading.Thread(target=increment_safe) for _ in range(4)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    print(f"safe:   expected 4000, got {shared['count']}")
```

```text
unsafe: expected 4000, got 1003
safe:   expected 4000, got 4000
```

Your unsafe number will differ, and that is exactly the point — a race condition is
non-deterministic.
</details>

**Exercise 3 — Write an async batch summariser.**
Write `async def summarise_all(texts: list[str]) -> list[str]` that calls an
`async def summarise(text)` coroutine for every text and returns all the results. Use
`asyncio.sleep` to simulate the API latency, and print how long the whole batch took for
1 text versus 5 texts.

<details>
<summary>Hint</summary>

`asyncio.gather(*[summarise(t) for t in texts])` runs them all at once. The total time
should be roughly the time of one call, no matter how many texts there are.
</details>

<details>
<summary>Solution</summary>

```python
import asyncio
import time


async def summarise(text: str) -> str:
    """Pretend to call an LLM: one round trip."""
    await asyncio.sleep(0.5)
    return f"summary of {text}"


async def summarise_all(texts: list[str]) -> list[str]:
    """Summarise every text concurrently and return the results in order."""
    return await asyncio.gather(*[summarise(text) for text in texts])


async def main() -> None:
    for count in (1, 5):
        texts = [f"document {i}" for i in range(count)]
        start = time.perf_counter()
        results = await summarise_all(texts)
        elapsed = time.perf_counter() - start
        print(f"{count} text(s) in {elapsed:.2f} s -> {results[0]}")


asyncio.run(main())
```

```text
1 text(s) in 0.50 s -> summary of document 0
5 text(s) in 0.51 s -> summary of document 0
```
</details>

**Exercise 4 — Break the event loop on purpose.**
Write two coroutines: one that calls `time.sleep(1.0)` and one that calls
`await asyncio.sleep(0.1)`. Run them with `asyncio.gather` and print the total time.
Then swap `time.sleep` for `await asyncio.sleep` and print the total again. Explain the
difference in one sentence.

<details>
<summary>Hint</summary>

`time.sleep(1.0)` blocks the only thread the event loop has, so the 0.1-second task
cannot even start until the 1-second task is finished.
</details>

<details>
<summary>Solution</summary>

```python
import asyncio
import time


async def blocking() -> str:
    time.sleep(1.0)
    return "blocking"


async def quick() -> str:
    await asyncio.sleep(0.1)
    return "quick"


async def measure(coro_a, coro_b) -> float:
    start = time.perf_counter()
    await asyncio.gather(coro_a(), coro_b())
    return time.perf_counter() - start


async def main() -> None:
    print(f"with time.sleep:     {await measure(blocking, quick):.2f} s")
    print(f"with asyncio.sleep:  {await measure(quick, blocking):.2f} s")


asyncio.run(main())
```

```text
with time.sleep:     1.11 s
with asyncio.sleep:  1.00 s
```

The blocking version takes 1.1 seconds because the quick task cannot start until the
blocking task releases the event loop. The async version takes 1.0 seconds because the
quick task runs during the blocking task's wait.
</details>

---

## ✅ Checkpoint

**1. What is the difference between concurrency and parallelism?**

<details>
<summary>Answer</summary>

Concurrency is about structuring work as many overlapping tasks; parallelism is about
actually executing several things at the same instant on different cores. A single-core
machine can be concurrent but not parallel.
</details>

**2. What does the GIL stop you from doing, and what does it not stop you from doing?**

<details>
<summary>Answer</summary>

It stops true CPU parallelism between threads (only one thread runs Python bytecode at a
time). It does *not* stop threads from overlapping I/O waits, because the GIL is released
while a thread waits on a socket or a file.
</details>

**3. Your program spends all its time waiting for HTTP responses. Which tool do you
reach for, and why not processes?**

<details>
<summary>Answer</summary>

Threads (`ThreadPoolExecutor`) or `asyncio` + `httpx.AsyncClient`. Processes would not
help: the work is waiting, not computing, and processes cost far more to start and to
pass data between.
</details>

**4. What is the difference between `executor.map` and `as_completed`?**

<details>
<summary>Answer</summary>

`executor.map` yields results in the order of the inputs, and waits for all of them.
`as_completed` yields each result as soon as that task finishes, in completion order.
</details>

**5. Why must you call `thread.join()`?**

<details>
<summary>Answer</summary>

`start()` returns immediately. Without `join()`, the main thread could finish and the
program could exit while the worker threads were still running — or their output could
be lost.
</details>

**6. What does a `threading.Lock` protect, and what is the alternative to needing one?**

<details>
<summary>Answer</summary>

It protects a critical section where shared state is read and written, so only one
thread is inside at a time. The better alternative is to not share mutable state at all:
give each thread its own data and combine the results afterwards.
</details>

**7. Why must you never call `time.sleep()` inside `async def`?**

<details>
<summary>Answer</summary>

Because the event loop has only one thread. `time.sleep()` blocks that thread, so every
other task in the program freezes until it returns. Use `await asyncio.sleep()`.
</details>

**8. What does `asyncio.gather` do with `return_exceptions=True`, and when do you want it?**

<details>
<summary>Answer</summary>

Without it, the first exception cancels the other tasks and propagates. With it, every
task runs to completion and the failures are returned in place of the results. You want
it for batch jobs where one bad item should not abort the whole batch.
</details>

---

## 🐛 Common mistakes

| Mistake | What you see | Fix |
|---|---|---|
| Forgetting `join()` after `start()` | The program exits before the threads finish, and their output never appears | Call `thread.join()` for every thread, or use `with ThreadPoolExecutor(...)` |
| Using `time.sleep` inside `async def` | Every other task freezes; total time is the sum of all sleeps | Use `await asyncio.sleep()`, or `await asyncio.to_thread(blocking_fn)` |
| Using `requests` inside async code | The event loop blocks for the whole HTTP request | Use `httpx.AsyncClient` |
| Creating a new `AsyncClient` per request | New TCP+TLS handshake every time; slower than synchronous code | Create one client and use it for the whole batch |
| Sharing a list between threads without a lock | Random wrong results, different on every run | Use a `threading.Lock`, a `queue.Queue`, or give each thread its own data |
| Using `ProcessPoolExecutor` with a lambda or a local function | `AttributeError: Can't pickle local object` | Use module-level functions and picklable arguments only |
| Missing `if __name__ == "__main__":` with processes on Windows/macOS | `RuntimeError: freeze_support() argument ...` or an infinite process spawn | Always guard the pool creation with the main guard |
| Expecting threads to speed up pure calculations | No speedup at all, sometimes slower | Use `ProcessPoolExecutor` for CPU-bound work |
| Ignoring rate limits when firing 100 concurrent LLM calls | HTTP 429 responses, or your account is throttled | Cap concurrency with `asyncio.Semaphore(5)` |
| `except Exception` around an `await` | `CancelledError` is not caught (it is a `BaseException`) and the task ends in a broken state | Catch `asyncio.CancelledError` explicitly, clean up, and re-raise |
| `asyncio.gather` over 10 000 coroutines at once | Thousands of sockets open, the OS complains, memory spikes | Bound the batch size with a semaphore, or process in chunks |

---

## 🔗 Resources

- [asyncio — Python documentation](https://docs.python.org/3/library/asyncio.html) — the
  official guide to coroutines, tasks and the event loop.
- [Concurrency with async IO — Real Python](https://realpython.com/python-asyncio/) — a
  long, careful walk through `asyncio` with plenty of examples.
- [Threading in Python](https://realpython.com/python-threading/) — threads, locks and
  queues, explained from the ground up.
- [What Is the GIL?](https://realpython.com/python-gil/) — a clear account of what the
  Global Interpreter Lock does and does not stop.
- [concurrent.futures — Python documentation](https://docs.python.org/3/library/concurrent.futures.html)
  — the reference for `ThreadPoolExecutor`, `ProcessPoolExecutor` and futures.
- [httpx documentation](https://www.python-httpx.org/) — the modern HTTP client, both
  sync and async, with `MockTransport` for testing.
- [httpx — PyPI](https://pypi.org/project/httpx/) — installation and version history.
- [asyncio TaskGroup documentation](https://docs.python.org/3/library/asyncio-task.html)
  — structured concurrency in Python 3.11+.
- [An async LLM client](https://github.com/simonw/llm) — a small, readable command-line tool
  that calls LLMs, including streaming, to see async HTTP done in real code.
- [Developing with asyncio — Python documentation](https://docs.python.org/3/library/asyncio-dev.html)
  — the official guide to writing async code well, including the patterns and the pitfalls.
- [httpx on GitHub](https://github.com/encode/httpx) — the source, changelog and issue
  tracker for the modern HTTP client.
- [Python free-threaded builds](https://docs.python.org/3/howto/free-threading-python.html)
  — the official guide to the experimental no-GIL build in Python 3.13+.

---

## ➡️ Next

- [16 — Practice projects](16-practice-projects.md) — eight guided projects that put
  everything from this course together, from a command line tool to a working API client.

**← Previous:** [14 — Standard library](14-standard-library.md)
