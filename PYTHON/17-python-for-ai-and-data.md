# Python for AI and Data

> **⏱️ Time:** ~45 minutes
> **📚 Prereqs:** [14 — Standard library](14-standard-library.md), [15 — Concurrency and async](15-concurrency-and-async.md)
> **🎯 By the end you can:** write the three kinds of Python that every AI project is made of — data
> code, API code, and the glue that holds them together

---

Everything so far taught you the *programming language*. This chapter shows you the *job*. Almost
every AI project you will ever work on is built from the same three layers, and you now have all the
Python you need to write them.

```text
┌─────────────────────────────────────────────────────────┐
│  LAYER 3 — APPLICATION                                   │
│  prompts, agents, evaluation, the thing a user sees     │
├─────────────────────────────────────────────────────────┤
│  LAYER 2 — MODELS & SERVICES                             │
│  LLM API calls, embeddings, retrieval, tool use         │
├─────────────────────────────────────────────────────────┤
│  LAYER 1 — DATA                                          │
│  loading, cleaning, slicing, batching, feature building  │
└─────────────────────────────────────────────────────────┘
```

The bad news: layers 1 and 2 are where most AI code is actually written, and most of it is plain
Python with a library bolted on. The good news: you already know how to write plain Python.

This chapter is a bridge, not a new course. Step 3 of this repository covers data management
properly, and Steps 7 to 10 cover the model layers. Today we just want you to see the shape of the
work and be able to write it.

---

## Why this matters for AI engineering

An AI engineer is someone who can move a piece of data from a file, through a model, into a
product, reliably, and know which of those three steps broke when it does.

That means the skill is not "call the API". It is:

- getting the data into a clean, well-typed shape before the model ever sees it,
- calling the API **defensively** — with timeouts, retries and rate-limit handling, because
  every API will eventually time out on you,
- and structuring the code so that when the model returns something unexpected, you can tell
  whether the data, the prompt, or the model was at fault.

All three of those are ordinary Python problems wearing an AI hat. That is good news.

---

## 1. The shape of an AI codebase

Before any code, look at the folder structure. Almost every serious AI project looks like this:

```text
my-ai-app/
├── pyproject.toml
├── .env                     # API keys (never committed)
├── .env.example             # the same file with blank values (committed)
├── src/
│   └── my_ai_app/
│       ├── __init__.py
│       ├── config.py        # reads settings from the environment
│       ├── llm.py           # the LLM client: one function, one job
│       ├── prompts.py       # prompt templates as plain strings
│       ├── data.py          # loading and cleaning
│       └── pipeline.py      # wires the layers together
└── tests/
    ├── test_data.py
    └── test_llm.py          # the LLM call is mocked, never real
```

Three observations that will save you weeks:

1. **`llm.py` is small.** One function that takes a prompt and returns text. If your LLM client is
   400 lines, you have an architecture problem, not a feature.
2. **Prompts are strings in a file**, not string literals scattered through your code. You will edit
   them a hundred times; you want them easy to find and easy to diff.
3. **Tests never call the real API.** They mock it. You will learn how in
   [file 13](13-testing.md); this chapter shows the pattern in practice.

---

## 2. Layer 1: data with NumPy and pandas

If you have ever done matrix maths, NumPy will feel immediately familiar. If you have ever
manipulated a spreadsheet, pandas will feel familiar. Both are libraries you `pip install`; neither
is part of the language.

### NumPy: arrays and vectorisation

A NumPy array is a grid of numbers that can do maths on **all at once**. That "all at once" is
called vectorisation, and it is the single idea you need.

```python
import numpy as np

# A plain Python list of numbers
prices = [10.0, 12.5, 9.99, 20.0]

# The same data as a NumPy array
arr = np.array(prices)

print("shape:", arr.shape)      # (4,) -> 4 values in 1 dimension
print("dtype:", arr.dtype)      # float64 -> numbers stored as 64-bit floats
print("mean:", arr.mean())      # 13.12...
print("total:", arr.sum())

# Vectorised: multiply EVERY element at once, no loop
with_tax = arr * 1.2
print("with tax:", with_tax)

# Compare a vector to a scalar -> a boolean array
expensive = arr > 10.0
print("expensive:", expensive)

# Boolean indexing: give me only the expensive ones
print("expensive prices:", arr[expensive])
```

The loop version of the third line would be:

```python
prices = [10.0, 12.5, 9.99, 20.0]

total = 0.0
for price in prices:
    total += price
print("total:", total)
```

Same answer. The vectorised one is faster, shorter, and — this is the important part — **less
likely to contain a bug**, because there is no index bookkeeping for you to get wrong.

### Broadcasting: the rule that confuses everyone

NumPy lets arrays of different shapes work together by "stretching" the smaller one. This is called
broadcasting, and it is why you can add a scalar to a whole array without writing a loop.

