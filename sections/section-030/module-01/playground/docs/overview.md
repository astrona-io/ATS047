---
draft: true
exam_objectives:
- Tracing and Spans
---
# Spans And Trace Context Playground

This is an ungraded environment. Nothing here is submitted or graded, and you can change anything.

## What runs

The `starfleet` namespace holds the `probe` and `scout` Services on port 8080. `probe` calls `scout` for every request on `/work`. Both write JSON log lines (`request_completed` for every request and `span` for sampled requests) and serve `/metrics`. The `traffic` Deployment sends about four requests per second to `probe`, and the services sample one request in four. The `prometheus` Deployment scrapes both every two seconds with exemplar storage on. The `shuttle` pod is a plain Python container for sending requests inside the cluster.

## Connect

```sh
export KUBECONFIG="$(astrona kubeconfig ats-047-playground-030-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-047-playground-030-01" || exit 1
```

## Things to try

Send requests with and without a `traceparent` header and read the span records in the logs of `probe` and `scout`. Send a request with your own `traceparent` header and find its span lines in both logs. Change `child_delay` and compare the self time of the `probe` span. Send a request with `propagate=false` and compare the trace ids. Send a request with a `traceparent` whose last field is `00` and check that no span line appears, while `request_completed` lines still do.

Remove the playground with `astrona destroy ats-047-playground-030-01` when you are done.
