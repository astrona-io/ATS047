---
draft: true
exam_objectives:
- Push vs Pull
---
# Push A Batch Result And Keep Its Job Label

Graded lab for the Pushgateway module. The learner pushes a group named `nightly_report`, sets `honor_labels: true` on the `pushgateway` scrape job and records three live PromQL results in an `evidence` ConfigMap. `testing/live.py` reads the Pushgateway metrics, checks the live configuration and re-runs each expression at the recorded time.

Status: UNTESTED. Only static checks (`astrona validate`, `bash -n`, `py_compile`) have run. Runtime verification is pending: `testing/smoke.sh` has not been run on a live cluster. The Pushgateway image tag `v1.11.1` has not been pulled.
