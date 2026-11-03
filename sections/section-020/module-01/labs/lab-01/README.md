---
draft: true
exam_objectives:
- Understand logs and events
---
# Correlate A Failed Request With Its Log Record And Route Metric

Graded lab for the module on metrics, logs and events. The learner sends one failing request, copies its log record and saves an `evidence` ConfigMap with a route failure rate. `testing/live.py` finds the record again in the shop log, checks that the `request_id` matches the response and re-runs the expression at the recorded time.

Status: UNTESTED. Only static checks (`astrona validate`, `bash -n`, `py_compile`) have run. Runtime verification is pending: `testing/smoke.sh` has not been run on a live cluster.
