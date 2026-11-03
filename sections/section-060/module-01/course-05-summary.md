---
draft: true
exam_objectives:
- Basics of SLOs, SLAs, and SLIs
---
# Summary

A Service Level Indicator (SLI) is a measured ratio of good events to valid events. Its definition states what an event is, which events are valid and which are good, and it also states where the measurement is taken. An availability SLI comes from a request counter, and a latency SLI comes from the cumulative buckets of a histogram.

A Service Level Objective (SLO) adds a target and a window to an SLI. The target decides how much failure is allowed, and each extra nine divides the allowance by ten. A rolling window forgets old failures gradually, and a calendar window forgets them on a fixed date. A Prometheus query that divides the increase of good events by the increase of valid events checks the objective.

A Service Level Agreement (SLA) is a contract with consequences such as service credits. Providers set the internal SLO stricter than the SLA, so that a missed SLO warns the team before a credit is owed. A contract can measure and exclude events differently from the team's query, and required dependencies limit what a service can promise.

Key facts:

- SLI = good events divided by valid events.
- SLO = SLI, target and window.
- SLA = agreement with consequences, usually looser than the SLO.
- Availabilities of required independent dependencies multiply.

<!-- astrona:playground:destroy -->
