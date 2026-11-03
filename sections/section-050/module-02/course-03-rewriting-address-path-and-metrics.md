---
draft: true
exam_objectives:
- Service Discovery
---
# Rewriting Address And Path And Relabeling Metrics

Selection and naming are only part of relabeling. A selected target can still be scraped in the wrong place: the declared port may be missing or wrong, or the metrics may live on a different path. And a target that is scraped correctly can still return samples you do not want to store. This page shows how target relabeling changes the scrape request, how metric relabeling processes the samples after the scrape, and how the same endpoint can end up in storage twice.

## Changing Where Prometheus Scrapes

A scrape request is built from internal labels. `__address__` is the host and port, `__scheme__` is `http` or `https`, and `__metrics_path__` is the path. A `replace` rule can write any of them, and the scrape uses the new value. This is how one convention serves many applications: each pod states in its annotations where its metrics are, and the rules copy those values into the internal labels.

The common convention uses three pod annotations: `prometheus.io/scrape`, `prometheus.io/port` and `prometheus.io/path`. These names are a habit of the community and not a feature of Prometheus. Prometheus does nothing with them unless your rules read them. In the pod role they arrive as `__meta_kubernetes_pod_annotation_prometheus_io_scrape`, `__meta_kubernetes_pod_annotation_prometheus_io_port` and `__meta_kubernetes_pod_annotation_prometheus_io_path`.

Three rules implement the convention. A `keep` rule on the `scrape` annotation with the regular expression `true` selects the pods. A `replace` rule on the `path` annotation writes `__metrics_path__` when the annotation exists. A `replace` rule reads `__address__` and the `port` annotation together, with the regular expression `([^:]+)(?::\d+)?;(\d+)` and the replacement `$1:$2`. It keeps the host of the address, drops any existing port and appends the port from the annotation. The same rule fixes a pod whose address has no port.

## Metric Relabeling

Target relabeling runs before the scrape and changes targets. Metric relabeling runs after the scrape and changes samples. It uses `metric_relabel_configs` in the same scrape job. The rule fields and actions are the same, but each rule runs once for every sample, and the metric name is available as the label `__name__`. A rule with `source_labels: [__name__]`, `regex: lab_queue_depth` and `action: drop` removes every sample with that name before storage.

The two stages have different effects. Metric relabeling cannot change which targets exist or where they are scraped, because the scrape is already done. Dropping a metric saves storage and query cost, but the application still computes the metric and the response still carries it over the network. The generated series `up` and the other scrape metrics, such as `scrape_samples_scraped`, are added by Prometheus and are not subject to the rules of the job's `metric_relabel_configs`.

## Duplicate Coverage

Two jobs that reach the same process produce two sets of series. A static job for `probe:8080` and a pod discovery job both scrape the `probe` pods. The series differ in their `job` and `instance` labels, so Prometheus stores both. A query that aggregates without the `job` label adds the same observations twice. Check coverage with a query that groups by `job`, and give every endpoint one owner.

## Try It: Rewrite Address And Path, Drop A Metric

Open a shell with the helper `prom_query`, which URL-encodes an expression and sends it to the Prometheus API through the `shuttle` pod.

<!-- astrona:playground:renew -->

```sh
export KUBECONFIG="$(astrona kubeconfig ats-047-playground-050-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-047-playground-050-02" || exit 1
prom_query() {
  kubectl -n starfleet exec shuttle -- python -c 'import sys, urllib.parse, urllib.request
url = "http://prometheus:9090/api/v1/query?query=" + urllib.parse.quote(sys.argv[1])
print(urllib.request.urlopen(url, timeout=8).read().decode())' "$1"
}
```

The next configuration keeps the `probe` and `scout` pods, builds the address from the pod IP address and port 8080, sets the path to `/stats` (the sample application serves its metrics on `/metrics` and on `/stats`), copies three labels and drops the metric `lab_queue_depth`. It also keeps a static job for `probe:8080` on purpose, so you can see duplicate coverage. Save this as `prometheus-config.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: starfleet
data:
  prometheus.yaml: |
    global:
      scrape_interval: 5s
      evaluation_interval: 5s
    scrape_configs:
    - job_name: prometheus
      static_configs:
      - targets:
        - localhost:9090
    - job_name: probe
      static_configs:
      - targets:
        - probe:8080
    - job_name: pods
      kubernetes_sd_configs:
      - role: pod
        namespaces:
          names:
          - starfleet
      relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        action: keep
        regex: probe|scout
      - source_labels: [__meta_kubernetes_pod_ip]
        target_label: __address__
        replacement: $1:8080
      - target_label: __metrics_path__
        replacement: /stats
      - source_labels: [__meta_kubernetes_namespace]
        target_label: namespace
      - source_labels: [__meta_kubernetes_pod_name]
        target_label: pod
      - source_labels: [__meta_kubernetes_pod_label_app]
        target_label: app
      metric_relabel_configs:
      - source_labels: [__name__]
        regex: lab_queue_depth
        action: drop
```

Apply it:

```sh
kubectl apply -f prometheus-config.yaml
```

Restart Prometheus, then check the scrape URLs and the metric that the rule drops:

```sh
kubectl -n starfleet rollout restart deployment/prometheus
kubectl -n starfleet rollout status deployment/prometheus
prom_query 'count(lab_queue_depth{job="pods"})'
```

The scrape URLs of the job `pods` end with `:8080/stats`. Read them in the `scrapeUrl` field of `/api/v1/targets`. The query for `lab_queue_depth` in the job `pods` returns an empty result list, because the rule dropped every sample with that name. The static job `probe` has no `metric_relabel_configs`, so it still stores the metric. Confirm both facts by grouping by job:

```sh
prom_query 'count by (job) (lab_queue_depth)'
prom_query 'count by (job) (lab_requests_total{service="probe"})'
```

The first query returns a series for the job `probe` only, because the pod job drops the metric. The second shows series from both the job `probe` and the job `pods` for the same application. A sum without the `job` label would count each request twice. Remove the static `probe` job from `prometheus-config.yaml`, apply it again and restart Prometheus to give the endpoint a single owner.

## What You Know Now

Target relabeling can rewrite the address, scheme and path of a scrape, so one convention in pod annotations can serve many applications. Metric relabeling processes samples after the scrape and can drop a metric by name, which saves storage but not the cost of producing it. Two jobs that reach the same process store two sets of series, so group by `job` to check coverage. A selected target now has the right address, path, labels and samples.

## Common pitfalls

> [!WARNING]
> The `prometheus.io/*` annotations have no effect unless your rules read them. A `replace` rule without a regular expression that matches leaves `__address__` unchanged, so check `scrapeUrl` after each change. Metric relabeling cannot fix a wrong address or a missing target, and it does not stop the application from producing the dropped metric.
