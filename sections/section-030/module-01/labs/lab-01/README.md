---
draft: true
exam_objectives:
- Tracing and Spans
---
# Follow One Trace Across Two Services

The `drifter` pod in `outpost` was blamed for a slow request, but the request really ran through `probe` and `scout`. You must prove from the logs how one trace links the two services, and show what happens when context is not passed on.

The grader (`testing/live.py`) reads the `evidence` ConfigMap, reads the logs of `probe` and `scout` again, and re-queries Prometheus for ratios and exemplars. The traffic generator sends about four requests per second to `probe`, samples one trace in four, makes every seventh request fail and every fifth request slow (`scout` waits 0.3 seconds).

Status: UNTESTED. Only static checks (`astrona validate`, `bash -n`, `py_compile`) have run. Runtime verification is pending: `testing/smoke.sh` has not been run on a live cluster. Prometheus exemplar ingestion from the OpenMetrics endpoint is assumed from the documentation and not yet observed.
