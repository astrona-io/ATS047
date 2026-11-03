---
draft: true
exam_objectives:
- Service Discovery
---
# Relabel Annotated Pods And Drop A Metric

The `scout` pod in `starfleet` is annotated for scraping, but Prometheus scrapes it in the wrong place, and the platform team no longer wants the `lab_queue_depth` metric stored.

## Starting state

Prometheus (Deployment `prometheus` in `starfleet`) has a static job `prometheus` and a job `pods` that discovers pods in `starfleet` and `outpost` with the `pod` role. One rule keeps pods whose annotation `prometheus.io/scrape` is `true`. The `probe` pods (two replicas) and the `scout` pod carry that annotation and the annotation `prometheus.io/port` with the value `8080`. The `scout` pod also has `prometheus.io/path` with the value `/stats` and declares no container port. The `probe` pods declare port 8080 and use the default path. The configuration is the ConfigMap `prometheus-config`, key `prometheus.yaml`.

Select the cluster of this lab:

```sh
export KUBECONFIG="$(astrona kubeconfig ats-047-capstone-050)"
test "$(kubectl config current-context)" = "kind-astro-ats-047-capstone-050" || exit 1
```

## Required result

- Every pod with the scrape annotation is scraped successfully. The scrape address comes from the pod IP address and the port annotation, and the path comes from the path annotation when the pod has one.
- Each target has the labels `namespace`, `pod` and `app` (the value of the pod label `app`).
- The samples named `lab_queue_depth` of the job `pods` are not stored. `lab_requests_total` stays.
- The rules read the annotations. Do not write pod names or ports into the rules. Keep the `keep` rule and the job `prometheus`.
- Make the running Prometheus use the new configuration.

## Verify the result

Submit with `astrona submit -c .`. The grader reads the targets API and runs queries against the running Prometheus. Allow a few seconds after a restart for the first scrapes.
