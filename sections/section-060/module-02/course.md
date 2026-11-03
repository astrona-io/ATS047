---
draft: true
exam_objectives:
- Basics of SLOs, SLAs, and SLIs
---
# Error Budgets And Burn Rate

This module teaches how a team turns a Service Level Objective (SLO) into a quantity it can spend and watch. You calculate an error budget, measure how fast a service uses it with the burn rate, and write Prometheus rules that alert on a fast burn.

## Learning Goals

- Calculate an error budget in events and in time from a target and a window.
- Measure how much of a budget a window has consumed.
- Calculate a burn rate and convert it into a time until the budget is exhausted.
- Explain why a burn rate alert checks a long and a short window.
- Write recording rules and an alerting rule for a burn rate in Prometheus.

## Before You Start

You need to know what an SLI, an SLO and a target are. The playground gives you a cluster with a small service that fails one request in ten, Prometheus and a traffic generator. The service promised 99 percent successful requests.

## Reading Order

1. Error budgets
2. Burn rate
3. Burn rate alerts
4. Guided practice in the playground
5. Summary

<!-- astrona:playground -->
