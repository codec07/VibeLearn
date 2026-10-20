# Zero to Mastery: AI Engineer / Agentic AI Developer

**A free, open-source, Markdown-first curriculum that takes you from "I have never written a line of
code" to "I can build AI systems that work in production."**

No video lectures. No paywall. No "10 hours of prerequisites". Just a well-ordered path, written in
plain English, with runnable examples at every step.

---

## Why this repository exists

Most AI courses start at "here is how to call the OpenAI API". By the time you reach that page you
are already assumed to be a competent programmer, and when you get stuck you have nobody to ask.

This repository goes the other way. It assumes **nothing**. It starts with what a variable is, and
ends with you building an agent system that calls tools, manages state and handles failures. Every
step depends only on the steps before it, and every step tells you exactly what you will be able to
build when you finish it.

The library you will use at the end (LangChain, LlamaIndex, PyTorch, scikit-learn, FastAPI) is the
easy part. The hard part is the thing nobody teaches: **the programmer's fundamentals**. That is
what this repository is for.

---

## The 10 steps

Each folder is one step. Each step contains a `guide.md` that tells you where to start, what you
need to know first, and what you will be able to build by the end.

| Step | Folder | What you will be able to do after it | Status |
|:-:|---|---|:-:|
| 1 | [**PYTHON**](PYTHON/guide.md) | Write, test, type and ship Python | **Complete** |
| 2 | [DEVELOPER FOUNDATIONS](DEVELOPER%20FOUNDATIONS/guide.md) | Use Git, GitHub, Linux, build APIs, design systems | _Upcoming_ |
| 3 | [DATA MANAGEMENT](DATA%20MANAGEMENT/guide.md) | Excel, SQL, NumPy, pandas, Matplotlib, Seaborn | _Upcoming_ |
| 4 | [MATHEMATICS (FOR AIML)](MATHEMATICS%20%28FOR%20AIML%29/guide.md) | Linear algebra, calculus, statistics | _Upcoming_ |
| 5 | [CLASSICAL MACHINE LEARNING](CLASSICAL%20MACHINE%20LEARNING/guide.md) | Train and evaluate classical models from scratch | _Upcoming_ |
| 6 | [ML PROJECTS](ML%20PROJECTS/guide.md) | Ship prediction, cancer-detection and stock models | _Upcoming_ |
| 7 | [DEEP LEARNING](DEEP%20LEARNING/guide.md) | Build neural networks and work with PyTorch | _Upcoming_ |
| 8 | [NLP & TRANSFORMERS](NLP%20&%20TRANSFORMERS/guide.md) | Tokenisation, attention, transformers, fine-tuning | _Upcoming_ |
| 9 | [GENERATIVE AI](GENERATIVE%20AI/guide.md) | Build RAG pipelines, evals and prompt systems | _Upcoming_ |
| 10 | [AGENTIC AI](AGENTIC%20AI/guide.md) | Build autonomous, tool-using agent systems | _Upcoming_ |

**Start here: [Step 1 - Python](PYTHON/guide.md).**

### Step 1 at a glance

| | |
|---|---|
| Chapters | 18 files, `00` to `17` |
| Reading time | ~119,000 words, roughly 17 hours of focused study |
| Code examples | **553 — every one executed and verified before publishing** |
| Test suites | 36 project tests plus per-chapter examples, all passing |
| Links | **234 external links checked, 0 broken** · 239 internal links, 0 broken |

The checks are not claims — they are scripts, and they are in this repository:

```bash
python tools/verify_blocks.py PYTHON/05-functions.md   # runs every code example
python tools/check_links.py .                          # checks internal links resolve
python tools/check_external_links.py .                 # checks external links still work
python tools/audit_structure.py .                      # checks every chapter has the same shape
```

---

## How this repository is organised

Every step folder follows the same structure, so you always know where you are:

