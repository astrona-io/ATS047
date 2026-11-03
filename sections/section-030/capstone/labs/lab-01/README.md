---
draft: true
exam_objectives:
- Tracing and Spans
---
# Tracing Capstone: Explain A Slow Request

The latency metric of `probe` shows slow requests. Before the team changes anything, they need to know which service holds the time in one slow trace, how many traces the sampler discards, and whether the spans leak a secret.

The grader (`testing/live.py`) reads the `evidence` ConfigMap, reads the logs of `probe` and `scout` again, and re-queries Prometheus for ratios and exemplars. The traffic generator sends about four requests per second to `probe`, samples one trace in four, makes every seventh request fail and every fifth request slow (`scout` waits 0.3 seconds).

Status: UNTESTED. Only static checks (`astrona validate`, `bash -n`, `py_compile`) have run. Runtime verification is pending: `testing/smoke.sh` has not been run on a live cluster. Prometheus exemplar ingestion from the OpenMetrics endpoint is assumed from the documentation and not yet observed.
