---
draft: true
exam_objectives:
- Push vs Pull
---
# Configure Remote Write And Observe A Stale Series

Graded lab for the remote write and staleness module. The learner adds `remote_write` to the `prometheus-config` ConfigMap, pushes and deletes a Pushgateway group and records four live results in an `evidence` ConfigMap. `testing/live.py` checks the configuration, confirms that the group is gone from the Pushgateway and re-runs every expression at the recorded time against the right server.

Status: UNTESTED. Only static checks (`astrona validate`, `bash -n`, `py_compile`) have run. Runtime verification is pending: `testing/smoke.sh` has not been run on a live cluster. The metric name `prometheus_remote_storage_samples_total` and the empty instant result after a delete are not yet confirmed on a live server.
