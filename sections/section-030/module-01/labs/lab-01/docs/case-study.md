---
draft: true
exam_objectives:
- Tracing and Spans
---
# Starting Environment

Two services, `probe` and `scout`, write span records to their logs. `probe` calls `scout` for every request. Prometheus scrapes both services. No evidence report exists.
