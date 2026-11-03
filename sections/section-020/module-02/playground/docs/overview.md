---
draft: true
exam_objectives:
- Understand logs and events
---
# Correlation And Sampling Playground

This is an ungraded environment. Nothing here is submitted or graded, and you can change anything.

## What runs

The `starfleet` namespace holds the `shop` Deployment. It serves requests on port 8080 at `/work` and metrics at `/metrics`, and it writes one JSON log record to standard output for each request it logs. It logs every failed request and one successful request in five. The `prometheus` Deployment scrapes the shop every two seconds under the job `shop`. The `traffic` Deployment sends about two requests per second to the shop: one in six returns status `500`, and every failure uses the route `/checkout`. The `shuttle` pod is a plain Python container that you use to send requests inside the cluster. The `drifter` pod in the `outpost` namespace is a second client.

## Connect

```sh
export KUBECONFIG="$(astrona kubeconfig ats-047-playground-020-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-047-playground-020-02" || exit 1
```

## Things to try

Define a helper that sends PromQL (Prometheus Query Language) expressions to Prometheus.

```sh
prom_query() {
  kubectl -n starfleet exec shuttle -- python -c 'import sys,urllib.parse,urllib.request; print(urllib.request.urlopen("http://prometheus:9090/api/v1/query?"+urllib.parse.urlencode({"query":sys.argv[1]}),timeout=8).read().decode())' "$1"
}
prom_query 'sum by (status) (shop_http_requests_total)'
prom_query 'sum by (level) (shop_log_records_total)'
prom_query 'shop_log_records_sampled_out_total'
```

Compare the number of requests with status `200` and the number of `info` records. Count the request records in `kubectl -n starfleet logs deployment/shop --tail=200` and compare the share of `error` records with the failure ratio from the metric. Delete the shop pod with `kubectl -n starfleet delete pod -l app=shop` and watch the counters start again from zero while the old log is gone.

Remove the playground with `astrona destroy ats-047-playground-020-02` when you are done.
