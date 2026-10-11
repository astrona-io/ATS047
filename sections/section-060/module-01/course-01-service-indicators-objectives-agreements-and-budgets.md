---
draft: true
exam_objectives:
- Basics of SLOs, SLAs, and SLIs
---
# Service Indicators, Objectives, Agreements And Budgets

Reliability objectives connect observed service behavior to an explicit expectation. A Service Level Indicator measures an outcome, a Service Level Objective sets a target over a window, and a Service Level Agreement defines an agreement that can include consequences. These concepts share measurement inputs but have different responsibilities.

## Define An Indicator From User Outcomes

An availability indicator can be the proportion of valid requests that receive an acceptable outcome. A latency indicator can be the proportion completing within a defined threshold. The definitions must explain what counts as valid and good. Client mistakes, cancellations and internal retries require deliberate treatment rather than being excluded solely to improve a number.

Measurement location matters. A server-side success can differ from what a client observed if the response was lost or exceeded the client's deadline. Select evidence matching the intended user experience and document its limits. A metrics endpoint's scrape success is a collection indicator, not automatically the service's business availability.

## Set A Target And Window

An SLO might require a defined good fraction over a rolling thirty-day window. The target, period and population jointly determine the meaning. A one-hour graph can provide current evidence but does not by itself establish the entire objective period's result. Calendar and rolling windows also have different operational interpretations.

An SLA can use related indicators while specifying contractual responsibilities, exclusions and remedies. The operational SLO calculation does not automatically determine legal consequences. Keep the agreement's definition separate from a team's internal target even when both use similar percentages.

## Calculate The Allowed Budget

If an objective requires 99.9% good outcomes, the allowed unacceptable fraction is 0.1% under its defined model. For one million valid events, that corresponds conceptually to one thousand unacceptable events. Event-based budgets should not be casually converted into fixed downtime minutes unless the objective actually uses a time-based measurement.

Remaining budget depends on the observed population and window. It can inform release or reliability work decisions, but it is not a guarantee that future failures are acceptable to every user. Different routes or regions may have important behavior hidden inside one aggregate.

## Burn Rate Relates Current Failure To Allowance

If the observed unacceptable fraction is 1% against a 0.1% allowance, the conceptual burn rate is ten. Sustaining that behavior consumes the allowance much faster than the objective's steady budget. The selected observation window determines how responsive or noisy the estimate is.

Short and long windows can support different response decisions. A brief burst may justify investigation while a sustained high burn can require urgent action. Define the intended response and evidence before copying alert thresholds from another service with a different objective or period.

## Preserve Evidence Limits

Low traffic can make ratios volatile, while missing collection can omit both numerator and denominator. A silent indicator can therefore mean no activity or unavailable evidence. Explicit coverage checks and suitable measurement volume can improve interpretation without pretending every absence is zero.

Document exclusions, aggregation and ownership. A useful objective aligns the measured population with the service promise and gives teams a basis for action. The percentage is meaningful only when its event definitions, window and collection evidence remain coherent.

## Common pitfalls

> [!WARNING]
> Scrape success is not automatically user availability. Event-based and time-based budgets differ, and contractual consequences cannot be inferred solely from an internal SLO percentage.
