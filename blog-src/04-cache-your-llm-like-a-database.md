---
title: "Cache your LLM like a database: bucket the inputs, template the output"
date: 2026-11-03
tags: [LLMs, Caching, System Design]
summary: "When thousands of users ask almost the same question, don't pay for thousands of generations. A two-level template cache pattern."
---

LLM calls are slow and cost money per token. If a million users ask nearly the same thing, generating a fresh answer for each is waste. The trick is to decide what the model *actually* needs to vary on.

## Step 1: turn continuous inputs into a few buckets

Many apps feed an LLM numbers: sensor readings, scores, satellite indices. Rather than keying a cache on raw values (which never repeat), I bucket each number into a few named categories, for example low / medium / high. Five bucketed inputs give a small, finite key space. Similar situations now share a key.

## Step 2: cache a *template*, not the final text

The first time a key is seen, call the model once and ask it for a report with **placeholders** for the exact values. Store that template. For every later request with the same key, **fill the placeholders** with that user's real numbers. Personalisation survives; the model call does not repeat.

## Step 3: a second level for translations

If the product speaks many languages, cache the translation of each template separately, keyed by `(template_id, language)`. Translate once per language, not once per user.

## Rules that keep it safe

- **Version the key.** Put a `prompt_version` in it. To invalidate, bump the version; never delete rows.
- **Guard half-written rows.** Mark a row `pending` while generating and exclude it from lookups, so concurrent requests do not read a half-written template.
- **Count hits.** Store a `hit_count` per template. It is your observability and your cost report in one column.
- **Fall back.** If the cache layer fails, call the model directly. A cache must never be a single point of failure.

## What to measure

- **Hit rate** = hits / (hits + generations).
- **Call reduction**, assuming one uncached call per request. Be honest that this is an upper bound if some requests would not have needed a call anyway.
- **Latency of the cold path versus the warm path** reported separately. Never present a cache-hit latency as your end-to-end latency.

## The trade-off

Bucketing is lossy by design. Coarse buckets mean more reuse but less specific advice. Audit the bucket boundaries with someone who knows the domain, and sample outputs for quality. Caching saves money; it does not make the content correct.
