---
draft: true
exam_objectives:
- Tracing and Spans
---
# Sampling And Exemplars Playground

This is an ungraded environment. Nothing here is submitted or graded, and you can change anything.

## What runs

The `starfleet` namespace holds the `probe` and `scout` Services on port 8080. `probe` calls `scout` for every request on `/work`. Both write JSON log lines (`request_completed` for every request and `span` for sampled requests) and serve `/metrics`. The `traffic` Deployment sends about four requests per second to `probe`, and the services sample one request in four. The `prometheus` Deployment scrapes both every two seconds with exemplar storage on. The `shuttle` pod is a plain Python container for sending requests inside the cluster.

## Connect

```sh
export KUBECONFIG="$(astrona kubeconfig ats-047-playground-030-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-047-playground-030-02" || exit 1
```

## Things to try

Measure the sampling ratio and follow exemplars from a histogram bucket to a trace. Define a helper for the Prometheus API, evaluate the sampling ratio, and call `/api/v1/query_exemplars` for `lab_request_duration_seconds_bucket{service="probe"}`. Pick an exemplar and find its span lines in the logs. Fetch `http://probe:8080/metrics` with and without the header `Accept: application/openmetrics-text` and compare the output.

Remove the playground with `astrona destroy ats-047-playground-030-02` when you are done.
