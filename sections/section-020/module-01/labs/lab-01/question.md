---
draft: true
exam_objectives:
- Understand logs and events
---
# Correlate A Failed Request With Its Log Record And Route Metric

A shop application runs as the `shop` Deployment in the `starfleet` namespace. It writes one JSON log record to standard output for each request it logs, and it serves metrics on port 8080 at `/metrics`. A Prometheus server scrapes it every two seconds under the job `shop`. A traffic generator sends about two requests per second: one in six fails with status `500`, and every failed request goes to the route `/checkout`. The team wants to know which route fails, and why one failed request failed.

## Starting state

No evidence report exists. The `shuttle` pod in `starfleet` can reach the `shop` Service on port 8080 and the `prometheus` Service on port 9090. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-047-lab-020-01-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-047-lab-020-01-01" || exit 1
```

Keep this connection selected for the whole task.

## Required result

Create a ConfigMap named `evidence` in the `starfleet` namespace. Its key `report.json` holds one JSON object with three fields.

- `response`: the JSON body that the shop returned for one failing request to the route `/checkout` that you sent with the user `lab-user`. It has the fields `request_id`, `route` and `status`, and `status` is `500`.
- `record`: the log record of that same request, copied unchanged from the standard output of the shop. Match it by `request_id`.
- `failing_routes`: the result of one expression that gives, for each `route`, the per-second rate of requests with status `500` over one minute. Each result series keeps only the `route` label.

Each result field (`failing_routes`, and the others named as results below) is an object with the keys `expression`, `evaluated_at` and `data`. The key `expression` holds the PromQL (Prometheus Query Language) text. The key `evaluated_at` holds the Unix time, in seconds, that you passed as the `time` parameter of `/api/v1/query`. The key `data` holds the `data` object that the API returned, unchanged.

Send the request yourself with the user `lab-user`. Use `rate()` for counters and keep the evidence younger than five minutes when you submit. The grader reads the shop log, finds your record again and runs your expression against Prometheus again. Wait at least one minute after the start so that a one-minute window holds enough samples.

## Verify The Result

Run `astrona submit` after the ConfigMap exists.