```python
import numpy as np

# A 3x3 matrix: 3 students, 3 exam scores
scores = np.array([
    [80, 90, 70],
    [60, 75, 85],
    [95, 88, 92],
])

# Shape (3, 3)
print("shape:", scores.shape)

# A single "weight" for each exam (1, 3) - broadcast across all 3 students
exam_weights = np.array([0.2, 0.3, 0.5])
weighted = scores * exam_weights
print("weighted row 1:", weighted[0])

# One bonus point for everyone (scalar) - broadcast across everything
bonused = scores + 1
print("row 1 after bonus:", bonused[0])

# Mean of each student's row -> shape (3,), one average per student
print("per-student average:", scores.mean(axis=1))

# Mean of each exam column -> shape (3,), one average per exam
print("per-exam average:", scores.mean(axis=0))
```

`axis=1` means "collapse along the rows" (giving you one number per row). `axis=0` means "collapse
along the columns". Getting these the wrong way round is the most common NumPy mistake. When in
doubt, print the shape after every operation.

### pandas: DataFrames

A `DataFrame` is a table: rows, columns, and named columns with their own types. If you have used
Excel, you already have the mental model.

```python
import pandas as pd

# Build a table from a list of records (this is what JSON looks like)
records = [
    {"model": "gpt-4o-mini",       "provider": "openai",    "cost_per_1k_in": 0.15},
    {"model": "claude-sonnet-4",    "provider": "anthropic", "cost_per_1k_in": 3.00},
    {"model": "gpt-4o",            "provider": "openai",    "cost_per_1k_in": 2.50},
    {"model": "llama-3.3-70b",     "provider": "meta",     "cost_per_1k_in": 0.59},
]

df = pd.DataFrame(records)

print(df)
print()
print("columns:", list(df.columns))
print("shape:", df.shape)

# Filter: keep rows where a condition is true
cheap = df[df["cost_per_1k_in"] < 1.0]
print("\ncheap models:")
print(cheap[["model", "cost_per_1k_in"]])

# Group and aggregate
by_provider = df.groupby("provider")["cost_per_1k_in"].agg(["count", "mean"])
print("\nby provider:")
print(by_provider)

# Sort
print("\ncheapest first:")
print(df.sort_values("cost_per_1k_in")[["model", "cost_per_1k_in"]].to_string(index=False))
```

That `to_string(index=False)` trick is worth memorising: it prints a clean table without the
awkward index column, which makes output much easier to read in a terminal or a log.

### The JSONL format you will meet constantly

Training data, evaluation results, LLM traces and most "big" datasets are stored as
**JSON Lines**: one JSON object per line. It is not valid JSON as a whole, so `json.load` will
fail on it — you read it line by line.

```python
import json

import pandas as pd

# Imagine this is 'traces.jsonl'
sample_lines = [
    '{"id": 1, "question": "What is Python?", "answer": "A programming language."}',
    '{"id": 2, "question": "What is an API?", "answer": "An interface to a service."}',
    '{"id": 3, "question": "What is JSON?", "answer": "A text data format."}',
]

records = []
for line in sample_lines:
    if line.strip():                      # skip blank lines
        records.append(json.loads(line))

for record in records:
    print(f"{record['id']}: {record['question']} -> {record['answer']}")

# Turn a list of records into a DataFrame in one line
df = pd.DataFrame(records)
print()
print(df.dtypes)
print(df.head())
```

A real file might be 100 GB. You do not load it. You stream it, and you filter as you go:

```python
import json

def read_jsonl(path, limit=None):
    """Stream a JSONL file, optionally stopping after `limit` records."""
    with open(path, "r", encoding="utf-8") as handle:
        for count, line in enumerate(handle):
            if limit is not None and count >= limit:
                break
            line = line.strip()
            if line:
                yield json.loads(line)

# In real use:
# for record in read_jsonl("huge.jsonl", limit=1000):
#     process(record)
print("generator defined - call it with a real path to stream a file")
```

`yield` (from [file 07](07-comprehensions-and-iterators.md)) is what makes this safe for huge
files: only one record is in memory at a time.

---

## 3. Layer 2: calling APIs defensively

This is the part where most beginner AI code breaks in production.

### The anatomy of an HTTP request

```python
import requests

# The four things you always need:
#   url      - WHERE
#   params   - the query string (filters, page numbers, search terms)
#   headers  - WHO you are (auth, content type)
#   json     - the request body (what you are sending)
#
# This calls a real public API. It needs a network connection, and it is
# wrapped in try/except so that a flaky network can never crash your program.

try:
    response = requests.get(
        "https://api.github.com/repos/python/cpython",
        headers={"Accept": "application/vnd.github+json"},
        timeout=10,                    # ALWAYS set a timeout
    )
except requests.RequestException as error:
    print("Network problem:", error)
else:
    print("status code:", response.status_code)          # 200 means success
    print("remaining calls:", response.headers.get("X-RateLimit-Remaining"))

    if response.ok:
        repo = response.json()
        licence = (repo.get("license") or {}).get("spdx_id", "unknown")
        print(f"{repo['full_name']}: {repo['stargazers_count']} stars, "
              f"{repo['forks_count']} forks, licence {licence}")
    else:
        # 401 = bad key, 403/429 = blocked or rate limited, 5xx = their problem
        print("Error body:", response.text[:200])
```

Three rules that will save you from a bad day:

1. **Always pass `timeout=`.** The default is *no timeout*, which means a hung request can hang your
   program forever. This is the single most common cause of "my script just stopped".
2. **Always check `response.status_code`.** A 200 is success; a 401 means bad key; a 429 means you
   hit a rate limit; a 500 means their problem.
