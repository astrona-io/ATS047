---
draft: true
exam_objectives:
- Service Discovery
---
# Relabel Targets And Metrics

Discovery gives Prometheus a list of candidates with internal metadata. Relabeling turns that list into the targets Prometheus really scrapes, with the labels the stored series will carry. This module teaches how relabeling rules work, how to select targets and name their labels, how to rewrite the address and path of a scrape, and how metric relabeling differs from target relabeling.

## Learning Goals

- Read a `relabel_configs` rule and predict its result from `source_labels`, `separator`, `regex`, `replacement`, `target_label` and `action`.
- Use `keep`, `drop` and `replace` to select targets and copy metadata into public labels.
- Explain which labels survive relabeling and why labels that start with two underscores do not reach stored series.
- Rewrite `__address__` and `__metrics_path__` from pod annotations.
- Distinguish target relabeling from metric relabeling and drop a metric with `metric_relabel_configs`.
- Find duplicate coverage and explain why it double counts.

## Before You Start

You need to know what a scrape job and a Prometheus label are, and how `kubernetes_sd_configs` produces candidates with `__meta_kubernetes_*` labels. The playground starts with a Prometheus server that discovers all pods and applies no rules.

## Reading Order

1. How Target Relabeling Works
2. Selecting Targets With keep And drop
3. Rewriting Address And Path And Relabeling Metrics
4. Summary

<!-- astrona:playground -->
