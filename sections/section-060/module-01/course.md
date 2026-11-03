---
draft: true
exam_objectives:
- Basics of SLOs, SLAs, and SLIs
---
# Service Level Indicators, Objectives And Agreements

This module teaches the three terms that describe service reliability: the Service Level Indicator (SLI), the Service Level Objective (SLO) and the Service Level Agreement (SLA). You build an SLI from Prometheus counters and histograms, judge it against a target over a window, and learn how a contract differs from an internal target.

## Learning Goals

- Define an SLI as a ratio of good events to valid events and state which events are valid and which are good.
- Build an availability SLI and a latency SLI with PromQL.
- Combine an SLI, a target and a window into an SLO, and check it with a query.
- Explain why an SLA differs from an SLO and why the SLO is set stricter.
- Explain how required dependencies limit a promise.

## Before You Start

You need to know what a request and a response are, and you should be able to read a short Prometheus query. The playground gives you a cluster with a small service, Prometheus and a traffic generator. No other setup is needed.

## Reading Order

1. Service Level Indicators
2. Service Level Objectives
3. Service Level Agreements
4. Guided practice in the playground
5. Summary

<!-- astrona:playground -->
