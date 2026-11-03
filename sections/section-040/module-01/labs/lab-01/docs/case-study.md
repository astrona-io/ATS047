---
draft: true
exam_objectives:
- Push vs Pull
---
# Starting Environment

The `probe` application, a traffic generator and a Prometheus server run in `starfleet`. A Pushgateway listens on port 9091. Prometheus scrapes the Pushgateway in the job `pushgateway` without `honor_labels`. No group is pushed and no evidence report exists.
