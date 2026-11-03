---
draft: true
exam_objectives:
- Metrics
---
# Labels And Aggregation Playground

This is an ungraded environment. Nothing here is submitted or graded, and you can change anything.

## What runs

The `starfleet` namespace holds two instances of a shop application, `shop-a` and `shop-b`, that both serve metrics on port 8080 at `/metrics`. The `prometheus` Deployment scrapes both every two seconds under the job `shop`. The `traffic` Deployment sends about four requests per second to `shop-a`, with one failure in ten, and about one request per second to `shop-b`, with one failure in two. Requests use three routes and fifty user identifiers. The `shuttle` pod is a plain Python container that you use to send requests inside the cluster.

## Connect

```sh
export KUBECONFIG="$(astrona kubeconfig ats-047-playground-010-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-047-playground-010-02" || exit 1
```

## Things to try

Define a helper that sends PromQL (Prometheus Query Language) expressions to Prometheus.

```sh
prom_query() {
  kubectl -n starfleet exec shuttle -- python -c 'import sys,urllib.parse,urllib.request; print(urllib.request.urlopen("http://prometheus:9090/api/v1/query?"+urllib.parse.urlencode({"query":sys.argv[1]}),timeout=8).read().decode())' "$1"
}
prom_query 'count by (__name__) ({job="shop"})'
prom_query 'sum by (route) (rate(shop_http_requests_total[1m]))'
prom_query 'sum by (instance) (rate(shop_http_requests_total{status="500"}[1m])) / sum by (instance) (rate(shop_http_requests_total[1m]))'
```

Compare the fleet error ratio with the average of the two instance ratios. Remove the `user_id` label with `sum without (user_id) (rate(shop_user_requests_total[1m]))` and count the series before and after. Stop the traffic with `kubectl -n starfleet scale deployment/traffic --replicas=0`, wait two minutes and watch what a one-minute `rate()` returns. Scale it back to 1 afterwards.

Remove the playground with `astrona destroy ats-047-playground-010-02` when you are done.
