---
draft: true
exam_objectives:
- Metrics
---
# Metrics Capstone: Review The Shop Metrics

Section capstone. The learner saves an `evidence` ConfigMap with metric types, the unbounded label, the badly named metric (`shop_latency_ms`), a fleet p95 latency and a per-instance error ratio. `testing/live.py` compares the types with the endpoint, re-runs both expressions at the recorded time and checks value ranges derived from the traffic generator (`shop-a` about 4 requests per second, 10 percent failures, 0.01 second delay; `shop-b` about 1 request per second, 50 percent failures, 0.2 second delay).

Status: UNTESTED. Only static checks (`astrona validate`, `bash -n`, `py_compile`) have run. Runtime verification is pending: `testing/smoke.sh` has not been run on a live cluster.
