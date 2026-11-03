---
draft: true
exam_objectives:
- Tracing and Spans
---
# Find A Slow Trace With An Exemplar

A latency graph for `probe` shows slow requests, and the on-call engineer needs the trace behind one of them. You must measure how many traces the services sample and use an exemplar to reach a slow trace.

## Starting state

The `starfleet` namespace runs two services. The `probe` Service receives requests on port 8080 at `/work` and calls the `scout` Service, which also listens on port 8080. Each service writes one JSON log line for every request it completes, with the event name `request_completed`. When a request is sampled, the service also writes a JSON log line with the event name `span`. A span line holds the fields `service`, `trace_id`, `span_id`, `parent_span_id`, `sampled`, `status`, `start_time`, `duration_seconds`, `name` and `attributes`. The `traffic` Deployment sends about four requests per second to `probe`, and the services sample one request in four. The `prometheus` Deployment scrapes both services every two seconds and stores exemplars. The `shuttle` pod in `starfleet` is a plain Python container for sending requests inside the cluster. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-047-lab-030-02-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-047-lab-030-02-01" || exit 1
```

Keep this connection selected for the whole task.

## Required result

Create a ConfigMap named `evidence` in the `starfleet` namespace. Its key `report.json` holds one JSON object with three fields. Wait at least two minutes after the start so that Prometheus holds slow exemplars.

- `sampling_ratio`: the result of one PromQL (Prometheus Query Language) expression that gives the fraction of started traces that are sampled, over one minute, as one series without labels. Use `lab_traces_started_total` and `rate()`.
- `exemplar`: an object with the keys `expression`, `evaluated_at`, `trace_id` and `value`. The key `expression` holds a query for the series of `lab_request_duration_seconds_bucket` with the label `service="probe"`. The keys `trace_id` and `value` hold the trace id and the value, in seconds, of the exemplar with the highest value in the last five minutes.
- `span_count`: the number of `span` log records for that trace id in the logs of `probe` and `scout` together.

The key `sampling_ratio` is an object with the keys `expression`, `evaluated_at` and `data`. The key `evaluated_at` holds the Unix time, in seconds, that you passed to Prometheus, and `data` holds the `data` object the API returned, unchanged. Keep the evidence younger than five minutes when you submit.

## Verify The Result

Run `astrona submit` after the ConfigMap exists.
