---
draft: true
exam_objectives:
- Service Discovery
---
# Relabel Annotated Pods And Drop A Metric Solution

Select the cluster of this lab:

```sh
export KUBECONFIG="$(astrona kubeconfig ats-047-capstone-050)"
test "$(kubectl config current-context)" = "kind-astro-ats-047-capstone-050" || exit 1
```

## Find what is wrong

The `scout` pod declares no container port, so pod discovery gives it an address that is the pod IP address alone. Prometheus adds port 80 and scrapes the wrong place. The metrics are on the path `/stats`, but Prometheus asks for `/metrics`. You can see this in the targets API: the `scrapeUrl` of the `scout` target has no port, and its health is `down`.

```sh
kubectl -n starfleet exec shuttle -- python -c 'import json, urllib.request
data = json.load(urllib.request.urlopen("http://prometheus:9090/api/v1/targets", timeout=8))["data"]
for target in data["activeTargets"]:
    if target["scrapePool"] == "pods":
        print(target["scrapeUrl"], target["health"])'
```

## Write the rules

Three rules are new. The first writes `__metrics_path__` from the path annotation, and only when the annotation has a value. The second joins `__address__` and the port annotation with the separator `;` and rewrites the address to the host plus the annotated port. The third group copies metadata into public labels. The block `metric_relabel_configs` drops the metric after each scrape. Save this as `prometheus-config.yaml`:

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
    - job_name: pods
      kubernetes_sd_configs:
      - role: pod
        namespaces:
          names:
          - starfleet
          - outpost
      relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: "true"
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        regex: (.+)
        target_label: __metrics_path__
      - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
        target_label: __address__
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

Prometheus reads the file at start, so restart the Deployment and read the targets again:

```sh
kubectl -n starfleet rollout restart deployment/prometheus
kubectl -n starfleet rollout status deployment/prometheus
```

Run the previous Python command again. The `scout` target now has a scrape URL that ends with `:8080/stats` and the health `up`. Submit with `astrona submit -c .`, then remove the lab with `astrona destroy ats-047-capstone-050`.

## Common pitfalls

> [!WARNING]
> The regular expression of the address rule must handle an address with and without a port, which is why the port part is optional. Metric relabeling cannot repair a wrong address. If `lab_queue_depth` is still returned, wait for the next scrape: Prometheus then marks the old series stale.
