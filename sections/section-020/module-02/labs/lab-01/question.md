---
draft: true
exam_objectives:
- Understand logs and events
---
# Measure Log Sampling And Find The Sensitive Field

A shop application runs as the `shop` Deployment in the `starfleet` namespace. It writes one JSON log record to standard output for each request it logs, and it serves metrics on port 8080 at `/metrics`. A Prometheus server scrapes it every two seconds under the job `shop`. A traffic generator sends about two requests per second: one in six fails with status `500`, and every failed request goes to the route `/checkout`. The team wants to know how much of the traffic the log shows, which field leaks personal data, and which source gives the true failure ratio.

## Starting state

No evidence report exists. The `shuttle` pod in `starfleet` can reach the `shop` Service on port 8080 and the `prometheus` Service on port 9090. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-047-lab-020-02-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-047-lab-020-02-01" || exit 1
```

Keep this connection selected for the whole task.

## Required result

Create a ConfigMap named `evidence` in the `starfleet` namespace. Its key `report.json` holds one JSON object with six fields.

- `logged_success_fraction`: a result. One expression that gives the fraction of successful requests (status `200`) that wrote a log record: the sum of `shop_log_records_total` with `level="info"` divided by the sum of `shop_http_requests_total` with `status="200"`.
- `sample_every`: an object with the keys `success` and `error`. Each value is the `sample_every` field that the shop writes in the records of that kind.
- `sensitive_field`: the name of the log field that holds personal data.
- `error_ratio`: a result. One expression that gives the fraction of all requests that returned status `500`, over one minute, from the metric `shop_http_requests_total`.
- `log_error_share`: an object with the integer keys `errors` and `total`. Count the request records in the last 200 lines of the shop log: `total` is the number of request records and `errors` is the number with level `error`. Ignore lines that are not request records.

Each result field (`failing_routes`, and the others named as results below) is an object with the keys `expression`, `evaluated_at` and `data`. The key `expression` holds the PromQL (Prometheus Query Language) text. The key `evaluated_at` holds the Unix time, in seconds, that you passed as the `time` parameter of `/api/v1/query`. The key `data` holds the `data` object that the API returned, unchanged.

Use `rate()` for counters and keep the evidence younger than five minutes when you submit. The grader reads the shop log and runs your expressions against Prometheus again. Wait at least one minute after the start so that the counters hold enough requests.

## Verify The Result

Run `astrona submit` after the ConfigMap exists.
