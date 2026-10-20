# Contributing

This repository is a teaching resource. Every word matters, and so does every code example. Thank
you for helping.

---

## The one rule

**Write for someone who has never programmed.**

That reader is smart and curious, but they do not know what a decorator is, they have never seen a
traceback, and they will hit their first error in the first ten minutes. Every sentence you write
should make their next step clearer and never make them feel stupid.

Clarity beats cleverness. A plain sentence that a beginner understands is worth more than an
elegant one they do not.

---

## Before you open a pull request

Run these checks on the file you changed. They are the same checks the repository promises.

### 1. Every code block must run

Each `python` fenced block in a chapter must execute without error on Python 3.12+.

```bash
# extract and run every python block from a chapter
python tools/verify_blocks.py PYTHON/05-functions.md
```

If a block deliberately cannot run (it needs an API key, a specific file on your machine, or a
network), say so **in the block itself**, in a comment, and show the command that makes it work:

```python
# Requires: pip install anthropic  and  ANTHROPIC_API_KEY in your environment
```

### 2. Every link must work

```bash
python tools/check_links.py .        # internal links must resolve
```

External links are checked manually before a chapter is merged. No link shorteners, no bare URLs as
link text, no "click here". If a link text does not tell the reader where they are going, rewrite
it.

### 3. Follow the file structure

Every chapter file keeps the same shape:

```markdown
# Title

<blurb>

> **⏱️ Time:** ~N minutes
> **📚 Prereqs:** [file.md](file.md)
> **🎯 By the end you can:** <outcome>

## Why this matters for AI engineering
## <content sections>
## 🧪 Try it yourself
## ✅ Checkpoint
## 🐛 Common mistakes
## 🔗 Resources
## ➡️ Next
```

If you add a section, keep the markers. They are how a reader knows what to do with each part.

### 4. Keep the navigation intact

Every chapter ends with a `➡️ Next` block linking to the next file, and a `← Previous` link. If you
add a file to a step, update the chain in both directions and add the file to that step's
`guide.md` table of contents.

---

## Style

- **Prose wraps at about 90 characters.** One idea per paragraph.
- **Define every technical term the first time you use it.** No assumed knowledge.
- **Emoji are limited** to the section markers listed above. No emoji in prose or in code comments.
- **No placeholder text.** "Coming soon", "TODO" and "we will cover this later" are not acceptable
  in a merged chapter.
- **Comments explain the non-obvious.** Do not narrate the code back to the reader.
- **Use real names.** Not `foo`, not `someValue`, not `do_something()`.

---

## What to contribute

| Good | Not useful |
|---|---|
| A broken example you found, with the fix | Typos in code comments that change nothing |
| A clearer explanation of a hard idea | A new chapter that duplicates an existing one |
| A missing beginner trap for the 🐛 table | A link to a paywalled or ad-heavy site |
| A better exercise or checkpoint question | A whole new framework in one pull request |
| A translation of an existing chapter | "I think this course is great" |

---

## Reporting a bug

Open an issue and include:

1. The file name and the section heading.
2. The code block you ran.
3. The **full** error message, as text, not a screenshot.
4. Your Python version (`python --version`) and operating system.

The full error message is the single most useful thing you can include. It usually contains the
file, the line number and the problem.

---

## Step-by-step work

The repository is built one step at a time, in a fixed order:

1. PYTHON
2. DEVELOPER FOUNDATIONS
3. DATA MANAGEMENT
4. MATHEMATICS (FOR AIML)
5. CLASSICAL MACHINE LEARNING
6. ML PROJECTS
7. DEEP LEARNING
8. NLP & TRANSFORMERS
9. GENERATIVE AI
10. AGENTIC AI

Each step ships complete and verified before the next one starts. If you want to propose a change
to a step that has not been written yet, open an issue and describe what you would include — that
is more useful than a large draft that has to be rewritten to match the house style.

---

## License

By contributing, you agree that your contributions are licensed under the
[MIT License](LICENSE).

---

**Questions? Open an issue. Bug reports with a full traceback get fixed fastest.**
