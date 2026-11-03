---
draft: true
exam_objectives:
- Service Discovery
---
# Discover Pods In One Namespace Solution

Select the cluster of this lab:

```sh
export KUBECONFIG="$(astrona kubeconfig ats-047-lab-050-01-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-047-lab-050-01-01" || exit 1
```

## Add the job

Prometheus reads its configuration from the ConfigMap `prometheus-config`. Save this as `prometheus-config.yaml`. It keeps the two static jobs and adds the job `pods` with the `pod` role, limited to `starfleet`:

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
```

Apply it:

```sh
kubectl apply -f prometheus-config.yaml
```

Prometheus reads the file at start, so restart the Deployment. Then check that the job lists the pods:

```sh
kubectl -n starfleet rollout restart deployment/prometheus
kubectl -n starfleet rollout status deployment/prometheus
kubectl -n starfleet exec shuttle -- python -c 'import json, urllib.request
data = json.load(urllib.request.urlopen("http://prometheus:9090/api/v1/targets?state=any", timeout=8))["data"]
for target in data["activeTargets"] + data["droppedTargets"]:
    found = target["discoveredLabels"]
    print(found.get("__meta_kubernetes_namespace"), found.get("__meta_kubernetes_pod_name"))'
```

Every line names the namespace `starfleet`. The `drifter` pod does not appear, because Prometheus never watches `outpost`. Submit with `astrona submit -c .`, then remove the lab with `astrona destroy ats-047-lab-050-01-01`.

## Common pitfalls

> [!WARNING]
> Applying the ConfigMap does not change the running server. Restart the Deployment, or the grader still sees the old configuration. Listing both namespaces makes the `drifter` pod a candidate and fails the check.
