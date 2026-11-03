---
draft: true
exam_objectives:
- Metrics
---
# Find The Costly Label And Calculate Fleet Rates

A shop application runs as two instances, `shop-a` and `shop-b`, in the `starfleet` namespace. A Prometheus server scrapes both every two seconds under the job `shop`. The `shop-a` instance handles most of the traffic and fails about one request in ten. The `shop-b` instance handles less traffic and fails one request in two. The team wants evidence of which metric creates the most series and how the whole fleet behaves.

## Starting state

No evidence report exists. The `shuttle` pod in `starfleet` can reach both instances on port 8080 and the `prometheus` Service on port 9090. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-047-lab-010-02-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-047-lab-010-02-01" || exit 1
```

Keep this connection selected for the whole task.

## Required result

Create a ConfigMap named `evidence` in the `starfleet` namespace. Its key `report.json` holds one JSON object with four fields.

- `unbounded_label`: the name of the label on the shop metrics whose number of values grows with the number of users.
- `cardinality`: the result of an expression that counts the series of every metric name of the job `shop`, one result per metric name.
- `fleet_route_rate`: the result of an expression that gives the request rate over one minute for each `route`, added up across both instances. Each result series keeps only the `route` label.
- `fleet_error_ratio`: the result of one expression that gives the fraction of all requests of both instances that returned status `500`, over one minute. It must be the failed request rate of the fleet divided by the request rate of the fleet.

Each result field is an object with the keys `expression`, `evaluated_at` and `data`. The key `expression` holds the PromQL (Prometheus Query Language) text. The key `evaluated_at` holds the Unix time, in seconds, that you passed as the `time` parameter of `/api/v1/query`. The key `data` holds the `data` object that the API returned, unchanged.

Use `rate()` for counters and keep the evidence younger than five minutes when you submit. The grader runs your expressions against Prometheus again. Wait at least one minute after the start so that a one-minute window holds enough samples.

## Verify The Result

Run `astrona submit` after the ConfigMap exists.
