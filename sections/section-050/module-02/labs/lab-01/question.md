---
draft: true
exam_objectives:
- Service Discovery
---
# Select And Label Pod Targets

The `probe` and `scout` pods in `starfleet` serve metrics. The other pods, including the `drifter` pod in `outpost`, do not, and they now produce failing scrapes.

## Starting state

Prometheus (Deployment `prometheus` in `starfleet`) has a static job `prometheus` and a job `pods` that discovers every pod in `starfleet` and `outpost` with the `pod` role. The job has no relabeling rules. Its configuration is the ConfigMap `prometheus-config`, key `prometheus.yaml`. The pods `probe` (two replicas) and `scout` carry the label `app` with their own name and declare port 8080.

Select the cluster of this lab:

```sh
export KUBECONFIG="$(astrona kubeconfig ats-047-lab-050-02-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-047-lab-050-02-01" || exit 1
```

## Required result

- Change `relabel_configs` of the job `pods` so that only pods whose label `app` is `probe` or `scout` become targets.
- Give each target the labels `namespace`, `pod` and `app`, with the namespace, the pod name and the value of the pod label `app`.
- Keep the job name, the `pod` role and both namespaces. Keep the job `prometheus`.
- Make the running Prometheus use the new configuration.

## Verify the result

Submit with `astrona submit -c .`. The grader reads the targets API of the running Prometheus. Allow a few seconds after a restart for the first scrapes.
