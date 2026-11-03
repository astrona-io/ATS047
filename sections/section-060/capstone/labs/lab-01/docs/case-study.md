---
draft: true
exam_objectives:
- Basics of SLOs, SLAs, and SLIs
---
# Starting Environment

One instrumented probe serves metrics and structured request logs. A traffic generator makes ten percent of requests fail. Prometheus scrapes every two seconds and holds an empty rule file.

The team promised 99 percent successful requests. The lab asks for recording rules for the error ratio and the burn rate, and an alerting rule that fires on a fast burn.
