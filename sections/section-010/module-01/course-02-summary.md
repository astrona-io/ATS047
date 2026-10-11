---
draft: true
exam_objectives:
- Metrics
---
# Summary

Metric types describe different measurement contracts. Counters accumulate events, gauges represent changing state, and distributions preserve information about observed values such as duration.

Queries must respect those contracts and the selected population. Scraped samples are bounded observations, while labels determine identity and cost; a useful metric is a clear answer to an operational question rather than an arbitrary number with a dashboard.
