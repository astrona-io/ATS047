---
draft: true
exam_objectives:
- Tracing and Spans
---
# Tracing Capstone: Explain A Slow Request

The latency metric of `probe` shows slow requests. Before the team changes anything, they need to know which service holds the time in one slow trace, how many traces the sampler discards, and whether the spans leak a secret.

## Starting state

The `starfleet` namespace runs two services. The `probe` Service receives requests on port 8080 at `/work` and calls the `scout` Service, which also listens on port 8080. Each service writes one JSON log line for every request it completes, with the event name `request_completed`. When a request is sampled, the service also writes a JSON log line with the event name `span`. A span line holds the fields `service`, `trace_id`, `span_id`, `parent_span_id`, `sampled`, `status`, `start_time`, `duration_seconds`, `name` and `attributes`. The `traffic` Deployment sends about four requests per second to `probe`, and the services sample one request in four. The `prometheus` Deployment scrapes both services every two seconds and stores exemplars. The `shuttle` pod in `starfleet` is a plain Python container for sending requests inside the cluster. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-047-lab-030-capstone-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-047-lab-030-capstone-01" || exit 1
```

Keep this connection selected for the whole task.

## Required result

Create a ConfigMap named `evidence` in the `starfleet` namespace. Its key `report.json` holds one JSON object with five fields. Wait at least two minutes after the start.

- `exemplar`: an object with the keys `expression`, `evaluated_at`, `trace_id` and `value`. The key `expression` queries the series of `lab_request_duration_seconds_bucket` with `service="probe"`. The keys `trace_id` and `value` hold the trace id and value, in seconds, of the exemplar with the highest value in the last five minutes.
- `spans`: the two `span` log records of that trace, one from `probe` and one from `scout`, taken unchanged from the logs and sorted by `service`.
- `self_time_seconds`: an object with the keys `probe` and `scout`. The self time of `scout` is its duration. The self time of `probe` is its duration minus the duration of the `scout` span.
- `critical_service`: the name of the service with the larger self time.
- `leaking_attribute`: an object with the keys `service` and `key`. It names the service whose span records the secret and the attribute key that holds it.
- `unsampled_share`: the result of one PromQL expression that gives the fraction of started traces that are not sampled, over one minute, as one series without labels.

The keys `exemplar` and `unsampled_share` use the same layout: `expression`, `evaluated_at` and either the exemplar values or the `data` object that the API returned. Keep the evidence younger than five minutes when you submit.

## Verify The Result

Run `astrona submit` after the ConfigMap exists.
