---
draft: true
exam_objectives:
- Service Discovery
---
# Discovering Targets And Relabeling Their Identity

Service discovery identifies where metrics might be collected. Static configuration lists targets directly, while dynamic discovery obtains candidates from systems such as Kubernetes, cloud APIs or files. Discovery does not itself guarantee that an endpoint is selected, reachable or exposing the intended metrics.

## Candidates And Selected Targets

A discovery mechanism supplies addresses and metadata about candidate targets. Kubernetes discovery can identify different resource roles, such as Pods or endpoint-related objects, depending on configuration. The selected role affects which candidates and metadata are available. Permission to read the relevant API objects is part of the discovery contract.

Prometheus then applies target relabeling before scraping. Rules can keep or drop candidates, change the scrape address, select a path or scheme, and retain useful metadata as ordinary target labels. A broad discovery configuration without appropriate selection can scrape unintended endpoints or create duplicate coverage. Conversely, an overly narrow rule can silently exclude the service whose metrics are needed.

## Internal Labels Have A Lifecycle

Discovery metadata commonly appears under internal labels beginning with double underscores, including provider-specific __meta labels. These labels serve configuration processing and are not automatically retained as ordinary labels on stored samples. If a namespace or service name should remain available for queries, explicitly map the appropriate metadata to a suitable public label.

Internal target labels also describe settings such as the address and metrics path. Changing them affects where the scraper sends a request. A public label called service, however, is descriptive series identity unless a rule explicitly uses it to configure a target. Similar-looking labels can therefore have very different roles.

## Relabeling Stages Are Different

Target relabeling acts on target metadata before collection. Metric relabeling acts on samples after a scrape and can drop selected metrics or transform sample labels before ingestion. Dropping a high-cardinality metric at ingestion can reduce storage cost, but it does not undo the cost of producing and transferring that metric during the scrape.

A target excluded before scraping does not produce the same health evidence as a target that remains selected but fails to respond. Review the target list and discovery state before interpreting a missing series as application failure. A discovered object may also advertise a port that is not the actual metrics endpoint.

## Evaluate A Dynamic Scenario

Suppose application replicas are replaced and receive new addresses. Dynamic discovery can follow those changes, while stable service and namespace labels allow fleet-level queries. Per-instance labels still distinguish series from each replica. If two scrape jobs select the same endpoint under different job labels, the same underlying observations may be stored twice and accidentally double-counted by a broad aggregation.

Target identity should support both attribution and aggregation. Retaining every discovery annotation indiscriminately can increase cardinality and expose information unnecessarily. Choose labels for a defined query or ownership need. Avoid unbounded request or user identifiers in the target identity.

## Diagnose Coverage In Order

First ask whether discovery can access the source and whether the expected object appears. Then examine relabeling selection, effective address, path and protocol. Finally consider network access, authentication and response parsing. A scrape failure and discovery exclusion require different corrections. Maintaining that sequence prevents a configuration change at the wrong stage from hiding the real coverage gap.

## Common pitfalls

> [!WARNING]
> Discovery produces candidates, not guaranteed successful scrapes. Target relabeling and metric relabeling occur at different stages, and internal metadata is not automatically retained on stored series.
