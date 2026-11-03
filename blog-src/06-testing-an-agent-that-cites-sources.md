---
title: "How I test an AI agent that must never invent a source"
date: 2026-11-04
tags: [Agents, Evaluation, Testing]
summary: "Sentinel drafts equity research with page-level citations, then audits itself for SEBI rules. Here is how I tested it, what I measured, and the number I stopped quoting."
---

Imagine an analyst asks, "What drove HDFC Bank's margin in FY2025?" and gets a confident answer with a citation: *page 187*. If that page does not exist, or does not say what the answer claims, the tool is worse than useless. It is a liability.

That was the idea behind **Sentinel**, a research agent I built for Indian equities. It finds the right passages in annual reports, drafts a short brief with citations, and then a second model checks the draft for compliance problems, such as giving buy/sell advice. It works. The interesting part was **how I made it testable**.

## The agent in one minute

1. **Search.** Keyword search (BM25) and meaning search (pgvector) run together. I merge the two result lists with reciprocal-rank fusion, then a small reranker orders the top passages.
2. **Draft.** A model writes the brief from those passages and attaches citations (company and page).
3. **Audit.** A fine-tuned Qwen-2.5-7B labels each claim as compliant, needs a disclaimer, unsupported, or an advice violation, and rewrites the risky ones.

## How I test it: three layers

**Layer 1: ordinary software tests.** The repo has 27 automated tests across three files (compliance, evaluation, smoke). On every push and pull request, continuous integration runs the linter (ruff), the type checker (mypy) and the tests. A scheduled weekly job re-runs the evaluation and compares it with a saved baseline, so a quiet regression can be caught.

**Layer 2: the model, with honest statistics.** The compliance model was tested on 271 held-out claims:

- **270 of 271 correct** (95% Wilson interval: about 97.9% to 99.9%).
- **No leakage that I could find:** zero exact or normalised duplicates between training and test, and no near-duplicate above 0.9 similarity.
- **A baseline next to it:** a simple TF-IDF plus logistic-regression model scored 269 of 271 on the same test. My training data is synthetic, so the task is easy, and I say so.

**Layer 3: citations.** This is the part people ask about, so here is exactly what is checked.

## How carefully are citations reviewed?

I wrote a citation checker that runs four mechanical checks:

1. **Known company.** The ticker must belong to the listed-company universe the system knows.
2. **Sane page.** The page number must be a real integer within the report's length, so "page 9,999" is flagged.
3. **Really retrieved.** The cited text must actually appear in the passages the search returned. A citation pointing at something that was never retrieved is flagged.
4. **No numbers without sources.** If a brief states figures but carries zero citations, it fails.

It is a strong guard against *made-up* sources. It is **not** a proof that every claim is true: it does not check that a cited passage logically supports the sentence. And today it runs in my evaluation and drift checks, while the live agent passes its citations into the compliance review. Wiring the checker into the live path is on my list.

## The number I stopped quoting

I had published faithfulness and answer-relevancy scores for the agent. When I tried to reproduce them, I couldn't. The evaluator in my repo is a quick keyword-overlap check built for fast regression runs, and on my test file it scores almost everything as perfect: if an answer is missing, it falls back to the expected answer, which matches itself. That makes it a smoke test, not evidence, and with no per-question outputs saved I had nothing to back the old numbers. So I stopped quoting them.

What I am doing instead: running the full pipeline end to end on the 100 questions, scoring with the official RAGAS library, and hand-checking about 50 citations myself.

## What I would tell you to copy

- Test the boring parts in CI so you can trust the interesting parts.
- Always put a dumb baseline next to your model.
- Be precise about what a check proves. "The page exists" is not "the claim is true."
- When you find that a metric is weaker than you thought, say so and fix the method.

More notes like this are on my [blog](index.html).
