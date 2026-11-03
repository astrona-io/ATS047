---
draft: true
exam_objectives:
- Metrics
---
# Starting Environment

Two instances of a shop application, `shop-a` and `shop-b`, expose metrics. `shop-a` handles about four requests per second with one failure in ten. `shop-b` handles about one request per second with one failure in two. Prometheus scrapes both every two seconds. One metric carries a label with one value per user. No evidence report exists.
