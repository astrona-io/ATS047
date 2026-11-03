---
draft: true
exam_objectives:
- Service Discovery
---
# Select And Label Pod Targets Solution

Select the cluster of this lab:

```sh
export KUBECONFIG="$(astrona kubeconfig ats-047-lab-050-02-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-047-lab-050-02-01" || exit 1
```

## Write the rules

One `keep` rule selects the pods. Its regular expression is anchored, so `probe|scout` matches the label values `probe` and `scout` only. Pods without an `app` label have an empty value and do not match, so they are dropped. Three `replace` rules copy metadata into public labels, because labels that start with two underscores are removed after relabeling. Save this as `prometheus-config.yaml`:

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
      - source_labels: [__meta_kubernetes_pod_label_app]
        action: keep
        regex: probe|scout
      - source_labels: [__meta_kubernetes_namespace]
        target_label: namespace
      - source_labels: [__meta_kubernetes_pod_name]
        target_label: pod
      - source_labels: [__meta_kubernetes_pod_label_app]
        target_label: app
```

Apply it:

```sh
kubectl apply -f prometheus-config.yaml
```

Prometheus reads the file at start, so restart the Deployment. Then list the final labels of the targets of the job `pods`:

```sh
kubectl -n starfleet rollout restart deployment/prometheus
kubectl -n starfleet rollout status deployment/prometheus
kubectl -n starfleet exec shuttle -- python -c 'import json, urllib.request
data = json.load(urllib.request.urlopen("http://prometheus:9090/api/v1/targets", timeout=8))["data"]
for target in data["activeTargets"]:
    if target["labels"]["job"] == "pods":
        print(target["labels"], target["health"])'
```

Three targets remain: two `probe` pods and the `scout` pod, each with `namespace`, `pod` and `app`. Submit with `astrona submit -c .`, then remove the lab with `astrona destroy ats-047-lab-050-02-01`.

## Common pitfalls

> [!WARNING]
> A pattern such as `probe` alone drops `scout`, because the expression must match the whole value. Restart Prometheus after applying the ConfigMap, or the grader still reads the old rules. Public labels need a rule: the internal `__meta_` labels are not stored.
