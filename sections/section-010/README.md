---
draft: true
exam_objectives:
- Metrics
---
# Metrics

This section covers how applications expose metrics and how Prometheus stores and queries them. It has two modules. The first teaches the four metric types and the functions that suit each one. The second teaches labels, aggregation across instances, naming and the limits of scraping.

Each module has a landing page, readings with hands-on steps in a private playground, a graded lab and a summary. The section ends with a capstone lab and a knowledge check.

## Learning Outcomes

- Read the exposition format and name the type of each metric from its `# TYPE` line.
- Read counters with `rate()` and `increase()`, and explain how counter resets are handled.
- Read gauges directly or with `_over_time` functions, and explain why `rate()` is wrong for them.
- Build a fraction and a quantile from histogram buckets, and explain why summary quantiles cannot be averaged.
- Explain how labels define series, and recognise an unbounded label and its cost.
- Aggregate with `sum by` and `sum without`, and calculate a fleet error ratio as a ratio of sums.
- Apply the naming and unit conventions, and explain what the scrape interval, `up` and staleness mean for a result.
