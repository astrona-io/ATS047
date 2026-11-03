---
draft: true
exam_objectives:
- Metrics
---
# Starting Environment

Two instances of a shop application, `shop-a` and `shop-b`, expose a request counter, a per-user counter, a duration histogram and a latency gauge. `shop-a` is fast and busy, `shop-b` is slower, less busy and fails more often. Prometheus scrapes both every two seconds. No evidence report exists.
