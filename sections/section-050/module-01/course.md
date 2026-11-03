---
draft: true
exam_objectives:
- Service Discovery
---
# Discover Scrape Targets

Prometheus collects metrics by pulling them from HTTP endpoints. Before it can pull anything, it needs a list of endpoints. This module teaches how Prometheus builds that list: first from a fixed list in the configuration, then dynamically by asking the Kubernetes API which pods exist.

## Learning Goals

- Explain the difference between a target list written by hand and a target list produced by service discovery.
- Name the mechanisms Prometheus can use to discover targets and the kind of data each one returns.
- Configure `kubernetes_sd_configs` with the `pod` role and limit it to chosen namespaces.
- Read the discovered labels of a target in the targets API and tell a discovered candidate from a scraped target.
- Explain which Kubernetes permissions discovery needs, what happens when pods are replaced, and how the `endpoints` role differs from the `pod` role.

## Before You Start

You need basic knowledge of pods, Services and namespaces in Kubernetes, and of what a Prometheus scrape is. The playground gives you a Kubernetes cluster with a Prometheus server that has permission to read pods, and a small set of workloads that expose metrics.

## Reading Order

1. Static And Dynamic Service Discovery
2. Discovering Pods With kubernetes_sd_configs
3. Discovery Roles, Permissions And Churn
4. Summary

<!-- astrona:playground -->
