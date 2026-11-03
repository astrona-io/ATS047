---
draft: true
exam_objectives:
- Service Discovery
---
# Discovery Roles, Permissions And Churn

Pod discovery is one of several ways to look at a Kubernetes cluster. The choice of role decides what a candidate represents, which metadata it carries and which permissions Prometheus needs. A cluster also changes while Prometheus runs, and discovery must follow those changes without a reload. This page compares the roles, shows the permissions behind them and watches discovery react when pods are replaced.

## The Roles

Each `kubernetes_sd_configs` entry names one role. The role selects the Kubernetes object type and the shape of the candidates:

- `pod`: one candidate per declared container port of each pod, as the previous page showed.
- `service`: one candidate per Service port. The address is the DNS name of the Service. Scraping it reaches one pod behind the Service at a time. This role fits a check of the Service as a whole, such as a blackbox probe, and not the collection of per-pod metrics.
- `endpoints`: one candidate per endpoint address and port of a Service. The address is a pod IP address and port, and the metadata includes both Service labels and pod labels. For endpoint addresses that belong to a pod, the metadata also describes the pod. The role also adds a candidate for each declared pod port that the Service does not list.
- `endpointslice`: the same idea as `endpoints`, built from `EndpointSlice` objects, which Kubernetes uses to scale Services to many pods.
- `node`: one candidate per cluster node, with the address of the kubelet. Use it for node-level metrics.
- `ingress`: one candidate per path of an Ingress, usually for probing the external URL.

For per-pod application metrics, `pod` and `endpoints` are the common choices. Use `pod` when the pod itself carries the information about how to scrape it, for example in annotations. Use `endpoints` when the Service is the unit you want to describe, because it adds `__meta_kubernetes_service_name` and the Service labels, and it lists only pods that a Service selects.

## Permissions

Discovery uses the Kubernetes API, so it follows Kubernetes authorization. The Prometheus pod runs as a ServiceAccount, and that account needs `get`, `list` and `watch` on every resource type that the configured roles use: `pods` for the `pod` role, `services`, `endpoints` and `pods` for the `endpoints` role, `endpointslices` in the `discovery.k8s.io` group for the `endpointslice` role, and `nodes` for the `node` role.

In the playground, a ClusterRole named `prometheus-discovery` grants these verbs on those resources, and a ClusterRoleBinding gives it to the ServiceAccount `prometheus`. When the permission is missing, nothing is dropped and nothing fails loudly in the targets list. Prometheus logs an error from the Kubernetes client, the watch for that role never succeeds, and the job shows no candidates. The result looks like "no targets", which an administrator can mistake for a configuration mistake. Always check permissions when a Kubernetes job is empty.

## Churn

Discovery is event-driven. When a Deployment replaces a pod, the Kubernetes API server sends a delete event for the old pod and an add event for the new one. Prometheus updates the candidates immediately. The old target disappears from the active targets. Its series stop receiving samples and become stale. The new pod becomes a new target with a new IP address and a new `__meta_kubernetes_pod_name`. A new target means new series, and series from the old pod remain in storage until they age out.

This has a consequence for queries. Labels that carry the pod name or address change on every replacement, so a long-term series for "one replica" does not exist. Fleet-level queries aggregate over labels that stay stable, such as the application name. The labels you keep for a target decide whether you can aggregate and whether you can drill down to one replica.

## Try It: Check Permissions And Follow Replacements

Open a shell with the playground selected. `kubectl auth can-i` with `--as` asks the API server whether another identity may perform an action, without acting as that identity.

<!-- astrona:playground:renew -->

```sh
export KUBECONFIG="$(astrona kubeconfig ats-047-playground-050-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-047-playground-050-01" || exit 1
kubectl auth can-i list pods --all-namespaces --as=system:serviceaccount:starfleet:prometheus
kubectl auth can-i list secrets -n starfleet --as=system:serviceaccount:starfleet:prometheus
```

The first command prints `yes`, because the ClusterRole allows listing pods in every namespace. The second prints `no`: discovery needs no access to Secrets, and the role does not grant it. Compare these answers with the rules of the ClusterRole:

```sh
kubectl get clusterrole prometheus-discovery -o yaml
```

Now switch the job to the `endpoints` role and compare the candidates. Save this as `prometheus-config.yaml`:

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
    - job_name: endpoints
      kubernetes_sd_configs:
      - role: endpoints
        namespaces:
          names:
          - starfleet
```

Apply it and restart Prometheus:

```sh
kubectl apply -f prometheus-config.yaml
kubectl -n starfleet rollout restart deployment/prometheus
kubectl -n starfleet rollout status deployment/prometheus
```

Print the Service name and the pod name that discovery attached to each candidate:

```sh
kubectl -n starfleet exec shuttle -- python -c 'import json, urllib.request
data = json.load(urllib.request.urlopen("http://prometheus:9090/api/v1/targets?state=any", timeout=8))["data"]
for target in data["activeTargets"] + data["droppedTargets"]:
    found = target["discoveredLabels"]
    print(found.get("__meta_kubernetes_service_name"), found.get("__meta_kubernetes_pod_name"), found.get("__address__"))'
```

Candidates for the `probe` Service name each `probe` pod and its IP address. The `scout` and `prometheus` Services appear with their pods in the same way. Pods that no Service selects, such as `shuttle` and `traffic`, do not appear at all, because the `endpoints` role starts from Services. Last, change the replica count and print the same list again after a short wait:

```sh
kubectl -n starfleet scale deployment/probe --replicas=3
kubectl -n starfleet rollout status deployment/probe
```

A third `probe` candidate appears without any change to the Prometheus configuration. Scale back to two replicas to restore the starting state and watch the extra candidate disappear:

```sh
kubectl -n starfleet scale deployment/probe --replicas=2
```

## What You Know Now

The role chooses what a candidate is: a pod port, a Service port, a Service endpoint, a node or an Ingress path. Each role needs read access to its own Kubernetes resources, and a missing permission produces an empty job, not an error in the target list. Discovery follows pod creation and deletion on its own through watch events, so the target list tracks the cluster as long as the selection rules stay correct. The remaining work is deciding which candidates to keep and which labels to give them, which is done by target relabeling.

## Common pitfalls

> [!WARNING]
> An empty Kubernetes job often means a missing `list` or `watch` permission, not a wrong rule: read the Prometheus logs and check `kubectl auth can-i` for the ServiceAccount. The `endpoints` role only sees pods that a Service selects, so a pod without a Service never appears. Labels that hold a pod name or IP address change at every replacement, so aggregate on stable labels.
