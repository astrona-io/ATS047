---
draft: true
exam_objectives:
- Metrics
---
# Metrics Playground

This is an ungraded environment. Nothing here is submitted or graded, and you can change anything.

## What runs

The `starfleet` namespace holds four workloads. The `probe` Deployment is an instrumented application that serves metrics on port 8080 at `/metrics`. The `prometheus` Deployment scrapes the `probe` every two seconds. The `traffic` Deployment sends about four requests per second to the `probe`, and one request in ten returns status 500. The `shuttle` pod is a plain Python container that you use to send requests inside the cluster. The `outpost` namespace holds a second pod named `drifter` for the same purpose.

## Connect

```sh
export KUBECONFIG="$(astrona kubeconfig ats-047-playground-010-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-047-playground-010-01" || exit 1
```

## Things to try

Read the raw metrics text of the `probe` and find the `# TYPE` line of every metric.

```sh
kubectl -n starfleet exec shuttle -- python -c 'import urllib.request; print(urllib.request.urlopen("http://probe:8080/metrics", timeout=8).read().decode())'
```

Send PromQL expressions to Prometheus with a helper function.

```sh
prom_query() {
  kubectl -n starfleet exec shuttle -- python -c 'import sys,urllib.parse,urllib.request; print(urllib.request.urlopen("http://prometheus:9090/api/v1/query?"+urllib.parse.urlencode({"query":sys.argv[1]}),timeout=8).read().decode())' "$1"
}
prom_query 'sum by (status) (rate(lab_requests_total[1m]))'
prom_query 'histogram_quantile(0.95, sum by (le) (rate(lab_request_duration_seconds_bucket[1m])))'
```

Try these experiments. Compare `lab_requests_total` with `rate(lab_requests_total[1m])`. Compare `increase(lab_requests_total[1m])` with `rate(lab_requests_total[1m])` multiplied by 60. Apply `rate()` to the gauge `lab_queue_depth` and explain the result. Restart the probe with `kubectl -n starfleet rollout restart deployment/probe` and watch the counter fall to zero and the rate stay smooth.

Remove the playground with `astrona destroy ats-047-playground-010-01` when you are done.
