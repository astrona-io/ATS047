---
draft: true
exam_objectives:
- Tracing and Spans
---
# Traces, Spans And The traceparent Header

A latency metric tells you that some requests are slow. It does not tell you which request, or which service inside the request path spent the time. Distributed tracing answers that question by recording the work of one request as a set of timed records that share one identifier. This part defines those records, shows the header that links them and sends one real request so you can read the records yourself.

## What a trace and a span are

A trace is the complete record of one request as it moves through the services that handle it. A span is one timed operation inside that trace, for example "the `probe` service handled `GET /work`" or "the `scout` service handled `GET /work`". A trace is therefore a group of spans, and every span in the group carries the same trace id.

A span has these fields:

- A trace id, which names the trace the span belongs to.
- A span id, which names this one span.
- A parent span id, which names the span that caused this one. A span with no parent is the root span of the trace.
- A name, a start time and a duration.
- A status that says whether the operation succeeded.
- Attributes, which are key and value pairs that describe the operation, such as the HTTP method and the route.

The ids are random numbers written in hexadecimal. A trace id is 16 bytes, which is 32 hexadecimal characters. A span id is 8 bytes, which is 16 hexadecimal characters. A random 16-byte value makes a clash between two traces extremely unlikely, so a tracing backend can store spans from many services without coordinating the ids.

## The example application

The playground runs two services in the `starfleet` namespace. The `probe` Service receives `GET /work` requests and calls the `scout` Service, which also serves `GET /work`. A `traffic` Deployment sends about four requests per second to `probe`. Both services write one JSON line to their log for every request, and one more JSON line, a span record, when the request is sampled. Sampling means that the service records spans for only some requests; the services here record one request in four.

The examples are small on purpose. They do not run a tracing backend such as Jaeger or Tempo. Each service writes the span record that an instrumented application would send to a backend, and that is enough to study the fields, the links between spans and the timing.

## The traceparent header

Two services can only add their spans to the same trace when the second service learns the trace id and the id of the span that called it. The W3C Trace Context standard defines an HTTP header for this, named `traceparent`. The caller adds the header to its outgoing request, and the receiver reads it.

The header has four fields separated by dashes:

```text
00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01
```

- The version, `00`, is two hexadecimal characters.
- The trace id is 32 lowercase hexadecimal characters. All zeros is not valid.
- The parent id is 16 lowercase hexadecimal characters. It is the span id of the caller's span. All zeros is not valid.
- The trace flags are two hexadecimal characters. The lowest bit is the sampled flag. The value `01` means the caller may have recorded the trace, and `00` means it did not.

A receiver that finds a valid header keeps the trace id, creates a new span id for its own span and records the parent id from the header as the parent of that span. A receiver that finds no header, or an invalid one, starts a new trace with a new trace id. The `probe` and `scout` services follow exactly these rules.

## Send one traced request

Define a shell function that runs a Python request inside the cluster from the `shuttle` pod. The pod is a plain Python container for sending requests to Services. The function takes a path and a `traceparent` value.

<!-- astrona:playground:renew -->

```sh
send_request() {
  kubectl -n starfleet exec shuttle -- python -c 'import sys, urllib.request; r = urllib.request.Request("http://probe:8080" + sys.argv[1], headers={"traceparent": sys.argv[2]}); print(urllib.request.urlopen(r, timeout=8).read().decode())' "$1" "$2"
}
```

Send a request with a header that you write yourself. The trace id and parent id below are only example values. The final `01` marks the trace as sampled.

```sh
send_request /work 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
```

The response is one JSON object. Its `trace_id` is the id from your header, its `parent_span_id` is `00f067aa0ba902b7`, and its `span_id` is a new value that `probe` generated. The `sampled` field is `true`. The `child` field holds the same set of fields for the span of `scout`.

## Read the span records in the logs

The `probe` service writes the span record to its log. Search the log for your trace id.

```sh
kubectl -n starfleet logs deployment/probe --tail=2000 | grep 4bf92f3577b34da6a3ce929d0e0e4736
```

You find two lines. One has the event name `request_completed`. The other has the event name `span` and adds the fields `name`, `start_time` and `attributes`. The `request_completed` line exists for every request, sampled or not, and it is a log line, not a span. The `span` line exists only for sampled requests, and it is the record a tracing backend would store.

Run the same search against the `scout` log:

```sh
kubectl -n starfleet logs deployment/scout --tail=2000 | grep 4bf92f3577b34da6a3ce929d0e0e4736
```

The same trace id appears in the `scout` log. The `parent_span_id` of the `scout` span is the `span_id` of the `probe` span. That one field is what links the two spans into a tree.

## The sampled flag decides what is recorded

Send the request again with the flag `00`. Use a different trace id so that the logs do not mix the two requests.

```sh
send_request /work 00-5bf92f3577b34da6a3ce929d0e0e4737-00f067aa0ba902b7-00
```

The response says `sampled: false`. Search both logs for the new trace id. Each service wrote a `request_completed` line, and neither wrote a `span` line. Both services obeyed the flag they received, and `probe` passed the flag `00` on to `scout`. A service that follows the header never overrides the decision of the first service in the trace, so a trace is either recorded in every service or in none.

## What a trace does not show

A trace shows the operations that the code or the instrumentation library chose to record. It is not a record of everything the machine did. Time spent in code that has no span, time spent waiting in an operating system queue and work done by a service that does not take part in tracing all remain invisible. When you read a trace, treat it as a view through the instrumentation you have, and state that limit before you draw a conclusion.

You now know what a trace, a span and a `traceparent` header contain, and you have seen two services record spans for one trace id. The open question is how the spans fit together in time: a parent span lasts at least as long as its children, and the relationship between the two durations tells you where the time went.

## Common pitfalls

> [!WARNING]
> A trace id in a log line is not a span. Only the `span` records describe timed operations. A `traceparent` value with an all-zero trace id or parent id is invalid, and a receiver ignores it and starts a new trace. The flag `00` does not mean the request failed; it means nobody recorded spans for it.
