---
draft: true
exam_objectives:
- Metrics
---
# Identify Metric Types And Write Rate And Histogram Expressions

Graded lab for the module on counters, gauges and distributions. The learner saves an `evidence` ConfigMap whose report names the metric types and holds two live PromQL results. `testing/live.py` reads the `# TYPE` lines from the probe, re-runs both expressions against Prometheus at the recorded time and checks the series count, the required functions and a value range.

Status: UNTESTED. Only static checks (`astrona validate`, `bash -n`, `py_compile`) have run. Runtime verification is pending: `testing/smoke.sh` has not been run on a live cluster.
