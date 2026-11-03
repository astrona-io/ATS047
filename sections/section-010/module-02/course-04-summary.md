---
draft: true
exam_objectives:
- Metrics
---
# Summary

A time series is one metric name with one exact set of label values. Each new combination creates a new series, and the number of series is the cardinality. Prometheus adds the `job` and `instance` labels at scrape time. A label with an unbounded set of values, such as a user identifier, multiplies the series count and costs memory and query time. Per-user detail belongs in logs or traces.

Aggregation operators combine series. The clause `by` keeps the listed labels and `without` removes the listed labels. You apply `rate()` to each counter series first and sum afterwards. A fleet error ratio is a ratio of sums, because an average of per-instance ratios gives a small instance the same weight as a busy one. A division matches series that have the same labels. Histogram buckets add up across instances, so a fleet quantile comes from `sum by (le)` and `histogram_quantile()`.

Metric names follow a convention: a subsystem prefix, the measured quantity and a base unit, with `_total` on counters. Values use seconds, bytes and ratios, not milliseconds or percentages.

A scrape sees one moment of a target. A gauge can change and return between two scrapes without a trace. The `up` series shows whether each scrape worked. A stale series returns no result, and a missing result is not zero.

- Series count is the product of label value counts.
- Unbounded labels belong in logs and traces, not in metrics.
- Sum the rates, then divide, for a fleet ratio.
- Use base units and the `_total` suffix.
- Check `up` before trusting a job's data.

<!-- astrona:playground:destroy -->
