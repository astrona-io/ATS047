---
draft: true
exam_objectives:
- Metrics
---
# Counters, Gauges And Distribution Measurements

A metric is a number that a program exposes about itself, together with a name, a type and optional labels. Prometheus collects these numbers by reading them over HTTP (Hypertext Transfer Protocol) and stores them as samples with timestamps. This module teaches the four metric types, the text format that carries them, and the Prometheus Query Language (PromQL) functions that are valid for each type.

## Learning Goals

- Read the exposition text format and name the type of each metric from its `# TYPE` line.
- Explain why a counter is read with `rate()` or `increase()` and what a counter reset does to a query.
- Explain why a gauge is read directly or with gauge functions, and why `rate()` is wrong for it.
- Build a fraction and a quantile from the bucket, count and sum series of a histogram.
- Explain why the quantiles of a summary cannot be averaged across instances.

## Before You Start

You need to read a command line, know what an HTTP request and a response are, and know what a Kubernetes pod and a Service are. You do not need to know PromQL. The module introduces each function before it uses it.

The playground starts one instrumented application named `probe`, a Prometheus server that scrapes it every two seconds, and a traffic generator that sends the `probe` about four requests per second. One request in ten returns status 500.

## What The Module Contains

The first part explains what a metric is, how an application exposes it and how the four types are declared. The second part covers counters, resets and the `rate()` and `increase()` functions. The third part covers gauges and the functions that suit them. The fourth part covers histograms and summaries and how to turn buckets into a fraction or a quantile.

A graded lab follows the fourth part. It asks you to identify the type of each metric and to write two expressions that Prometheus evaluates. The module ends with a summary.

<!-- astrona:playground -->