3. **Never put an API key in your source code.** Read it from the environment:

```python
import os

# Set it once per terminal session:  export OPENAI_API_KEY="sk-..."
# On Windows PowerShell:              $env:OPENAI_API_KEY="sk-..."
api_key = os.environ.get("OPENAI_API_KEY")

if not api_key:
    print("No API key found. Set OPENAI_API_KEY in your environment.")
else:
    print(f"Found a key that starts with {api_key[:7]}...")

print("base url:", os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"))
```

### Retries with exponential backoff

If a request fails because of a transient network problem, the correct response is to **wait and try
again** — with a longer wait each time, so you do not hammer the service. This is called exponential
backoff.

```python
import random
import time

def call_with_retry(operation, attempts=3, base_delay=1.0):
    """Run `operation`, retrying on failure with exponential backoff."""
    last_error = None

    for attempt in range(attempts):
        try:
            return operation()
        except Exception as error:           # noqa: BLE001 - a real retry policy catches broadly
            last_error = error
            if attempt == attempts - 1:
                break                          # last attempt, give up
            delay = base_delay * (2 ** attempt)
            delay += random.uniform(0, 0.1)   # jitter, so clients do not sync up
            print(f"attempt {attempt + 1} failed ({error}); retrying in {delay:.2f}s")
            time.sleep(delay)

    raise last_error

# A fake flaky operation so the example runs offline
attempts_made = {"count": 0}

def flaky_operation():
    attempts_made["count"] += 1
    if attempts_made["count"] < 3:
        raise ConnectionError("network hiccup")
    return "success on attempt " + str(attempts_made["count"])

result = call_with_retry(flaky_operation, attempts=4, base_delay=0.05)
print("result:", result)
```

Real code narrows the `except` clause to the failures that are actually worth retrying (a timeout, a
`429`, a `502`). Retrying a `400 Bad Request` is pointless — the request will never succeed.

### Rate limits and pagination

APIs rarely return everything at once. They give you a page, and a link to the next page.

```python
# The shape of pagination, without hitting a real API
page = 1
results_per_page = 20
total_items = 57
total_pages = (total_items + results_per_page - 1) // results_per_page   # integer ceiling

print(f"{total_items} items across {total_pages} pages")
for page_number in range(1, total_pages + 1):
    print(f"  fetching page {page_number} ...")

# The arithmetic matters: ceiling division
#   (57 + 20 - 1) // 20  ==  3
#   57 // 20            ==  2   <-- would silently drop the last page
```

---

## 4. Layer 2: talking to an LLM

An LLM API is a regular HTTP API with an unusual payload. The shape is always the same:

```python
# The shape of an LLM call, with a fake local model so it runs offline.
# The real thing differs only in the URL, the headers and the model name.

class FakeLLM:
    """Stands in for a real LLM client. Same interface, no network."""

    def __init__(self, model="fake-model"):
        self.model = model
        self.call_count = 0

    def complete(self, prompt, temperature=0.0):
        self.call_count += 1
        answer = f"[{self.model}] received {len(prompt)} characters"
        return {"text": answer, "model": self.model, "prompt_chars": len(prompt)}


llm = FakeLLM()

messages = [
    {"role": "system", "content": "You are a precise assistant. Answer in one sentence."},
    {"role": "user", "content": "What is retrieval-augmented generation?"},
]

response = llm.complete("\n".join(m["content"] for m in messages), temperature=0.0)
print(response["text"])
print("model:", response["model"])

# With a real SDK the shape is nearly identical:
#
#   from openai import OpenAI
#   client = OpenAI()                       # reads OPENAI_API_KEY from the environment
#   response = client.chat.completions.create(
#       model="gpt-4o-mini",
#       messages=messages,
#       temperature=0.0,
#   )
#   print(response.choices[0].message.content)
#
# The SDK adds retry logic, timeouts and type hints. The idea does not change.
```

Three details of that shape matter:

- **Messages have roles.** `system` sets behaviour, `user` asks, `assistant` replies. A chat
  history is just a list of these dictionaries.
- **Temperature is a randomness dial.** `0.0` is as deterministic as the model can be — use it for
  anything you test or evaluate. Higher values are for creative writing.
- **You must keep the message history** across turns. The API is stateless; the conversation lives
  in the list you send.

### Prompt templates belong in variables

```python
# A template is just a string. Put them in one place, not scattered through the code.
SUMMARY_PROMPT = """Summarise the following text in exactly one sentence.

Text:
{text}

Summary:"""

REWRITE_PROMPT = """Rewrite the text below so a {audience} can understand it.
Keep it under {max_words} words.

Text:
{text}

Rewritten text:"""

text = "Vector databases store embeddings and answer similarity queries."

# .format() is fine for simple templates
print(SUMMARY_PROMPT.format(text=text))
print()
print(REWRITE_PROMPT.format(text=text, audience="a ten-year-old", max_words=30))
```

For anything that goes to a real model, use the `string.Template` style with explicit
placeholders, or a proper templating library — because user input containing a `{` will crash
`.format()`. That is a real bug you will hit.

### Streaming

A long answer can arrive token by token. Streaming lets you show it as it arrives instead of
waiting for the whole thing.

