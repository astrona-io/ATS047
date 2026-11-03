---
draft: true
exam_objectives:
- Service Discovery
---
# Discovering Pods With kubernetes_sd_configs

A static target that names a Service hides the pods behind it. Kubernetes service discovery solves this: Prometheus asks the Kubernetes API server for the pods themselves and builds one candidate per pod. This page adds a discovery job to a running Prometheus, shows what the candidates look like before any rule touches them, and limits discovery to the namespaces you choose.

## The kubernetes_sd_configs Block

`kubernetes_sd_configs` is a list under a scrape job. Each entry has a `role` that says which kind of Kubernetes object Prometheus lists and watches. The `pod` role returns every pod. Prometheus opens a watch connection to the Kubernetes API server, receives the current pods, and then receives an event each time a pod is created, changed or deleted. It does not poll on a timer.

```yaml
- job_name: pods
  kubernetes_sd_configs:
  - role: pod
    namespaces:
      names:
      - starfleet
```

The `namespaces` field limits discovery to the named namespaces. Without it, Prometheus watches pods in every namespace, and it needs permission to do so. With it, Prometheus watches only the listed namespaces, which reduces both the data it keeps in memory and the permissions it needs. The `selectors` field narrows the list further on the API server side, with a label selector or a field selector for one role.

## One Candidate Per Declared Port

The `pod` role creates candidates from the container ports declared in the pod specification. For each container port that a pod declares, Prometheus creates one candidate whose `__address__` is the pod IP address and that port, for example `10.244.1.5:8080`. A pod with two declared ports gives two candidates. A container that declares no port gives one candidate whose address is the pod IP address alone, without a port.

The port is only a hint. A declared `containerPort` is documentation in Kubernetes: the container may listen on other ports, and it may not serve metrics on the declared one. Prometheus does not check this at discovery time. It finds out when it scrapes. When an address has no port, Prometheus adds the default port of the scheme, which is 80 for `http`. The scrape then goes to the wrong place and fails.

Every candidate also carries metadata. These are the main internal labels of the `pod` role:

- `__meta_kubernetes_namespace`: the namespace of the pod.
- `__meta_kubernetes_pod_name`: the name of the pod.
- `__meta_kubernetes_pod_ip`: the IP address of the pod.
- `__meta_kubernetes_pod_label_<name>`: one label per pod label, for example `__meta_kubernetes_pod_label_app`. Characters that are not valid in a label name become underscores.
- `__meta_kubernetes_pod_annotation_<name>`: one label per pod annotation, sanitized in the same way.
- `__meta_kubernetes_pod_container_name` and `__meta_kubernetes_pod_container_port_number`: the container and the declared port that produced the candidate.
- `__meta_kubernetes_pod_phase` and `__meta_kubernetes_pod_ready`: the pod phase and whether it is ready.

## Try It: Add A Pod Discovery Job

Open a shell and repeat the setup. The helper `show_discovered` prints, for every active and every dropped target of the job `pods`, the namespace, the pod name and the address before any relabeling.

<!-- astrona:playground:renew -->

```sh
export KUBECONFIG="$(astrona kubeconfig ats-047-playground-050-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-047-playground-050-01" || exit 1
prom_get() {
  kubectl -n starfleet exec shuttle -- python -c 'import sys, urllib.request; print(urllib.request.urlopen("http://prometheus:9090" + sys.argv[1], timeout=8).read().decode())' "$1"
}
show_discovered() {
  prom_get '/api/v1/targets?state=any' | python3 -c 'import json, sys
data = json.load(sys.stdin)["data"]
for state in ("activeTargets", "droppedTargets"):
    for target in data[state]:
        found = target["discoveredLabels"]
        if found.get("job") == "pods" or target.get("scrapePool") == "pods":
            print(state, found.get("__meta_kubernetes_namespace"), found.get("__meta_kubernetes_pod_name"), found.get("__address__"))'
}
```

Add the discovery job next to the two static jobs. The configuration lives in the ConfigMap `prometheus-config`. Save this as `prometheus-config.yaml`:

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
          - outpost
```

Apply it:

```sh
kubectl apply -f prometheus-config.yaml
```

The Prometheus container reads its configuration file when it starts, so restart the Deployment and wait until the new pod is ready. Then list what discovery found:

```sh
kubectl -n starfleet rollout restart deployment/prometheus
kubectl -n starfleet rollout status deployment/prometheus
show_discovered
```

The output lists the `probe` pods, the `scout` pod, the `traffic` pod, the `shuttle` pod, the Prometheus pod itself and the `drifter` pod from the `outpost` namespace. Pods that declare a port show an address with that port. Pods that declare none, such as `shuttle`, `traffic` and `drifter`, show their IP address alone. Now check the scrape result of the same job:

```sh
prom_get '/api/v1/targets' | python3 -c 'import json, sys
for target in json.load(sys.stdin)["data"]["activeTargets"]:
    if target["labels"]["job"] == "pods":
        print(target["scrapeUrl"], target["health"], target["lastError"][:60])'
```

The targets that declared port 8080 or 9090 are healthy. The targets without a port are scraped on port 80 and report an error, because nothing listens there. All of them are active targets, since no rule removed any candidate. Discovery gave the complete list of pods, and only some of those pods expose metrics.

## Limit Discovery To One Namespace

Change `names` so that only `starfleet` is listed: edit `prometheus-config.yaml`, remove the line `- outpost`, apply the file again and restart the Deployment. Then run `show_discovered` again. The `drifter` pod is gone from the list, because the Kubernetes watch for the `outpost` namespace no longer exists. This is different from a dropped target. A dropped target was discovered and then removed by a rule. A pod in an unwatched namespace is never discovered, so it does not appear in the dropped targets either.

## What You Know Now

The `pod` role gives one candidate per declared container port, with the pod IP address as the host and many `__meta_kubernetes_*` labels as metadata. The candidate list includes every pod in the watched namespaces, including pods that do not serve metrics. Namespaces restrict what is discovered at all, while rules decide which candidates become targets. What remains open is how other roles differ, which permissions discovery needs, and what happens when pods are replaced.

## Common pitfalls

> [!WARNING]
> A declared `containerPort` does not prove that the container serves metrics there, and a pod without a declared port gives an address without a port that Prometheus scrapes on port 80. Editing the ConfigMap does not change the running server: Prometheus reads the file at start or on a reload, so restart the Deployment or reload the configuration after each change.
