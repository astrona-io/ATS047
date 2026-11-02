---
draft: true
exam_objectives:
- Push vs Pull
---
# Pull Scraping, Push Delivery And Short-Lived Jobs

Prometheus normally collects metrics by scraping targets. The target exposes current metric values, and Prometheus requests them on a configured schedule. In a push model, the producer initiates delivery to a receiving system. Both approaches can support useful observability, but they provide different evidence about producer health and data freshness.

## Pull Collection Owns The Schedule

The scraper controls interval, timeout and target selection. It can observe whether a target responds and whether the response can be processed. The generated up metric represents scrape success for the target. A value of one does not prove the application's business operations are correct; an application can serve a valid metrics endpoint while failing every user request.

Pull collection requires network reachability from the scraper to the target. Discovery determines which targets should be scraped, and access controls should allow that path while protecting the endpoint. A target removed from discovery and a discovered target with a failed scrape are different conditions. The former may no longer produce a current up series in the same way as the latter.

## Push Delivery Changes Failure Evidence

A push receiver can accept updates when the producer is active, but absent updates can have several meanings: the process stopped, its network failed, its schedule changed or no new work occurred. Freshness must be represented and interpreted deliberately. Successful delivery once does not establish continued producer health.

Short-lived jobs can finish before a normal scrape reaches them. The Prometheus Pushgateway is intended for selected service-level batch-job use cases where metrics need to remain available after completion. It is not the default design for every application or machine-level metric. Alternatives can preserve machine-associated batch results through an exporter when that better fits ownership and lifecycle.

## Manage Pushgateway Lifecycle

A pushed group remains in the gateway until it is replaced or deleted according to its API and lifecycle handling. Prometheus scraping the gateway can succeed even if the original batch job stopped running long ago. The gateway's up metric therefore describes the gateway scrape, not the liveness of every producer whose values it holds.

Grouping labels determine which pushed metrics belong together. Unbounded instance identifiers can accumulate stale groups and increase cardinality. Prefer a stable service-level identity where appropriate, and define who cleans obsolete groups. Represent the last successful batch completion explicitly when an alert needs to detect an overdue result.

## Distinguish Downstream Sample Transport

Remote write sends samples already collected by Prometheus or a compatible agent to a remote endpoint. It can support centralized storage or another downstream system, but it does not automatically instrument an application or discover a target. It also introduces queueing, retries and destination availability concerns that are separate from the original scrape.

A remote destination outage can coexist with successful local collection. Conversely, a healthy remote receiver cannot supply samples that the collector never obtained. Trace each stage of the path when interpreting freshness: producer exposition, collection, local processing and downstream delivery.

## Choose By Evidence And Ownership

For a long-running service, ordinary scraping often gives a clear target health and scheduling model. For a service-level batch result, retained pushed metrics may fit the lifecycle when their cleanup and freshness are explicit. Select the mechanism based on what is being measured, who owns its identity and how absence should be interpreted. Convenience alone is insufficient if it leaves stale data indistinguishable from current success.

## Common pitfalls

> [!WARNING]
> Scraping a Pushgateway successfully does not establish that every producer is alive. Pushed group cleanup, target discovery and remote write are distinct responsibilities.
