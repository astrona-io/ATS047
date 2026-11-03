---
draft: true
exam_objectives:
- Tracing and Spans
---
# Sampling And Exemplars

This module explains why only some requests are traced, how that choice affects what you can conclude, and how an exemplar links a metric sample to one recorded trace. It uses the same `probe` and `scout` services as a request path, with Prometheus storing exemplars.

## Learning Goals

- Compare head-based and tail-based sampling and the cost of each.
- Measure a sampling ratio from a counter with `rate()`.
- List the reasons a span can be missing from a trace.
- Explain what an exemplar is, why the trace id is not a label, and what Prometheus needs to store exemplars.
- Move from a latency histogram to an exemplar, a trace and a log line, and state the limits of each step.

## Before You Start

You need to know what a trace, a span and the `traceparent` header are, and how to read a histogram with `rate()`. The hands-on steps use a private playground with two services, a traffic generator and Prometheus with exemplar storage enabled.

## Reading Order

1. Sampling decisions and what they hide.
2. Exemplars from a metric sample to a trace.
3. Reading metrics, exemplars, traces and logs together.
4. Summary.

<!-- astrona:playground -->
