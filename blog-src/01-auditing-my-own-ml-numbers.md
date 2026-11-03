---
title: "A 5-line baseline humbled my 99.6%"
date: 2026-11-03
tags: [Evaluation, Fine-tuning, LLMs]
summary: "I fine-tuned a 7B model to 270/271 on a held-out set. Then I trained TF-IDF + logistic regression on the same data and got 269/271. Here is what I changed in how I report results."
---

I fine-tuned **Qwen-2.5-7B with QLoRA** to classify financial claims into four compliance labels for **Sentinel**, my research-and-compliance agent. On a 271-claim held-out set it got **270 correct**. That looks great on a resume.

Then I did what I should have done first: I trained a boring baseline.

## The baseline check

TF-IDF features plus logistic regression, trained in seconds on the same 2,174 training claims, scored **269/271** on the same test set. The fine-tuned model's one-error "win" is well inside the noise: the 95% Wilson interval for 270/271 is about 97.9–99.9%.

| Method | Accuracy on the 271-claim test set |
|---|---|
| Majority class | 29.9% |
| Nearest-neighbour label copy | 91.9% |
| TF-IDF + logistic regression | 99.3% (269/271) |
| Fine-tuned Qwen-2.5-7B (QLoRA) | 99.6% (270/271) |

## Why the task was easy

I had generated the training data with an LLM from crisp label definitions. Synthetic data from one generator tends to be separable by style and keywords. I did check for leakage: zero exact or normalised duplicates between train and test, and no near-duplicate above 0.9 cosine similarity. So the test was clean, just easy.

## The placeholder I found in my own script

While auditing, I found that my benchmark script had **hard-coded numbers** for the comparison models. They looked like measurements in a report, but they were constants. I removed every claim that depended on them.

## What I do now

1. **Report n and an interval**, never a bare percentage.
2. **Always ship a dumb baseline** next to the model.
3. **Say where the data came from** (here: synthetic).
4. **Never put a number in a README that a script did not just compute.**
5. **Keep the claim honest**: the interesting part of Sentinel is the agent (hybrid retrieval, citations, a compliance rewrite step), not the last decimal of a classifier score.

A result you can defend under hostile questions is worth more than a perfect-looking one.
