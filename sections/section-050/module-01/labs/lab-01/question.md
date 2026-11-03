---
draft: true
exam_objectives:
- Service Discovery
---
# Discover Pods In One Namespace

The platform team no longer wants to scrape `probe:8080` through the Service only. The `starfleet` pods must be discovered as individual candidates, and the `drifter` pod in `outpost` must not be discovered.

## Starting state

The `starfleet` namespace runs a Prometheus server (Deployment `prometheus`), two `probe` pods, one `scout` pod, a `traffic` pod and a `shuttle` pod. The `outpost` namespace runs the `drifter` pod. Prometheus has two static jobs: `prometheus` and `probe`. Its ServiceAccount may list and watch pods in every namespace. Its configuration is the ConfigMap `prometheus-config`, key `prometheus.yaml`.

Select the cluster of this lab:

```sh
export KUBECONFIG="$(astrona kubeconfig ats-047-lab-050-01-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-047-lab-050-01-01" || exit 1
```

## Required result

- Add a scrape job named `pods` that uses `kubernetes_sd_configs` with the `pod` role.
- Limit discovery to the namespace `starfleet`.
- Keep the jobs `prometheus` and `probe` as they are.
- Make the running Prometheus use the new configuration.

Do not add relabeling rules. Every pod of `starfleet` stays a candidate, whether or not it serves metrics.

## Verify the result

Submit with `astrona submit -c .`. The grader asks the Prometheus API which pods the job `pods` discovered. Prometheus needs a few seconds after a restart before its target list is complete.
