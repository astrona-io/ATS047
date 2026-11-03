---
draft: true
exam_objectives:
- Push vs Pull
---
# Remote Write And Staleness

Collecting a sample is only the first step in the life of a metric. Prometheus can copy samples to another system, and a query decides which series are current. This module teaches remote write, the staleness rules and a method for finding which stage of the collection path made data old.

## Learning Goals

- Explain what remote write sends, which component sends it and how its queue handles failures.
- Configure a `remote_write` entry and confirm that samples arrive at a receiver.
- Explain the lookback window and staleness markers, and predict what an instant query and a range query return after a series ends.
- Test freshness by value instead of by presence.
- Trace a stale value through the producer, the scrape, local processing and downstream delivery.

## Before You Start

You need to know what a scrape is, what the `up` series means and what a Pushgateway group is. The module states the facts it needs again when it uses them.

The playground has two Prometheus servers. The server `prometheus` scrapes the `probe`, the Pushgateway and itself, and has no `remote_write` entry. The server `receiver` accepts samples on `/api/v1/write` and does not scrape. A Pushgateway runs on port 9091, and its scrape job already sets `honor_labels: true`.

## What The Module Contains

The first part explains remote write and turns it on. The second part explains the lookback window and staleness markers and shows a pushed series going stale. The third part defines the stages of the collection path and uses them to trace a fault.

A graded lab follows the third part. It asks you to configure remote write, delete a pushed group and record four PromQL results. The module ends with a summary.

<!-- astrona:playground -->
