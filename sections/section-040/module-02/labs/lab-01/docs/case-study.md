---
draft: true
exam_objectives:
- Push vs Pull
---
# Starting Environment

Two Prometheus servers run in `starfleet`: `prometheus`, which scrapes the `probe` and the Pushgateway, and `receiver`, which accepts remote write. The first server has no `remote_write` section. No group is pushed and no evidence report exists.