```text
REPO/
├── README.md          <- you are here
├── CONTRIBUTING.md    <- how to help
├── tools/             <- the scripts that verify this repository
│   ├── verify_blocks.py        <- runs every code example in a chapter
│   ├── check_links.py          <- checks that internal links resolve
│   └── check_external_links.py <- checks that external links still work
├── STEP-FOLDER/
│   ├── guide.md      <- read this first: the roadmap for this step
│   ├── README.md     <- a one-line pointer to guide.md
│   ├── 01-topic.md   <- the chapters, in the order you should read them
│   ├── 02-topic.md
│   └── ...
│   └── resources.md  <- curated, verified links for the whole step
```

- **`guide.md`** — the focused guide for that step: where to start, what the prerequisites are, what
  you will be able to build at the end, and a table of contents with time estimates.
- **Numbered chapter files** — the actual teaching material. Read them in order; each one depends
  on the last.
- **`resources.md`** — official documentation, tools, courses and cheatsheets for that step, with
  every link checked before it was published.
- **`tools/`** — the scripts used to verify this repository. Every code example in every chapter
  is executed before it is published, and every link is checked.

Chapter files are written in pure Markdown so they render beautifully directly on GitHub — no site
build, no clone, no setup. Read them in your browser, and run the examples in your editor, side by
side.

---

## How to use it

1. **Open the folder for the step you are on.** Start with `PYTHON/guide.md`.
2. **Read one chapter at a time.** Do not binge. The order is load-bearing.
3. **Type every example yourself.** Do not copy-paste. Typing it is where the learning happens.
4. **Run the code and break it on purpose.** Python's error messages are part of the curriculum.
5. **Do the exercises.** Each chapter ends with hands-on exercises and a short checkpoint quiz.
6. **Use the resources at the end of each chapter** when you need a deeper reference.
7. **Skip what you already know.** Every `guide.md` has a "where to start if you already know X"
   table. Use it. There is no prize for reading things you know.

Every code example in this repository has been executed before it was published. If an example
breaks, it is a bug in the repository, not in your setup — please open an issue.

---

## Principles

- **Runnable or it does not ship.** Every code block is executed and verified. No pseudo-code
  pretending to be real code.
- **Links are checked.** No dead links, no link farms, no SEO padding. If a resource is worth your
  time, it is on the list; if it is not, it is not.
- **Free forever.** Everything here is open source and free to use. Paid tools appear only as
  clearly-marked optional extras.
- **Written for humans.** Plain language, every term defined on first use, no condescension, and no
  unexplained jargon.
- **Built in public, one step at a time.** Each step is finished and verified before the next one
  begins, so the curriculum is always coherent rather than a pile of half-written notes.

---

## Who this is for

- Complete beginners who want to understand code, not just copy it.
- Developers from another language who want to think in Python.
- People who want to move into AI/ML and keep getting stuck on the fundamentals.
- Working engineers who want a single, well-ordered path instead of ten conflicting tutorials.

## What you need

- A computer (Windows, macOS or Linux) and about 500 MB of free disk space.
- Curiosity and roughly 17 hours for Step 1, spread over a few weeks.
- No prior programming experience. Genuinely none.
- No budget. Everything referenced here is free.

---

## Contributing

This repository is built step by step, and every chapter is reviewed for correctness before it is
merged. If you want to help:

- **Spot a bug in an example.** Open an issue with the file name, the block, and what you saw.
- **Improve an explanation.** Open a pull request. Keep the tone consistent with the file you are
  editing and preserve the file's structure — the ⏱️/📚/🎯 header, the 🧪 exercises, the ✅
  checkpoint, the 🐛 common-mistakes table, the 🔗 resources and the ➡️ next link.
- **Add a resource.** Only if it is official, current, and genuinely useful. Explain in the pull
  request why it belongs there.

Please keep the audience in mind: a reader who has never programmed. Clarity beats cleverness.

## License

Released under the **MIT License**, so you can use, adapt and teach from this material freely.
Attribution is appreciated but not required.

---

**Ready? Open [PYTHON/guide.md](PYTHON/guide.md) and write your first line of Python.**
