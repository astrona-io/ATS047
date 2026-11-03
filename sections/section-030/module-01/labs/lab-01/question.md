---
draft: true
exam_objectives:
- Tracing and Spans
---
# Follow One Trace Across Two Services

The `drifter` pod in `outpost` was blamed for a slow request, but the request really ran through `probe` and `scout`. You must prove from the logs how one trace links the two services, and show what happens when context is not passed on.

## Starting state

The `starfleet` namespace runs two services. The `probe` Service receives requests on port 8080 at `/work` and calls the `scout` Service, which also listens on port 8080. Each service writes one JSON log line for every request it completes, with the event name `request_completed`. When a request is sampled, the service also writes a JSON log line with the event name `span`. A span line holds the fields `service`, `trace_id`, `span_id`, `parent_span_id`, `sampled`, `status`, `start_time`, `duration_seconds`, `name` and `attributes`. The `traffic` Deployment sends about four requests per second to `probe`, and the services sample one request in four. The `prometheus` Deployment scrapes both services every two seconds and stores exemplars. The `shuttle` pod in `starfleet` is a plain Python container for sending requests inside the cluster. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-047-lab-030-01-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-047-lab-030-01-01" || exit 1
```

Keep this connection selected for the whole task.

## Required result

Create a ConfigMap named `evidence` in the `starfleet` namespace. Its key `report.json` holds one JSON object with four fields.

Send one request from the `shuttle` pod to `http://probe:8080/work?child_delay=0.2` with the header `traceparent: 00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01`. The `probe` Service continues the trace from that header and passes the context on to `scout`.

- `trace_id`: the trace id from your header, as a string.
- `spans`: the list of `span` log records for this trace id, taken unchanged from the logs of `probe` and `scout`, sorted by `service`. It holds exactly two records.
- `probe_self_time_seconds`: the `duration_seconds` of the `probe` span minus the `duration_seconds` of the `scout` span, as a number.
- `orphan`: an object with the keys `probe_trace_id` and `scout_trace_id`. Send a second request to `http://probe:8080/work?propagate=false`. With `propagate=false`, `probe` does not send a `traceparent` header to `scout`. Take both ids from the JSON response, where the `scout` result is under the key `child`.

The grader reads the logs of both services again, so the request must still be in the last 5000 log lines of each service when you submit.

## Verify The Result

Run `astrona submit` after the ConfigMap exists.
