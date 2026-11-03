---
draft: true
exam_objectives:
- Service Discovery
---
# Playground: Discover Scrape Targets

This ungraded environment is a kind cluster (Kubernetes running in containers) with a private context. Nothing in it is graded, and you can change anything.

## What Runs In The Cluster

The `starfleet` namespace holds a Prometheus server with its own ServiceAccount and a ClusterRole that lets it list and watch pods, Services, endpoints, EndpointSlices and nodes. It also holds two `probe` pods and one `scout` pod that serve metrics on port 8080, a `traffic` pod that sends requests to them every half second, and a `shuttle` pod used to reach the Prometheus API from inside the cluster. The `outpost` namespace holds one `drifter` pod.

Prometheus starts with two static jobs: `prometheus` scrapes itself and `probe` scrapes the Service name `probe:8080`. Its configuration is the ConfigMap `prometheus-config`. The server reads the file at start, so restart the Deployment after each change.

## Select The Cluster

```sh
export KUBECONFIG="$(astrona kubeconfig ats-047-playground-050-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-047-playground-050-01" || exit 1
```

## Things To Try

- Read the targets API with the `shuttle` pod: `/api/v1/targets?state=any` returns active and dropped targets with their `discoveredLabels`.
- Add a job with `kubernetes_sd_configs` and the `pod` role, then restrict it to one namespace.
- Switch the role to `endpoints` and compare the discovered labels.
- Scale the `probe` Deployment and watch the candidate list change without editing the configuration.
- Ask the API server what the Prometheus ServiceAccount may do with `kubectl auth can-i --as=system:serviceaccount:starfleet:prometheus`.

Remove the playground when you finish with `astrona destroy ats-047-playground-050-01`.
