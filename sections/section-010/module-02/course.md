---
draft: true
exam_objectives:
- Metrics
---
# Labels, Aggregation And Scrape Limits

A metric name alone rarely says enough. Labels split one metric into many series, aggregation combines them again, and the scrape process limits what the stored data can show. This module teaches how labels define series and cost, how to aggregate counters and ratios across instances without wrong results, and which limits scraping puts on every number.

## Learning Goals

- Explain that every unique combination of metric name and label values is one time series.
- Recognise an unbounded label and explain what it costs in memory and query time.
- Aggregate with `sum by` and `sum without`, and explain why a ratio of sums differs from an average of ratios.
- Apply the Prometheus naming rules for units and the `_total` suffix.
- Explain how the scrape interval, staleness and a failed scrape limit what a query can show.

## Before You Start

You need to know what a counter, a gauge and a histogram are, and what `rate()` does. The module repeats the facts it needs in one or two sentences. The playground starts two instances of a shop application, a Prometheus server and a traffic generator.

## What The Module Contains

The first part covers labels, series identity and cardinality, with a metric that carries one label value per user. The second part covers aggregation across instances and the difference between a ratio of sums and an average of ratios. The third part covers naming, units, the scrape interval, staleness and the `up` metric.

A graded lab follows the second part. It asks you to find the metric that creates the most series and to calculate fleet rates. The module ends with a summary.

<!-- astrona:playground -->
