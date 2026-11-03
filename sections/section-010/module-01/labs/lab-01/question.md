---
draft: true
exam_objectives:
- Metrics
---
# Identify Metric Types And Write Rate And Histogram Expressions

The `probe` application in the `starfleet` namespace exposes metrics, and a Prometheus server scrapes it every two seconds. A traffic generator sends about four requests per second, and one request in ten fails with status 500. The team needs a short evidence report that names the type of every metric and answers two questions with PromQL (Prometheus Query Language) expressions.

## Starting state

No evidence report exists. The `shuttle` pod in `starfleet` can reach both the `probe` Service on port 8080 and the `prometheus` Service on port 9090. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-047-lab-010-01-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-047-lab-010-01-01" || exit 1
```

Keep this connection selected for the whole task.

## Required result

Create a ConfigMap named `evidence` in the `starfleet` namespace. Its key `report.json` holds one JSON object with three fields.

- `metric_types`: an object that maps every metric name that starts with `lab_` to its type, exactly as the `# TYPE` lines of the `probe` metrics endpoint declare it.
- `failure_rate`: the result for the number of failed requests per second, as the rate of the counter `lab_requests_total` for status `500` over a one-minute window.
- `fast_fraction`: the result for the fraction of requests that finished in 0.05 seconds or less, calculated from the histogram `lab_request_duration_seconds` over a one-minute window.

The `failure_rate` and `fast_fraction` fields are each an object with the keys `expression`, `evaluated_at` and `data`. The key `expression` holds the PromQL text you ran. The key `evaluated_at` holds the Unix time, in seconds, that you passed as the `time` parameter. The key `data` holds the `data` object that the Prometheus HTTP API `/api/v1/query` returned, unchanged.

Each expression must return exactly one series. Use `rate()` on the counters and keep the evidence younger than five minutes when you submit. The grader reads the metrics endpoint and runs your expressions against Prometheus again, so values that are not real do not pass.

## Verify The Result

Run `astrona submit` after the ConfigMap exists. Wait for at least one minute of collected traffic before you evaluate a one-minute rate, because a shorter history gives a missing or rough value.
