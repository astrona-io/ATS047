---
draft: true
exam_objectives:
- Service Discovery
---
# Summary

Prometheus pulls metrics, so it needs a list of targets. A static list is a set of addresses in the configuration file. It is easy to read, but it cannot follow a cluster in which pods are created, deleted and moved, and a static address that names a Service hides the individual pods behind it.

Service discovery replaces the list with a source to ask. Mechanisms such as files, DNS, Consul, cloud provider APIs and the Kubernetes API each return candidates with an address and a set of internal `__meta_` labels. Discovery only produces candidates. Target relabeling then decides which candidates become active targets. Only active targets are scraped and have an `up` series, and a dropped target has no series at all.

With `kubernetes_sd_configs`, Prometheus watches the Kubernetes API server and receives an event for each change. The `pod` role gives one candidate per declared container port, with the pod IP address as host. A container without a declared port gives an address without a port, which Prometheus scrapes on port 80. The `namespaces` field limits what is watched. A pod in an unwatched namespace is never discovered.

Other roles describe other objects: a Service port, a Service endpoint, a node or an Ingress path. Each role needs `get`, `list` and `watch` on its own resources through the ServiceAccount of the Prometheus pod. A missing permission gives an empty job and an error in the Prometheus log.

Key facts:

- A candidate is not a target until target relabeling keeps it.
- No `up` series means dropped or never discovered. `up` equal to 0 means scraped and failed.
- The configuration file is read at start or on a reload, so edits need a restart or a reload.
- Replaced pods create new targets with new addresses and new series.

<!-- astrona:playground:destroy -->