```python
# Streaming, simulated with a fake model
class StreamingFakeLLM:
    def stream(self, prompt, chunk_size=4):
        text = "Python is a programming language used widely in AI engineering."
        for start in range(0, len(text), chunk_size):
            yield text[start:start + chunk_size]      # a generator: yields as it goes

print("Streaming response:")
for chunk in StreamingFakeLLM().stream("Tell me about Python"):
    print(chunk, end="", flush=True)                   # flush=True forces the print out now
print("\n")
```

`flush=True` matters in a real app: without it, Python buffers output and the user sees nothing
until the process ends. You learned generators in
[file 07](07-comprehensions-and-iterators.md); this is one of their most practical uses.

---

## 5. Embeddings and similarity, from first principles

An **embedding** is a list of numbers that represents the *meaning* of some text. Texts with
similar meanings have similar number lists. This is the foundation of retrieval, RAG, and semantic
search.

You can understand the whole idea with no API and no model, by building "embeddings" yourself using
word counts. It is not as good as a real model, but the *mechanics* are identical.

```python
import math
from collections import Counter

# Words that appear everywhere and therefore tell you nothing.
STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "of", "to", "in", "on", "and", "or",
    "how", "do", "i", "my", "you", "it", "that", "this", "for", "with",
}

def stem(word):
    """Crude plural stripping: 'embeddings' -> 'embedding', 'numbers' -> 'number'."""
    if word.endswith("s") and not word.endswith("ss") and len(word) > 3:
        return word[:-1]
    return word

def tokenize(text):
    """Lowercase, strip punctuation, drop stop words, stem the rest."""
    cleaned = "".join(ch if ch.isalnum() or ch.isspace() else " " for ch in text.lower())
    return [stem(w) for w in cleaned.split() if w not in STOP_WORDS]

def bag_of_words_embedding(text, vocabulary):
    """Turn text into a fixed-length vector of word counts."""
    counts = Counter(tokenize(text))
    return [float(counts.get(word, 0)) for word in vocabulary]

def cosine_similarity(a, b):
    """How close are two vectors? 1.0 = identical direction, 0.0 = unrelated."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)

docs = {
    "doc_a": "Python is a programming language used to write code.",
    "doc_b": "A vector database stores embeddings for semantic search.",
    "doc_c": "Numbers are used in mathematics to count and measure things.",
}

# In reality a model has tens of thousands of dimensions. Here we build the
# vocabulary from the documents themselves, which is the simplest possible choice.
vocabulary = sorted({word for text in docs.values() for word in tokenize(text)})
print("vocabulary:", vocabulary)

vectors = {name: bag_of_words_embedding(text, vocabulary) for name, text in docs.items()}

query = "how do I store vector numbers for search"
query_vector = bag_of_words_embedding(query, vocabulary)

print("\nsimilarity to query:")
scored = []
for name, vector in vectors.items():
    score = cosine_similarity(query_vector, vector)
    scored.append((score, name))
    print(f"  {name}: {score:.3f}")

scored.sort(reverse=True)
print("\nbest match :", scored[0][1])
print("runner-up  :", scored[1][1])
print("no match   :", scored[2][1])
```

Three things to take from this:

1. **Cosine similarity ignores magnitude.** It compares *direction*, not size. A long document and a
   short one with the same vocabulary point the same way.
2. **The mechanism is identical at scale.** A real embedding model produces a 1,536-number vector
   per text with the same properties: similar meanings, similar directions. Swapping the bag-of-words
   for a real model changes the quality, not the code.
3. **This naive version has obvious weaknesses**, and knowing what they are tells you what a real
   embedding model is doing for you. There is no **IDF** weighting, so a word that appears in every
   document counts as much as a rare, meaningful one. There is no understanding of synonyms — "car"
   and "automobile" share nothing here. And the vocabulary is fixed, so any word it never saw is
   invisible. A real model has learned thousands of dimensions of meaning that capture all of this.

---

## 6. A miniature retrieval system (no external dependencies)

Put it all together: load documents, embed them, embed the query, score, return the best passages.
This is the *core loop of RAG*, in about 40 lines and zero dependencies.

