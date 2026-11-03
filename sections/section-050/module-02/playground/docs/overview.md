---
draft: true
exam_objectives:
- Service Discovery
---
# Playground: Relabel Targets And Metrics

This ungraded environment is a kind cluster with a private context. Nothing in it is graded, and you can change anything.

## What Runs In The Cluster

The `starfleet` namespace holds a Prometheus server, two `probe` pods and one `scout` pod that serve metrics on port 8080 on both `/metrics` and `/stats`, a `traffic` pod that sends requests to them, and a `shuttle` pod used to reach the Prometheus API from inside the cluster. The `outpost` namespace holds the `drifter` pod. The application exposes `lab_requests_total` and `lab_queue_depth`.

Prometheus runs a static job `prometheus` and a job `pods` that discovers every pod of both namespaces with the `pod` role and applies no relabeling. Its configuration is the ConfigMap `prometheus-config`. The server reads the file at start, so restart the Deployment after each change.

## Select The Cluster

```sh
export KUBECONFIG="$(astrona kubeconfig ats-047-playground-050-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-047-playground-050-02" || exit 1
```

## Things To Try

- Compare `discoveredLabels` and `labels` of a target in `/api/v1/targets`.
- Write a `keep` rule with a regular expression that is too narrow and find the missing pod under `droppedTargets`.
- Rewrite `__address__` and `__metrics_path__`, then read `scrapeUrl`.
- Drop `lab_queue_depth` with `metric_relabel_configs` and query it.
- Add a static job for `probe:8080` and compare series per `job`.

Remove the playground when you finish with `astrona destroy ats-047-playground-050-02`.
