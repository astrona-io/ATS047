---
draft: true
exam_objectives:
- Tracing and Spans
---
# Summary

A trace is the record of one request across the services that handle it, and a span is one timed operation inside it. Each span has a trace id, a span id, an optional parent span id, a name, a start time, a duration, a status and attributes. The `traceparent` header carries the trace id, the id of the calling span and the sampled flag from one service to the next, so a receiving service can attach its span to the right trace and parent.

The parent-child links form a tree that records which operation started which. The tree does not say which operation caused a problem. The self time of a span, its duration minus the time covered by its children, shows where a request spent its time, and the longest span is often only waiting for a child. Durations of overlapping children are not added together, and time that no span explains needs other evidence such as metrics, logs or a profile.

Context propagation has three steps: inject the context into the outgoing request, extract it from the incoming request, and create the new span as a child. A service that skips a step starts a separate trace, and the original trace then shows less work than happened. A collector does not repair this, because it does not instrument applications. Queues need a deliberate choice between continuing the trace and starting a new one with a link.

Span attributes are stored and read like logs, so they must not hold secrets or full request targets, and they should have a small set of values. A trace is always a view through the instrumentation and the sampling decisions that were in place, not a guarantee that every operation was recorded.

<!-- astrona:playground:destroy -->
