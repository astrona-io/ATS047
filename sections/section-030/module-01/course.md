---
draft: true
exam_objectives:
- Tracing and Spans
---
# Tracing Requests Through Spans And Context

This module explains what a distributed trace contains and how to read it. It follows one request through two services, `probe` and `scout`, and shows what a span is, how spans link into a tree, how to calculate the time a span spends on its own work and what happens when the trace context is not passed on.

## Learning Goals

- Name the fields of a span and the three fields of the `traceparent` header.
- Read parent-child links and calculate the self time of a span.
- Explain why overlapping child durations are not added together.
- Describe how context propagates across a service boundary and what a lost context looks like in the data.
- Explain why span attributes must not carry secrets.

## Before You Start

You need basic knowledge of HTTP requests and headers, and a shell with `kubectl`. The hands-on steps use a private playground that runs two services, a traffic generator and Prometheus. No tracing backend is installed: the services write their span records to their logs, which is enough to study the fields, the links and the timing.

## Reading Order

1. Traces, spans and the `traceparent` header.
2. Parent-child structure, timing and self time.
3. Context propagation, lost context and sensitive attributes.
4. Summary.

<!-- astrona:playground -->
