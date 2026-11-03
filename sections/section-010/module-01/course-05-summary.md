---
draft: true
exam_objectives:
- Metrics
---
# Summary

An application exposes its measurements as text on an HTTP endpoint. Prometheus scrapes that text on a schedule and stores each sample as a series identified by a metric name and a set of labels. A `# TYPE` line declares one of four types, and the type tells the reader which calculations are valid.

A counter is a running total that only grows and resets to zero when the process restarts. You read it with `rate()` for a per-second average or with `increase()` for a total over a window. Both functions detect a reset and compensate, and both need a window that holds several samples. You apply the rate to each series first and aggregate afterwards.

A gauge is a current value that moves in both directions. You read it directly, or you use `avg_over_time()`, `max_over_time()`, `delta()` and `predict_linear()` over a window. Applying `rate()` to a gauge treats every decrease as a reset and gives wrong numbers without an error. A scrape sees a gauge only at its own moment, so a short peak between two scrapes can be missed.

A histogram exposes cumulative buckets with an `le` label, plus a sum and a count, and all of them are counters. You calculate a fraction under a bucket bound exactly, and you estimate a quantile with `histogram_quantile()` by interpolation inside a bucket. A summary exposes quantiles computed in the application, which cannot be combined across instances.

- Counters: use `rate()` or `increase()`, never the raw value.
- Gauges: use the value or the `_over_time` functions, never `rate()`.
- Histograms: aggregate buckets with `sum by (le)` before `histogram_quantile()`.
- Summaries: do not average quantiles from several instances.

<!-- astrona:playground:destroy -->
