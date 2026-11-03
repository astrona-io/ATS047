---
draft: true
exam_objectives:
- Push vs Pull
---
# Pull Versus Push Capstone: Retire Stale Groups And Ship Batch Metrics

Graded capstone for the pull versus push section. The learner deletes two stale Pushgateway groups, pushes a fresh `nightly_report` group, sets `honor_labels: true`, adds `remote_write` to a receiver Prometheus server and records three live results. `testing/live.py` checks the gateway contents, the configuration and the expressions on both servers.

Status: UNTESTED. Only static checks (`astrona validate`, `bash -n`, `py_compile`) have run. Runtime verification is pending: `testing/smoke.sh` has not been run on a live cluster.