```python
import math
from collections import Counter

# --- The corpus -------------------------------------------------------
CORPUS = {
    "python": "Python is a high-level programming language. You write code with it.",
    "retrieval": "Retrieval finds the most relevant documents for a given query.",
    "embeddings": "Embeddings are lists of numbers that capture the meaning of text.",
    "agents": "An agent is a program that plans, calls tools, and checks its own results.",
    "testing": "Testing means running your code on known inputs to check that the answers are correct.",
}

STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "of", "to", "in", "on", "and", "or",
    "how", "do", "i", "my", "you", "it", "that", "this", "for", "with",
}

def stem(word):
    """Crude plural stripping: 'embeddings' -> 'embedding', 'numbers' -> 'number'."""
    if word.endswith("s") and not word.endswith("ss") and len(word) > 3:
        return word[:-1]
    return word

def tokenize(text):
    """Lowercase, strip punctuation, drop stop words, stem the rest."""
    cleaned = "".join(ch if ch.isalnum() or ch.isspace() else " " for ch in text.lower())
    return [stem(w) for w in cleaned.split() if w not in STOP_WORDS]

def build_vocabulary(documents):
    words = set()
    for text in documents.values():
        words.update(tokenize(text))
    return sorted(words)

def embed(text, vocabulary):
    counts = Counter(tokenize(text))
    return [float(counts.get(word, 0)) for word in vocabulary]

def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0

# --- Index once, at startup -------------------------------------------
vocabulary = build_vocabulary(CORPUS)
index = {name: embed(text, vocabulary) for name, text in CORPUS.items()}

# --- Query ------------------------------------------------------------
def retrieve(query, top_k=2):
    query_vector = embed(query, vocabulary)
    scores = [(cosine(query_vector, vector), name) for name, vector in index.items()]
    scores.sort(reverse=True)
    return scores[:top_k]

def answer(query, top_k=2):
    hits = retrieve(query, top_k)
    if not hits or hits[0][0] == 0.0:
        return "I do not have anything relevant to that question."
    best_score, best_name = hits[0]
    return f"Based on '{best_name}' (score {best_score:.2f}): {CORPUS[best_name]}"

print(answer("what is an embedding?"))
print()
print(answer("how do I check my code?"))
print()
print(answer("what is the capital of Peru?"))
```

That last line is the important one: a retrieval system that always answers something is a
*dangerous* system. Real ones return "no good match" and let the model say "I don't know". Deciding
when **not** to answer is a core part of the job.

---

## 7. Layer 3: the glue

### Cost estimation

LLM calls cost money, and the maths is simple enough to do in your head.

```python
def estimate_cost(input_tokens, output_tokens, price_per_1k_input, price_per_1k_output):
    """Prices are per 1,000 tokens (tokens are roughly 0.75 * words)."""
    input_cost = (input_tokens / 1000) * price_per_1k_input
    output_cost = (output_tokens / 1000) * price_per_1k_output
    return input_cost + output_cost


def count_tokens_roughly(text):
    """A rough token estimate: ~4 characters per token for English."""
    return max(1, len(text) // 4)


prompt = "Explain retrieval-augmented generation to a software engineer in three sentences."
response_text = "RAG retrieves relevant documents and passes them to a language model as context, so answers are grounded in your own data rather than only in the model's training. This reduces hallucinations and lets you use private or up-to-date information. The tradeoff is latency and the cost of the retrieval step."

input_tokens = count_tokens_roughly(prompt)
output_tokens = count_tokens_roughly(response_text)

print(f"input tokens:  {input_tokens}")
print(f"output tokens: {output_tokens}")
print(f"estimated cost: ${estimate_cost(input_tokens, output_tokens, 0.15, 0.60):.5f}")
print(f"cost of 10,000 such calls: ${estimate_cost(input_tokens, output_tokens, 0.15, 0.60) * 10_000:.2f}")
```

Always log token usage. It is the difference between "the bill went up" and knowing exactly which
feature caused it.

### Configuration from the environment

```python
import os
from dataclasses import dataclass

@dataclass
class Settings:
    """Application settings, loaded from environment variables."""
    model: str = "gpt-4o-mini"
    temperature: float = 0.0
    max_tokens: int = 500
    api_key: str | None = None

    @classmethod
    def from_env(cls):
        return cls(
            model=os.environ.get("LLM_MODEL", "gpt-4o-mini"),
            temperature=float(os.environ.get("LLM_TEMPERATURE", "0.0")),
            max_tokens=int(os.environ.get("LLM_MAX_TOKENS", "500")),
            api_key=os.environ.get("OPENAI_API_KEY"),
        )

    @property
    def is_configured(self):
        return bool(self.api_key)

settings = Settings.from_env()
print("model      :", settings.model)
print("temperature:", settings.temperature)
print("max tokens :", settings.max_tokens)
print("configured :", settings.is_configured)
```

Note the `| None` type and the `str | None` — [file 11](11-type-hints-and-modern-python.md) pays
off here. Note also `from_env` as a classmethod: it is the factory for this object. That is the
pattern from [file 10](10-object-oriented-programming.md).

### Testing AI code without calling a model

This is the pattern that separates a hobby project from a professional one.

```python
# The unit under test: it takes a client and talks to it.
def summarise(client, text):
    response = client.complete("Summarise in one sentence: " + text)
    return response["text"].strip()


# A fake client that records what it was asked, and returns a canned answer.
class RecordingClient:
    def __init__(self, reply="a summary"):
        self.reply = reply
        self.prompts = []

    def complete(self, prompt, temperature=0.0):
        self.prompts.append(prompt)
        return {"text": self.reply}


# --- the test ---------------------------------------------------------
client = RecordingClient(reply="  Python is a programming language.  ")
result = summarise(client, "Python is a programming language.")

assert result == "Python is a programming language.", f"unexpected result: {result!r}"
assert len(client.prompts) == 1
assert client.prompts[0].startswith("Summarise in one sentence:")

print("all assertions passed")
print("prompt the client received:", client.prompts[0])
```

With `pytest` this becomes a `test_summarise` function, and you add `monkeypatch` or
`unittest.mock.patch` when the client is constructed inside the function rather than injected. The
principle is the same: **the function under test should not decide how to reach the model.** It
should receive a client and use it. That makes the test trivial and the code reusable.

