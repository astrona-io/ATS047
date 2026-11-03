---
draft: true
exam_objectives:
- Service Discovery
---
# Selecting Targets With keep And drop

Pod discovery lists every pod in the watched namespaces, and most pods do not serve metrics. Scraping all of them wastes requests, creates `up` series with the value 0 and hides real failures in noise. Selection rules solve this: they decide which candidates become targets. This page covers the `keep` and `drop` actions, how a rule that reads several labels works, and how the anchored regular expression makes the difference between a working rule and a rule that silently removes the wrong pods.

## keep And drop

The `keep` action keeps a candidate only if the joined source labels match the regular expression. Every candidate that does not match is dropped. The `drop` action does the opposite: a matching candidate is dropped, and every other candidate stays. Both actions ignore `target_label` and `replacement`, because they change the set of targets and not a label.

A dropped candidate is not scraped and has no `up` series. It still exists in Prometheus for inspection. The targets API lists it under `droppedTargets` with its `discoveredLabels`, so you can see which candidates a rule removed and why a pod you expected is missing.

Choose between the two by the question you can answer. When you know what you want, for example "pods with the label `app` equal to `probe` or `scout`", write one `keep` rule. A `keep` rule is a list of what is allowed, so new pods are excluded until someone allows them. When you know what you do not want, such as one namespace, write a `drop` rule. A `drop` rule lets every new kind of pod through, including pods that do not expose metrics.

## Several Source Labels

A rule can read more than one label. Prometheus joins the values with the `separator`, in the order of `source_labels`, and matches the joined string against the regular expression. With the default separator `;`, the labels `__meta_kubernetes_namespace` and `__meta_kubernetes_pod_label_app` give a string such as `starfleet;probe`. The regular expression `starfleet;(probe|scout)` then matches pods named by both conditions at once.

A label that does not exist counts as an empty string. A pod without an `app` label produces `starfleet;`, which does not match `starfleet;(probe|scout)`, so a `keep` rule removes it. Remember that the label name in the metadata replaces characters that are invalid in a label name with underscores, so the pod label `app.kubernetes.io/name` becomes `__meta_kubernetes_pod_label_app_kubernetes_io_name`.

## Anchoring Decides The Result

The regular expression must match the whole joined string. Two examples show why this matters. The first rule in the exercise below keeps pods whose `app` label is exactly `probe`. A pod labeled `probe-v2` is dropped, and so is a pod labeled `scout`. Writing `probe.*` would keep the first and still drop the second, and writing `probe|scout` would keep `probe` and `scout` only. When a pod disappears, compare its label value with the expression character by character before you suspect discovery.

## Try It: Keep One Application, Then Two Conditions

Open a shell. The helper `show_selection` prints the pod name of the active targets and the pod name of the dropped targets of the job `pods`.

<!-- astrona:playground:renew -->

```sh
export KUBECONFIG="$(astrona kubeconfig ats-047-playground-050-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-047-playground-050-02" || exit 1
prom_get() {
  kubectl -n starfleet exec shuttle -- python -c 'import sys, urllib.request; print(urllib.request.urlopen("http://prometheus:9090" + sys.argv[1], timeout=8).read().decode())' "$1"
}
show_selection() {
  prom_get '/api/v1/targets?state=any' | python3 -c 'import json, sys
data = json.load(sys.stdin)["data"]
for state in ("activeTargets", "droppedTargets"):
    names = sorted(t["discoveredLabels"].get("__meta_kubernetes_pod_name", "?") for t in data[state] if t.get("scrapePool") == "pods")
    print(state, names)'
}
```

First keep only the pods whose `app` label is `probe`. Save this as `prometheus-config.yaml`:

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
        regex: probe
```

Apply it:

```sh
kubectl apply -f prometheus-config.yaml
```

Then restart Prometheus and list the selection:

```sh
kubectl -n starfleet rollout restart deployment/prometheus
kubectl -n starfleet rollout status deployment/prometheus
show_selection
```

The active list has the two `probe` pods. The `scout` pod is in the dropped list, because `scout` does not match the anchored expression `probe`. The pods without an `app` label are dropped as well. Now keep both applications, and only in the namespace `starfleet`, with one rule that reads two labels. Replace the `relabel_configs` block in `prometheus-config.yaml` with this one:

```yaml
      relabel_configs:
      - source_labels: [__meta_kubernetes_namespace, __meta_kubernetes_pod_label_app]
        action: keep
        regex: starfleet;(probe|scout)
```

Apply the file again, restart Prometheus and list the selection:

```sh
kubectl apply -f prometheus-config.yaml
kubectl -n starfleet rollout restart deployment/prometheus
kubectl -n starfleet rollout status deployment/prometheus
show_selection
```

The active list now has the two `probe` pods and the `scout` pod. Every other pod, including the `drifter` pod from `outpost`, is in the dropped list. To see the health of the active targets, query the API for `up`:

```sh
prom_get '/api/v1/query?query=up'
```

The result has one series per active target of the job `pods` and one for the job `prometheus`. A dropped pod has no series. Since the three kept pods declare port 8080 and serve metrics there, each series has the value 1 once the first scrape is done.

## What You Know Now

`keep` and `drop` decide which candidates become targets. A rule can read several labels joined by the separator, and the regular expression must match the whole joined string, so a small difference in a pattern removes the wrong pods without an error. Dropped targets stay visible in the targets API with their discovered labels, and they have no `up` series. The open question is how to correct a target whose address or path is wrong, and how to control which samples are stored after a scrape.

## Common pitfalls

> [!WARNING]
> An unanchored mental model causes most selection mistakes: `probe` does not match `probe-v2`. A missing label counts as an empty string, so a `keep` rule removes pods that lack the label. Do not conclude that a pod failed when it is missing from the active targets; look for it in the dropped targets first.
