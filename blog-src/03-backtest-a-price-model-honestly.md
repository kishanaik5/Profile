---
title: "How to backtest a price forecaster without fooling yourself"
date: 2026-11-03
tags: [Forecasting, Time Series, Evaluation]
summary: "Your service's own error metric is probably measured on training data. Here is a rolling-origin backtest recipe, with a naive baseline in the room."
---

A forecasting service can return a nice-looking error number and still be unproven. In one price-forecasting service I worked on, the metric the API reported was computed on the **same data the models were trained on**. It tells you how well the model memorised the past, not how well it predicts the future.

## The recipe

**1. Rolling origins, not one split.** Pretend it is an earlier date `T`. Train on data up to `T`, forecast the next 12 weeks, and compare with what actually happened. Move `T` forward and repeat. Every origin is one test.

**2. Put a naive baseline in the room.** "Repeat the last price" is brutally hard to beat on noisy markets. Add a mean of the last few weeks, and a seasonal-naive forecast (the value from 52 weeks ago) if you have more than a year of data.

**3. Use the same code path as production.** Import the real feature builder, the real hyper-parameters, and the real recursive-forecast function. A backtest that reimplements the model is a test of your reimplementation.

**4. Use a scale-free metric.** MAPE (or sMAPE) lets you average across commodities with very different prices. MAE alone is dominated by the expensive ones.

**5. Put an interval on the improvement.** Compute the per-origin difference between the baseline's error and the model's error, then bootstrap it. Origins from the same series overlap, so the interval is optimistic. Say so.

**6. Look at the winners and losers.** Count how many series the model beats the baseline on. Look at the median error as well as the mean, because a few terrible origins can drag the average.

## Lessons from running it

- An **average of several models** was more stable than most individual models, but no single model was clearly best across the board.
- The model the API exposed as its headline was not the best one. You only find that by backtesting.
- With under a year of history, a seasonal baseline is impossible and seasonality features cannot be learned from the training window. Say what your history allows.

A research notebook that reports a great score on one commodity for one month is a starting point, not a result. Backtest across series, against a baseline, with an interval.