---

## 8. What you have actually learned

Look at what that last file did. It used:

| Concept | Where you learned it |
|---|---|
| lists, dicts, functions, classes | [02](02-syntax-and-variables.md), [05](05-functions.md), [10](10-object-oriented-programming.md) |
| generators and `yield` for streaming | [07](07-comprehensions-and-iterators.md) |
| `json`, `csv`, file I/O, exceptions, logging | [09](09-file-io-and-errors.md) |
| type hints, dataclasses, `\| None` | [11](11-type-hints-and-modern-python.md) |
| `venv`, `pyproject.toml`, `ruff`, `mypy` | [12](12-environments-and-tooling.md) |
| `pytest` and mocking | [13](13-testing.md) |
| `pathlib`, `collections`, `math`, `statistics` | [14](14-standard-library.md) |
| `asyncio` and `httpx` for concurrent API calls | [15](15-concurrency-and-async.md) |
| environment variables and secrets | [12](12-environments-and-tooling.md) |

There is no "AI-specific Python". There is Python, used well, in a particular domain. That is the
entire insight, and it is why this course started at absolute zero.

---

## 🧪 Try it yourself

### Exercise 1 — a price calculator

Write a function `total_cost(models, usage)` where `models` is a list of dicts with keys `name`,
`price_per_1k_in`, `price_per_1k_output` and `usage` is a dict mapping model name to a dict with
`in_tokens` and `out_tokens`. Return a dict of model name to total cost, and the grand total.

<details>
<summary>Hint</summary>

Loop over the models, look up the usage by name, and call the same `estimate_cost` logic you wrote
above. Handle a model in `models` that has no entry in `usage` (treat it as zero tokens) — that is
the kind of edge case real data has.

</details>

<details>
<summary>Solution</summary>

```python
def total_cost(models, usage):
    costs = {}
    for model in models:
        name = model["name"]
        tokens = usage.get(name, {"in_tokens": 0, "out_tokens": 0})
        cost = (tokens["in_tokens"] / 1000) * model["price_per_1k_in"]
        cost += (tokens["out_tokens"] / 1000) * model["price_per_1k_output"]
        costs[name] = cost
    costs["TOTAL"] = sum(costs.values())
    return costs


models = [
    {"name": "small", "price_per_1k_in": 0.15, "price_per_1k_output": 0.60},
    {"name": "big", "price_per_1k_in": 3.00, "price_per_1k_output": 15.00},
]
usage = {"small": {"in_tokens": 5000, "out_tokens": 1000}}

print(total_cost(models, usage))
```

</details>

### Exercise 2 — chunk a long document

Write `chunk_text(text, size)` that splits a string into chunks of at most `size` characters,
splitting only at word boundaries. Return a list of chunks. Then write `chunk_text_by_sentences`
that splits on `.` and `!` and `?` instead.

<details>
<summary>Hint</summary>

Use `text.split()` to get words, then accumulate words into a buffer until adding the next word
would exceed `size`. For the sentence version, use `re.split(r"(?<=[.!?])\s+", text)`.

</details>

<details>
<summary>Solution</summary>

```python
import re

def chunk_text(text, size):
    chunks = []
    current = []
    for word in text.split():
        candidate = " ".join(current + [word])
        if len(candidate) > size and current:
            chunks.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        chunks.append(" ".join(current))
    return chunks


def chunk_text_by_sentences(text, size=200):
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks = []
    current = []
    for sentence in sentences:
        candidate = " ".join(current + [sentence])
        if len(candidate) > size and current:
            chunks.append(" ".join(current))
            current = [sentence]
        else:
            current.append(sentence)
    if current:
        chunks.append(" ".join(current))
    return chunks


sample = ("Retrieval augmented generation grounds a model in your own documents. "
          "It reduces hallucinations. It adds latency. It costs money per query. "
          "Always evaluate before you ship it.")

print(chunk_text(sample, 60))
print()
print(chunk_text_by_sentences(sample, 80))
```

</details>

### Exercise 3 — add a cache to the fake LLM

Make `FakeLLM` cache its answers by prompt, so asking the same question twice only "calls" the
model once. Print how many real calls were made.

<details>
<summary>Hint</summary>

Add a `self._cache = {}` to `__init__`. In `complete`, check the cache first; on a miss, compute
the answer, store it, and increment `call_count` only on a miss.

</details>

<details>
<summary>Solution</summary>

```python
class CachingLLM:
    def __init__(self, model="fake-model"):
        self.model = model
        self.call_count = 0
        self._cache = {}

    def complete(self, prompt, temperature=0.0):
        key = (prompt, temperature)
        if key in self._cache:
            return self._cache[key]
        self.call_count += 1
        answer = {"text": f"[{self.model}] answered {len(prompt)} chars",
                  "model": self.model, "prompt_chars": len(prompt)}
        self._cache[key] = answer
        return answer


llm = CachingLLM()
llm.complete("hello")
llm.complete("hello")
llm.complete("goodbye")
print("real calls made:", llm.call_count)   # 2
```

</details>

### Exercise 4 — add a score threshold

Right now `retrieve` always returns `top_k` results, even if every score is `0.0`. Change it to
take a `min_score` parameter and return only hits at or above it. Then make `answer` use a threshold
of `0.1` instead of special-casing `0.0`.

