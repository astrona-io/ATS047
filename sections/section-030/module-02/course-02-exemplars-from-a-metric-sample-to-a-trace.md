---
draft: true
exam_objectives:
- Tracing and Spans
---
# Exemplars: From A Metric Sample To A Trace

A histogram shows that some requests were slow, but it shows only counts in buckets. To find out why a request was slow you need the trace of one of those requests. A trace id cannot be a metric label, because every request has a different one. An exemplar solves this problem: it attaches one trace id to a metric sample without creating a new time series. This part explains the exemplar format, how Prometheus stores exemplars and how to query them.

## Why a trace id is not a label

Every distinct combination of label values makes a separate time series in Prometheus. A label holding a trace id has a new value for every request, so each request would create a new series. The memory and storage of the server would grow with the traffic, and each series would hold a single sample. This is the unbounded label problem, and the trace id is its clearest example.

The trace id belongs in logs and in traces, where one record per request is normal. In a metric, the trace id can appear only as an exemplar.

## What an exemplar is

An exemplar is an example observation that a service attaches to a sample in its metrics output. It has a set of labels, usually just `trace_id`, a value and an optional timestamp. For a histogram, the exemplar sits on a bucket and holds the value of one real observation that fell into that bucket, together with the trace id of the request that made it.

Exemplars exist only in the OpenMetrics exposition format. The older Prometheus text format has no syntax for them. A service attaches an exemplar to a sample line after a hash character:

```text
<metric>_bucket{le="0.5"} <count> # {trace_id="<trace id>"} <value> <timestamp>
```

The text after the hash is the exemplar: its label set in braces, the observed value, and the Unix time of the observation in seconds. The OpenMetrics format also requires a final line `# EOF`. The total length of an exemplar's label names and values is limited to 128 characters, which a 32-character trace id fits easily.

## Seeing the format in the example services

Prometheus asks for the OpenMetrics format with the HTTP header `Accept: application/openmetrics-text`. The example services return OpenMetrics when they see that header and the classic text format otherwise. Define a helper that fetches the metrics of `probe` with a header of your choice.

<!-- astrona:playground:renew -->

```sh
fetch_metrics() {
  kubectl -n starfleet exec shuttle -- python -c 'import sys, urllib.request; r = urllib.request.Request("http://probe:8080/metrics", headers={"Accept": sys.argv[1]}); print(urllib.request.urlopen(r, timeout=8).read().decode())' "$1"
}
fetch_metrics 'application/openmetrics-text' | grep lab_request_duration_seconds_bucket
```

Each line is a bucket of the histogram `lab_request_duration_seconds`. Some bucket lines end with `# {trace_id="..."}`, followed by a value and a time. Those are the exemplars. A bucket that no sampled request has fallen into has no exemplar. Now fetch the same metrics in the classic format and compare:

```sh
fetch_metrics 'text/plain' | grep lab_request_duration_seconds_bucket
```

The bucket lines have the same counts and no exemplars, because the classic format cannot carry them.

## Which requests get an exemplar

A service attaches an exemplar only for a request whose trace is sampled. The reason is practical: an exemplar that points to a trace that was never recorded leads nowhere. The example services keep the most recent sampled observation for each bucket and replace it when a newer one arrives. The exemplars you see are therefore recent, and each bucket shows at most one trace id per scrape.

## How Prometheus stores exemplars

Prometheus must be started with the feature flag `--enable-feature=exemplar-storage`. Without it, Prometheus ignores exemplars in the scraped data. With it, Prometheus keeps exemplars in a circular buffer in memory. The buffer has a fixed size, and when it is full, the oldest exemplars are overwritten. Exemplars are therefore kept for a shorter time than the samples themselves, and they are lost on a restart.

The example Prometheus Deployment has the flag in its arguments. Check it:

```sh
kubectl -n starfleet get deployment prometheus -o jsonpath='{.spec.template.spec.containers[0].args}'
```

The list includes `--enable-feature=exemplar-storage`. The scrape also has to negotiate the OpenMetrics format, which Prometheus does by default through the `Accept` header it sends to the target.

## Querying exemplars

Prometheus has an HTTP endpoint, `/api/v1/query_exemplars`, which takes a PromQL selector in the parameter `query` and a time range in the parameters `start` and `end`. It returns the exemplars of the matching series in that range. Ask for the exemplars of the `probe` bucket series of the last five minutes:

```sh
kubectl -n starfleet exec shuttle -- python -c 'import time, urllib.parse, urllib.request; now = time.time(); q = urllib.parse.urlencode({"query": "lab_request_duration_seconds_bucket{service=\"probe\"}", "start": now - 300, "end": now}); print(urllib.request.urlopen("http://prometheus:9090/api/v1/query_exemplars?" + q, timeout=8).read().decode())'
```

The response has a `data` list. Each item has `seriesLabels`, which names one bucket series including its `le` label, and `exemplars`, a list whose items have `labels`, `value` and `timestamp`. The `value` is the observed duration in seconds. An exemplar in the series with `le="0.5"` has a value above 0.25, so it comes from a slow request.

## From an exemplar to the trace

The `trace_id` inside an exemplar is the lookup key. In a deployment with a tracing backend, a dashboard opens the trace with that id. In the example, the backend is the log, so search both service logs for the id:

```sh
kubectl -n starfleet logs deployment/probe --tail=5000 | grep '"event": "span"'
```

Pick a line whose `duration_seconds` is above 0.25 and note its `trace_id`. The same id in the exemplar and in the span line shows that the exemplar pointed to a real recorded trace.

## What exemplars do not do

An exemplar is one example, not a summary. The slowest exemplar is not the slowest request, because exemplars exist only for sampled requests and only the latest one is kept for each bucket. An exemplar also does not prove that its request is typical of the bucket. Use exemplars to open a trace that explains one slow request, and use the histogram to judge how common slow requests are.

You now know how a metric sample can carry the id of a trace, how Prometheus stores it and how to read it. The remaining question is how to combine the metric, the exemplar, the trace and the logs into one investigation, and where each of them stops being reliable.

## Common pitfalls

> [!WARNING]
> Exemplars need the OpenMetrics format on the target and `--enable-feature=exemplar-storage` on Prometheus. If either is missing, the query returns no exemplars even though the service attaches them. Never copy the trace id into a label to make it easier to search; that creates one series per request.
