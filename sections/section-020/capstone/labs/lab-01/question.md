---
draft: true
exam_objectives:
- Understand logs and events
---
# Logs And Events Capstone: Investigate A Failing Shop

A shop application runs as the `shop` Deployment in the `starfleet` namespace. It writes one JSON log record to standard output for each request it logs, and it serves metrics on port 8080 at `/metrics`. A Prometheus server scrapes it every two seconds under the job `shop`. A traffic generator sends about two requests per second: one in six fails with status `500`, and every failed request goes to the route `/checkout`. Before the shop goes into production, the team needs one review that joins a log record, the metrics, the sampling and the Kubernetes event of the shop pod.

## Starting state

No evidence report exists. The `shuttle` pod in `starfleet` can reach the `shop` Service on port 8080 and the `prometheus` Service on port 9090. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-047-lab-020-capstone-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-047-lab-020-capstone-01" || exit 1
```

Keep this connection selected for the whole task.

## Required result

Create a ConfigMap named `evidence` in the `starfleet` namespace. Its key `report.json` holds one JSON object with eight fields.

- `response`: the JSON body that the shop returned for one failing request to the route `/checkout` that you sent with the user `capstone-user`. It has the fields `request_id`, `route` and `status`, and `status` is `500`.
- `record`: the log record of that same request, copied unchanged from the standard output of the shop. Match it by `request_id`.
- `failing_routes`: the result of one expression that gives, for each `route`, the per-second rate of requests with status `500` over one minute. Each result series keeps only the `route` label.
- `logged_success_fraction`: a result. One expression that gives the fraction of successful requests (status `200`) that wrote a log record: the sum of `shop_log_records_total` with `level="info"` divided by the sum of `shop_http_requests_total` with `status="200"`.
- `sample_every`: an object with the keys `success` and `error`. Each value is the `sample_every` field that the shop writes in the records of that kind.
- `sensitive_field`: the name of the log field that holds personal data.
- `error_ratio`: a result. One expression that gives the fraction of all requests that returned status `500`, over one minute, from the metric `shop_http_requests_total`.
- `event`: an object with the keys `pod`, `reason` and `uid`. It describes the Kubernetes event with the reason `Started` for the pod of the `shop` Deployment: `pod` is the pod name, `reason` is the event reason and `uid` is the `metadata.uid` of the event.

Each result field (`failing_routes`, and the others named as results below) is an object with the keys `expression`, `evaluated_at` and `data`. The key `expression` holds the PromQL (Prometheus Query Language) text. The key `evaluated_at` holds the Unix time, in seconds, that you passed as the `time` parameter of `/api/v1/query`. The key `data` holds the `data` object that the API returned, unchanged.

Send the request yourself with the user `capstone-user`. Use `rate()` for counters and keep the evidence younger than five minutes when you submit. Kubernetes keeps events for one hour by default, so read the event in the first hour of the lab. The grader reads the shop log and the events, and runs your expressions against Prometheus again. Wait at least one minute after the start.

## Verify The Result

Run `astrona submit` after the ConfigMap exists.
