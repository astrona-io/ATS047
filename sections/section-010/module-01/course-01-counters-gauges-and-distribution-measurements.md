---
draft: true
exam_objectives:
- Metrics
---
# Counters, Gauges And Distribution Measurements

A metric is a numerical observation with a defined meaning. Its type describes how the value behaves and which calculations are appropriate. Prometheus commonly works with counters, gauges, histograms and summaries. Choosing the type requires knowing the measured quantity rather than deciding how the eventual chart should look.

## Counters Accumulate Events

A counter records accumulated events or amounts, such as completed requests or bytes sent. It normally increases until its owning state resets, often during process restart. A decrease is therefore interpreted differently from ordinary falling demand. Query functions such as rate and increase use that counter model to estimate activity from collected samples.

The raw counter is not a current requests-per-second value. A process that has run longer may expose a larger total despite currently doing less work. Compare activity over appropriate windows rather than rank service health by cumulative totals alone. A visible reset can be handled, but events never collected cannot be reconstructed perfectly.

## Gauges Describe Current State

A gauge can rise or fall as ordinary behavior. Queue depth, temperature and current memory consumption are examples. Setting a gauge to a current observed value differs from incrementing a counter when an event occurs. A decrease in queue depth can mean work completed rather than a reset.

Gauge calculations can summarize recent values or estimate a trend. Counter rate functions should not be used merely because a gauge graph has an upward segment. The semantic contract governs the function choice. A value called total is not a counter if the producer overwrites it with an arbitrary current state.

## Distributions Preserve More Detail

A histogram records observation distribution through buckets or a supported native representation, together with relevant count and sum evidence. It can support estimates of duration quantiles or the fraction below a threshold. Resolution and aggregation depend on the actual representation and compatible populations.

A summary can include client-computed quantile estimates alongside count and sum. Those quantiles cannot generally be averaged into a fleet percentile. A mean computed from sum and count also differs from a slow-tail percentile. State which statistic answers the operational question before using it as an objective or alert threshold.

## Labels Define The Population

A metric name and label set identify a series. Labels can distinguish route, status, service or instance where useful. Every combination creates another series, so an unbounded request ID or user ID can impose large collection and storage costs. Individual-event detail often belongs in logs or traces instead.

Aggregation should combine compatible units and populations. Summing request rates across independent instances can describe a fleet rate. Averaging per-instance error percentages can misrepresent the fleet when traffic volumes differ. Measurement meaning remains essential even when the expression is valid.

## Collection Has Limits

A scrape observes exposed state at selected times. Brief gauge peaks can occur between observations, and process termination can lose final counter increments before collection. Missing series are not automatically zero. Metrics provide useful operational evidence within those limits rather than a complete ledger of every event. Define the question, population, unit and lifecycle so the result can be interpreted honestly.

## Common pitfalls

> [!WARNING]
> Counter resets and ordinary gauge decreases have different meanings. Distribution statistics are not interchangeable, and valid arithmetic cannot repair incompatible units or populations.
