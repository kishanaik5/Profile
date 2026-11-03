---
title: "When your validation set is secretly your training set"
date: 2026-11-03
tags: [Fine-tuning, Evaluation, Data]
summary: "Fine-tuning on templated data makes leakage easy to create and easy to miss. The checks I run now, and how I report results when the leakage cannot be removed."
---

If you generate training data from a knowledge base with templates, your validation data is probably generated from the same knowledge base. The model can look excellent and still tell you nothing about generalisation.

## Four leakage checks (they take minutes)

1. **Exact duplicates:** is any validation prompt or answer byte-identical to something in training?
2. **Normalised duplicates:** lowercase, strip punctuation, collapse whitespace, then compare.
3. **Entity overlap:** do the same (crop, disease) or (company, claim) pairs appear on both sides? In templated data they almost always do, and this is the check that matters.
4. **Near-duplicates:** TF-IDF or embedding cosine above 0.9 (or MinHash) between validation and training items.

Report the *counts*, not just "no leakage found."

## What I do when I cannot remove it

If every validation entity also appears in training, I stop calling it a generalisation test. I call it what it is: a measure of **format learning and recall of the knowledge base**. That is still useful, because it tells you whether the model learned the schema you wanted.

## Score with task metrics, not loss

Loss is not a quality metric, and a loss logged after a third of an epoch certainly is not. I measure **field-level exact match** against the ground truth. For a model that must return a fixed template, I check:

- Is the required format present? (Compare against the base model: it will score 0%, because it never saw the template, which proves format learning and nothing more.)
- Does a key categorical field match? (e.g. the recommended action)
- Does a numeric range match? Numeric fields are where small models fail. If exact match is low, the lesson is architectural: **serve numbers from a deterministic lookup, and let the model write the words.**

## Always add

- **n and an interval** (Wilson for proportions).
- **A base-model comparison**, so you know what the fine-tune added.
- **A clear note about the data source** (templated, synthetic, or human-written).

## The better evaluation

Hold out **whole entities**: remove entire (crop, disease) pairs from training and test on them. Add a human or LLM judge for quality, and have a domain expert review a sample. Until then, state the limitation in the first paragraph of your report, not the last.
