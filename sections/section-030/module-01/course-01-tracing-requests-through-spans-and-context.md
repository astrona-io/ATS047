---
draft: true
exam_objectives:
- Tracing and Spans
---
# Tracing Requests Through Spans And Context

Distributed tracing follows the work associated with a request across participating components. A trace is composed of spans, each representing a timed operation such as handling an HTTP request or querying a database. It can help explain where time was spent and which operation failed when an aggregate latency metric signals a problem.

## Understand The Span Relationship

A span has an identity, a trace identity, timing information and attributes describing the operation. Parent-child relationships indicate which operation initiated another operation. A service can also record events or links where supported by the tracing model. The resulting trace describes instrumented work rather than every activity performed by the machine.

A request-serving span might contain a child span for a database call and another for a downstream service call. Attributes can describe the route, response status or database operation. Use bounded, useful attributes and protect confidential content. Recording credentials or complete sensitive queries in a span creates an exposure path unrelated to whether the trace is helpful for performance analysis.

## Propagate Context Across Boundaries

A receiving service needs compatible context to connect its work to the upstream request. Trace context is commonly propagated through protocol headers or message metadata. The service must extract the context and create appropriate related spans. Merely deploying a collector does not instrument every application or fix missing propagation.

If one service fails to propagate context, its downstream work can appear as an unrelated trace. An incomplete trace may therefore show less work than actually occurred. Asynchronous queues also require a deliberate context model because a producer's operation and a later consumer's operation may not have a simple synchronous parent-child lifetime.

## Interpret Timing Rather Than Summing Blindly

Suppose two dependency calls each last several hundred milliseconds but run concurrently. Adding their durations overstates the elapsed time contributed to the request because their intervals overlap. Sequential calls have a different effect. Inspect the timing relationship and critical path before deciding which dependency dominates the user-visible latency.

A parent span can also contain uninstrumented local work, queueing or waiting. A long parent with short children does not automatically prove the parent service used excessive CPU. It indicates time not explained by the visible children and requires further evidence. Metrics and profiling or logs can clarify the remaining hypothesis.

## Account For Sampling And Coverage

Tracing every request can be costly, so deployments often sample. Head-based sampling decides early, while tail-based approaches can consider later trace information. Their tradeoffs affect which errors and slow requests are retained. A rare failure may be absent from a sampled trace set even when the failure-rate metric shows it occurred.

Missing spans can reflect disabled instrumentation, exporter failures, context loss or collector limits. State those limitations before making a conclusion about the request path. A visually complete trace is still a view through the selected instrumentation, not a guarantee that every relevant operation was represented.

## Combine Signals Appropriately

Use metrics to identify affected services, magnitude and trends, then traces to examine request paths within the relevant population. Logs can provide error detail for a selected span or correlation identifier. A trace identifier is useful in those records but generally unsuitable as an unbounded metric label. Exemplars can connect selected measurements to trace context without creating a time series for every request.

## Common pitfalls

> [!WARNING]
> A collector does not automatically instrument applications. Sampling and propagation gaps can hide work, and overlapping span durations must not be added as if all operations were sequential.
