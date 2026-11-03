---
title: "Tracking microscopic swimmers with YOLOv8 + DeepSORT on 2 vCPUs"
date: 2026-11-03
tags: [Computer Vision, Tracking, Backend]
summary: "How a microscopy video becomes a motility report: detection, tracking, a queue, and where the time actually goes."
---

The task: take a microscope video of a semen sample and say what share of cells swim forward, wiggle, or don't move. The detection-and-tracking prototype is public: [`sperm_motility_project`](https://github.com/kishanaik5/sperm_motility_project). Step 4 below describes the architecture of the service I later wrapped around it at work (the code there is private, so this is the design only).

## The pipeline

1. **Detect.** YOLOv8 looks at every frame (resized to 416×416) and boxes each cell.
2. **Track.** DeepSORT links boxes across frames so each cell keeps an ID: a Kalman filter predicts where it will be, and an appearance embedding helps keep identities apart when cells cross.
3. **Decide.** For each track that lasts at least 10 frames: moved far and in a fairly straight line → *progressive*; barely moved → *immotile*; otherwise → *non-progressive*. The thresholds are proportions of the frame width, so they do not need a µm-per-pixel calibration (a limitation I will come back to).
4. **Serve.** A FastAPI endpoint accepts the video and returns `202` with a report ID immediately. A Celery worker reads from a Redis queue, one job at a time, downloads the video from S3, runs the pipeline, and writes the result to PostgreSQL.

## One job at a time, on purpose

The container has about 2 vCPUs and 4 GB of RAM. Prefetch 1, late acknowledgement, and freeing memory after each task keep one long video from taking the box down.

## Where the time goes

On two short clips (about 7–8 seconds each, 640×360), end-to-end processing on CPU with 2 threads took **37–65 seconds**. Detection was cheap, about 27 ms per frame. **DeepSORT's appearance embedding was the bottleneck**, at roughly 120–260 ms per frame, and its cost grows with how many cells are in the frame. If I needed this faster I would try a lighter embedder, a motion-only tracker like ByteTrack, or skipping appearance features when the field is dense.

## What I would not claim

- **No accuracy number.** I have no ground-truth annotations. A tracker that creates hundreds of IDs for a few dozen cells is fragmenting identities, and MOTA needs labelled boxes with IDs.
- **These are not CASA metrics.** Real CASA reports VCL, VSL, VAP and LIN, which need a frame rate and a physical scale. Mine is a displacement heuristic.
- **Two clips is a smoke test**, not a benchmark.

The honest next step is to annotate two or three clips in CVAT and compute MOTA and IDF1 with `motmetrics`.
