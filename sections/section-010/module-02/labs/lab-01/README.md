---
draft: true
exam_objectives:
- Metrics
---
# Find The Costly Label And Calculate Fleet Rates

Graded lab for the module on labels, aggregation and scrape limits. The learner saves an `evidence` ConfigMap with four fields. `testing/live.py` re-runs each expression at the recorded time, checks the required functions and grouping, and checks value ranges derived from the traffic generator in `bootstrap/manifests/start.yaml` (`shop-a` about 4 requests per second with 10 percent failures, `shop-b` about 1 request per second with 50 percent failures, 50 user identifiers).

Status: UNTESTED. Only static checks (`astrona validate`, `bash -n`, `py_compile`) have run. Runtime verification is pending: `testing/smoke.sh` has not been run on a live cluster.
