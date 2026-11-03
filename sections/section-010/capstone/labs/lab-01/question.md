---
draft: true
exam_objectives:
- Metrics
---
# Metrics Capstone: Review The Shop Metrics

The `starfleet` namespace runs a shop application as two instances, `shop-a` and `shop-b`, under the Prometheus job `shop`. Before the shop goes into production, the team needs a metrics review that covers metric types, naming, label cost, latency and error ratios.

## Starting state

No evidence report exists. The `shuttle` pod in `starfleet` can reach both instances on port 8080 and the `prometheus` Service on port 9090. Prometheus scrapes every two seconds. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-047-lab-010-capstone-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-047-lab-010-capstone-01" || exit 1
```

Keep this connection selected for the whole task.

## Required result

Create a ConfigMap named `evidence` in the `starfleet` namespace. Its key `report.json` holds one JSON object with five plain fields and two result fields.

- `metric_types`: an object that maps every metric name that starts with `shop_` to its declared type, as the `# TYPE` lines of the `shop-a` metrics endpoint show.
- `unbounded_label`: the name of the label whose number of values grows with the number of users.
- `naming_issue`: the name of the one `shop_` metric whose name does not follow the Prometheus naming convention for units.
- `p95_latency`: the result of an expression that estimates the 0.95 quantile of request duration in seconds for the whole fleet over one minute, from the histogram `shop_request_duration_seconds`.
- `error_ratio_by_instance`: the result of one expression that gives, for each `instance`, the fraction of requests that returned status `500` over one minute. Each result series keeps only the `instance` label.

The two result fields are objects with the keys `expression`, `evaluated_at` and `data`. The key `expression` holds the PromQL (Prometheus Query Language) text. The key `evaluated_at` holds the Unix time, in seconds, that you passed as the `time` parameter of `/api/v1/query`. The key `data` holds the `data` object that the API returned, unchanged.

Use `rate()` for counters and keep the evidence younger than five minutes when you submit. The grader reads the metrics endpoint and runs your expressions again. Wait at least one minute after the start.

## Verify The Result

Run `astrona submit` after the ConfigMap exists.