<details>
<summary>Hint</summary>

Filter the `scores` list before slicing it, and remember that `min_score` should have a default so
existing calls still work.

</details>

<details>
<summary>Solution</summary>

```python
# A self-contained mini retriever, so this file runs on its own.
import math
from collections import Counter

CORPUS = {
    "python": "Python is a high-level programming language. You write code with it.",
    "embeddings": "Embeddings are lists of numbers that capture the meaning of text.",
    "testing": "Testing means running your code on known inputs to check that the answers are correct.",
}
STOP_WORDS = {"a", "an", "the", "is", "are", "of", "to", "in", "and", "or", "how", "do", "i"}

def tokenize(text):
    cleaned = "".join(c if c.isalnum() or c.isspace() else " " for c in text.lower())
    return [w[:-1] if w.endswith("s") and not w.endswith("ss") and len(w) > 3 else w
            for w in cleaned.split() if w not in STOP_WORDS]

VOCAB = sorted({w for t in CORPUS.values() for w in tokenize(t)})
INDEX = {name: [float(Counter(tokenize(text)).get(w, 0)) for w in VOCAB]
         for name, text in CORPUS.items()}

def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


def retrieve(query, top_k=2, min_score=0.0):
    query_vector = [float(Counter(tokenize(query)).get(w, 0)) for w in VOCAB]
    scores = [(cosine(query_vector, vec), name) for name, vec in INDEX.items()]
    scores = [pair for pair in scores if pair[0] >= min_score]
    scores.sort(reverse=True)
    return scores[:top_k]


def answer(query, top_k=2):
    hits = retrieve(query, top_k, min_score=0.1)
    if not hits:
        return "I do not have anything relevant to that question."
    best_score, best_name = hits[0]
    return f"Based on '{best_name}' (score {best_score:.2f}): {CORPUS[best_name]}"


print(answer("what is an embedding?"))
print(answer("what is the capital of Peru?"))
```

A threshold is the simplest form of a **relevance guard**, and it is one of the most important
knobs in any real retrieval system. Tune it against a labelled evaluation set, not by vibes.

</details>

### Exercise 5 — a mini evaluation harness

Write `evaluate(questions, expected_keywords)` that runs your `answer()` function over a list of
questions, checks whether every expected keyword appears in the answer (case-insensitively), and
returns a score out of 1.0 plus a list of failures. Use it on three questions from the corpus above.

<details>
<summary>Hint</summary>

A simple `all(keyword.lower() in answer.lower() for keyword in expected_keywords)` gives you a
boolean per question. Average the booleans for the score, and collect the failures in a list.

</details>

<details>
<summary>Solution</summary>

```python
# A self-contained mini retriever, so this file runs on its own.
import math
from collections import Counter

DOCS = {
    "python": "Python is a high-level programming language. You write code with it.",
    "embeddings": "Embeddings are lists of numbers that capture the meaning of text.",
    "testing": "Testing means running your code on known inputs to check that the answers are correct.",
}
VOCAB = sorted({w for t in DOCS.values() for w in t.lower().split()})
INDEX = {name: [float(Counter(text.lower().split()).get(w, 0)) for w in VOCAB]
         for name, text in DOCS.items()}


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


def answer(question):
    query = [float(Counter(question.lower().split()).get(w, 0)) for w in VOCAB]
    scores = sorted(((cosine(query, vec), name) for name, vec in INDEX.items()), reverse=True)
    if not scores or scores[0][0] == 0.0:
        return "I do not have anything relevant to that question."
    return DOCS[scores[0][1]]


def evaluate(questions, expected_keywords):
    passed = 0
    failures = []
    for question, keywords in zip(questions, expected_keywords):
        result = answer(question).lower()
        missing = [kw for kw in keywords if kw.lower() not in result]
        if not missing:
            passed += 1
        else:
            failures.append((question, missing))
    score = passed / len(questions) if questions else 0.0
    return score, failures


questions = [
    "what is an embedding?",
    "how do I check my code?",
    "what is the capital of Peru?",
]
expected = [
    ["number", "meaning"],
    ["code", "check"],
    ["do not have"],
]

score, failures = evaluate(questions, expected)
print(f"score: {score:.0%}")
for question, missing in failures:
    print(f"  FAILED: {question} - missing {missing}")
```

</details>

---

## ✅ Checkpoint

1. What are the three layers of an AI codebase, from bottom to top?
   <details><summary>Answer</summary>Data (loading, cleaning, batching) → models and services (LLM
   calls, embeddings, retrieval, tools) → application (prompts, agents, evaluation, the user-facing
   product).</details>

2. Why should you always pass `timeout=` to an HTTP request?
   <details><summary>Answer</summary>Because the default is no timeout at all, so a hung request
   hangs your program forever. It is the most common cause of a script that "just stopped".</details>

3. What does exponential backoff do, and why is there jitter in it?
   <details><summary>Answer</summary>It waits longer between each retry (doubling each time) so you
   do not hammer a struggling service. The random jitter stops many clients from retrying in
   lockstep and overwhelming the service again.</details>

