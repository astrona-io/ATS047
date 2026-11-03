---
draft: true
exam_objectives:
- Service Discovery
---
# Service Discovery

This section covers how Prometheus finds the endpoints it scrapes and how it turns discovered candidates into targets with the right address, path and labels. It has two modules. The first covers discovery, in particular `kubernetes_sd_configs`. The second covers relabeling of targets and of metrics. A capstone lab closes the section.

## Learning Outcomes

- Explain the difference between a static target list and service discovery, and name the common discovery mechanisms.
- Configure `kubernetes_sd_configs` with the `pod` role and limit it to chosen namespaces.
- Explain the roles `pod`, `service`, `endpoints`, `endpointslice`, `node` and `ingress`, and the permissions they need.
- Separate discovered candidates from active and dropped targets, and read `discoveredLabels` in the targets API.
- Write `relabel_configs` rules with `keep`, `drop` and `replace`, and predict their result from the anchored regular expression.
- Rewrite `__address__` and `__metrics_path__` from pod annotations.
- Distinguish target relabeling from metric relabeling and drop a metric after a scrape.
- Find duplicate coverage that double counts the same observations.

## The Learning Path

### 1. Discover Scrape Targets

Static lists, discovery mechanisms, the `pod` role, namespaces, other roles, permissions and churn. The module playground is a kind cluster with a Prometheus server that has static jobs and read access to pods. The graded lab adds a pod discovery job limited to one namespace.

### 2. Relabel Targets And Metrics

How a relabeling rule is evaluated, `keep` and `drop`, rewriting the address and the path, `metric_relabel_configs` and duplicate coverage. The module playground is a kind cluster with a Prometheus server that discovers every pod without rules. The graded lab selects and labels the `probe` and `scout` pods.

### Section Capstone

A graded lab in `capstone/labs/lab-01`. The reader fixes the scrape of annotated pods (a pod without a declared port and a custom path), adds the labels `namespace`, `pod` and `app`, and drops one metric. All labs are marked UNTESTED: they pass static validation only and have not been booted.

## Knowledge Check

The file `quiz.yaml` holds the section quiz as a question bank in draft status.
