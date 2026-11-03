---
draft: true
exam_objectives:
- Understand logs and events
---
# Measure Log Sampling And Find The Sensitive Field

Graded lab for the module on correlation, sampling and retention. The learner measures the sampling fraction, reads the `sample_every` field, names the sensitive log field and compares the failure ratio from the metric with the error share of the log. `testing/live.py` re-runs both expressions at the recorded time and checks the counts against the live log.

Status: UNTESTED. Only static checks (`astrona validate`, `bash -n`, `py_compile`) have run. Runtime verification is pending: `testing/smoke.sh` has not been run on a live cluster.