4. Which HTTP status code means "you are sending requests too fast"?
   <details><summary>Answer</summary>429 (Too Many Requests). It is usually worth retrying after
   waiting; a 400 Bad Request is not.</details>

5. What is the difference between `json.load` and reading a `.jsonl` file line by line?
   <details><summary>Answer</summary>A `.json` file is one JSON document, so `json.load` works. A
   `.jsonl` file is one JSON object per line, which is not valid JSON as a whole — you must read it
   line by line and call `json.loads` on each line.</details>

6. What does `yield` buy you when streaming a huge dataset?
   <details><summary>Answer</summary>It lets the function produce one record at a time, so only one
   record is ever in memory. Without it you would load the entire file into RAM first.</details>

7. What does cosine similarity compare?
   <details><summary>Answer</summary>Direction, not magnitude. Two vectors that point the same way
   score 1.0 even if one is much longer. It is why a one-sentence query can score highly against a
   long document.</details>

8. Why should a retrieval system be willing to say "I don't know"?
   <details><summary>Answer</summary>Because a system that always returns its best match will
   confidently answer from an irrelevant document. Refusing to answer when the top score is too low
   is a core part of building something trustworthy.</details>

9. How do you make a function that calls an LLM testable without an API key?
   <details><summary>Answer</summary>Inject the client: the function receives a client object and
    calls it, rather than constructing one itself. The test passes a fake client that records the
    prompt and returns a canned answer.</details>

10. What is the rough token count of a 400-character English string?
    <details><summary>Answer</summary>About 100 tokens, at roughly 4 characters per token. It is an
    estimate — real tokenisers vary — but it is accurate enough for cost projections.</details>

</details>

---

## 🐛 Common mistakes

| Mistake | What you see | Fix |
|---|---|---|
| No `timeout` on a request | The program hangs forever on a slow network | Always pass `timeout=10` (or similar) |
| Checking `response.json()` before the status code | A confusing `JSONDecodeError` on a 500 page | Check `response.status_code` first; use `response.raise_for_status()` |
| Hard-coding an API key in the source | The key leaks to GitHub and gets revoked | Read it from `os.environ`; commit a `.env.example`, never a `.env` |
| Retrying every exception forever | A 400 Bad Request is retried 5 times for no reason | Retry only transient errors: timeouts, 429, 502, 503 |
| Loading a huge JSONL file with `readlines()` | The process runs out of memory | Stream it line by line with a generator |
| Using `.format()` on a template containing user text | A `KeyError` or a crash from a stray `{` | Use `str.format_map` with a fixed dict, or a template library |
| Assuming a retrieval hit is a good hit | A confident, wrong answer | Set a score threshold and return "no match" below it |
| Testing by calling the real API | Slow, flaky, costs money, needs a key | Inject a fake client and assert on the recorded prompt |
| Forgetting `flush=True` when streaming | The user sees nothing until the whole response arrives | `print(chunk, end="", flush=True)` |
| Sharing one mutable default across requests | One user's data leaks into another's | Build the payload inside the function, not in the defaults |
| Log-nothing, cost-someone-else | The bill arrives and nobody knows why | Log token counts and estimated cost on every call |
| Using `df.iterrows()` for heavy lifting | Gloriously slow on a large frame | Prefer vectorised ops or `itertuples()` |

---

## 🔗 Resources

- [OpenAI API documentation](https://platform.openai.com/docs/overview) — the API reference for
  OpenAI models, including the chat, embeddings and streaming endpoints.
- [OpenAI Python SDK](https://github.com/openai/openai-python) — the official Python client. Its
  source is short and well-written, so it is a good thing to read.
- [Anthropic API documentation](https://docs.anthropic.com/en/docs/intro-to-claude) — the reference
  for the Claude API.
- [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python) — the official Python
  client for Claude.
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/index) — thousands of
  pretrained models behind one Python API. The core of Step 8.
- [LiteLLM](https://pypi.org/project/litellm/) — one interface for calling many model providers,
  which is what you want the moment you need a fallback.
- [NumPy](https://pypi.org/project/numpy/) — the fast n-dimensional array library behind almost
  every AI framework.
- [pandas](https://pypi.org/project/pandas/) — DataFrames for tabular data. You will meet it
  properly in Step 3.
- [httpx](https://www.python-httpx.org/) — the modern HTTP client with first-class async support.
  Better than `requests` for new code.
- [requests](https://requests.readthedocs.io/en/latest/) — the classic HTTP library. Still
  everywhere, and still fine for synchronous code.
- [Chroma](https://pypi.org/project/chromadb/) — an embedding database for retrieval. The core of
  Step 9.
- [simonw/llm](https://github.com/simonw/llm) — a small, readable command-line tool for calling
  LLMs. Read its source to see how short this can be.

---

## ➡️ Next

- [**Resources**](resources.md) — the full curated link list for this step, including the standard
  library reference by task and the AI libraries you will need in Steps 3 and 7 to 10.
- **Then:** [DEVELOPER FOUNDATIONS](../DEVELOPER%20FOUNDATIONS/guide.md) — Git, GitHub, Linux,
  FastAPI and system design. Now that you can write Python, it is time to learn how professionals
  collaborate on it.

**← Previous:** [15 — Concurrency and async](15-concurrency-and-async.md)
