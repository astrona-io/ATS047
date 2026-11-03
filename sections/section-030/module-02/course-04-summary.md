---
draft: true
exam_objectives:
- Tracing and Spans
---
# Summary

Sampling decides which traces are recorded. Head sampling decides when a trace starts, costs almost nothing and treats failures like any other request. Tail sampling decides after the trace ends and can keep every error and every slow trace, but it needs a collector that holds all the spans of a trace. The sampled flag in the `traceparent` header carries the first decision to every later service. A set of sampled traces is not a fair copy of all requests, so it cannot give the real error rate or latency distribution. Metrics count every request and give the magnitude.

A span can be missing for several reasons that look the same: the request was not sampled, the context was lost, the service was not instrumented, or an exporter or collector dropped the span. A log line for every request is a useful second record when a span is missing.

An exemplar attaches one trace id to one metric sample, such as a histogram bucket, without creating a new time series. Exemplars exist only in the OpenMetrics format, and Prometheus stores them only when it runs with `--enable-feature=exemplar-storage`, in a circular buffer of fixed size. The `query_exemplars` endpoint returns them for a selector and a time range. A trace id must never become a label, because it creates one series per request.

An investigation starts with the metric, moves through an exemplar to a trace, reads the self time of the spans, and ends in the logs. Each signal proves only its own scope: the metric proves how many, the trace proves how and where for one sampled request, and the log proves what a service chose to write. A finding names its evidence and its limits.

<!-- astrona:playground:destroy -->
