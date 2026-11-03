---
draft: true
exam_objectives:
- Tracing and Spans
---
# Find A Slow Trace With An Exemplar

A latency graph for `probe` shows slow requests, and the on-call engineer needs the trace behind one of them. You must measure how many traces the services sample and use an exemplar to reach a slow trace.

The grader (`testing/live.py`) reads the `evidence` ConfigMap, reads the logs of `probe` and `scout` again, and re-queries Prometheus for ratios and exemplars. The traffic generator sends about four requests per second to `probe`, samples one trace in four, makes every seventh request fail and every fifth request slow (`scout` waits 0.3 seconds).

Status: UNTESTED. Only static checks (`astrona validate`, `bash -n`, `py_compile`) have run. Runtime verification is pending: `testing/smoke.sh` has not been run on a live cluster. Prometheus exemplar ingestion from the OpenMetrics endpoint is assumed from the documentation and not yet observed.
