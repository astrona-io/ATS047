---
draft: true
exam_objectives:
- Push vs Pull
---
# Starting Environment

A Pushgateway holds two stale groups, `old_export` and `legacy_sync`. Prometheus scrapes it without `honor_labels` and has no `remote_write` section. A second Prometheus server, `receiver`, accepts remote write. No evidence report exists.
