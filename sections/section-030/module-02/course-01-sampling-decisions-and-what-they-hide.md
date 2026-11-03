---
draft: true
exam_objectives:
- Tracing and Spans
---
# Sampling Decisions And What They Hide

Recording every span of every request costs processing time, network traffic and storage. Most deployments therefore record only a share of the requests. That choice is called sampling, and it decides which problems you can find later. This part explains the sampling methods, measures the sampling rate of the example services and shows which requests a sampler discards.

## What sampling is

Sampling is the decision to record the spans of some traces and to discard the rest. The decision applies to a whole trace, not to single spans, so that a recorded trace is complete. A trace that is not sampled still exists as a request. It only leaves no spans.

The sampled flag in the `traceparent` header carries the decision. The first service in a request makes it, and every later service that follows the header repeats it. A service that sees the flag `01` records its span. A service that sees `00` does not.

## Head-based sampling

Head-based sampling decides when the trace starts, before any work has happened. The simplest forms are a fixed ratio, such as one trace in four, or a probability, such as 10 percent. The decision costs almost nothing, and the services do not need to buffer anything.

The weakness is that the decision cannot depend on how the request ended. A head sampler with a ratio of 25 percent keeps about one in four failed requests and one in four slow requests, exactly as it keeps one in four ordinary requests. If failures are rare, the sampled traces can contain no failure at all, even though a failure counter shows that failures happened.

The parent-based variant is the rule that a service follows an existing decision. When a request arrives with a `traceparent` header, the service uses the flag from the header. Only when no header exists does the service apply its own ratio. The example services work this way.

## Tail-based sampling

Tail-based sampling decides after the trace is finished, so the decision can use what happened: keep every trace that has an error, keep every trace slower than a limit, and keep a small share of the others. It gives much better coverage of the rare and interesting traces.

It costs more. Something has to hold all the spans of a trace until the trace is complete, usually in a collector. That collector needs memory, and it needs all the spans of one trace to arrive at the same collector instance. If a trace takes longer than the collector waits, the decision is made on an incomplete trace. Tail-based sampling does not remove the cost of producing spans, because the applications still create and send all of them.

## Measure the sampling rate

The example services count the traces they start in the counter `lab_traces_started_total`, with the label `sampled` set to `true` or `false`. A fraction of the rates tells you how much of the traffic is recorded. Define a helper that sends a PromQL (Prometheus Query Language) expression to Prometheus from the `shuttle` pod.

<!-- astrona:playground:renew -->

```sh
prom_query() {
  kubectl -n starfleet exec shuttle -- python -c 'import sys, urllib.parse, urllib.request; print(urllib.request.urlopen("http://prometheus:9090/api/v1/query?" + urllib.parse.urlencode({"query": sys.argv[1]}), timeout=8).read().decode())' "$1"
}
prom_query 'sum by (sampled) (rate(lab_traces_started_total[1m]))'
```

The response has two series, one for each value of `sampled`. The rate for `false` is about three times the rate for `true`, because the services keep one trace in four. Now calculate the fraction directly:

```sh
prom_query 'sum(rate(lab_traces_started_total{sampled="true"}[1m])) / sum(rate(lab_traces_started_total[1m]))'
```

The value is close to 0.25. The sum in the divisor adds the rates of both series, and the sum in the dividend keeps only the sampled one, so the result is the share of started traces that were recorded.

## What the metric sees and the traces do not

The same services count every completed request in `lab_requests_total`, split by the label `status`. This counter is not sampled. Compare the number of failed requests with the number of failed requests that have a span.

```sh
prom_query 'sum(rate(lab_requests_total{service="probe",status="500"}[1m]))'
```

About one in seven requests from the traffic generator fails, so the rate is around 0.5 failures per second. Only about a quarter of these failures were sampled, so the logs hold about 0.14 error spans per second. A trace search for failed requests finds a quarter of the real failures, and the metric is the only place that counts all of them. Use metrics for magnitude and trends, and use traces for the detail of the requests you did keep.

## Why spans are missing

A span can be absent from a trace view for several different reasons, and the view looks the same for all of them. The request was not sampled. The context was lost and the child started another trace. The service was not instrumented. The exporter failed to send the span, or a collector dropped it because its queue was full. Before you conclude that an operation did not happen, rule out these causes. A request that has a `request_completed` log line but no span in the backend was sampled out or was dropped, and the line tells you the service handled it.

## Checking the sampled flag by hand

You can see the parent-based rule yourself. Send a request with the flag `01`, then another with the flag `00`, and compare the `sampled` field of the responses. Use the helper that adds the header.

```sh
send_request() {
  kubectl -n starfleet exec shuttle -- python -c 'import sys, urllib.request; r = urllib.request.Request("http://probe:8080" + sys.argv[1], headers={"traceparent": sys.argv[2]}); print(urllib.request.urlopen(r, timeout=8).read().decode())' "$1" "$2"
}
send_request /work 00-2af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01
send_request /work 00-3af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-00
```

The first response says `sampled: true` and the second says `sampled: false`. The services did not apply their one-in-four rule, because a decision already existed. These requests do not appear in `lab_traces_started_total`, because that counter only counts traces that a service started itself.

## Sampling and cost

The cost of a trace has three parts: the work of creating the spans in the application, the network traffic to send them and the storage and indexing in the backend. Head sampling in the application removes all three for the requests it discards, and tail sampling in a collector removes only the storage part. When the application cost matters, the decision has to be made early.

Storage cost grows with the number of spans per trace as well as with the number of traces. A service that creates a span for every function call produces much larger traces than one that creates spans for incoming requests and outgoing calls. Reduce the size of the traces and the number of traces together, and keep a sample that still contains the requests you need to explain.

## Choosing a method

Choose a rate from what you need to see and what you can store. A low head sampling rate suits a high-traffic service where each trace looks like the others. Rare failures and rare slow requests need either a high rate or a tail-based policy that keeps them by their outcome. A common design combines a low head rate for normal traffic with tail rules that keep all errors and all very slow traces. State the sampling policy next to any trace-based conclusion, because the policy decides what the data can show.

You now know how traces are selected and why the recorded set is not a fair copy of all requests. The open question is how to get from a metric that shows slow requests to one of the traces that were kept.

## Common pitfalls

> [!WARNING]
> A sampled set of traces does not show the real error rate or the real latency distribution. Head sampling discards failures at the same rate as successes. A missing span does not prove that the operation did not run, because the cause can be sampling, lost context, missing instrumentation or a dropped export.
