---
draft: true
exam_objectives:
- Basics of SLOs, SLAs, and SLIs
---
# Basics of SLOs, SLAs, and SLIs

This section covers how teams measure and promise service reliability. It has two modules. The first defines the Service Level Indicator (SLI), the Service Level Objective (SLO) and the Service Level Agreement (SLA), and builds them from Prometheus metrics. The second turns an objective into an error budget, measures how fast a service uses it with the burn rate, and writes Prometheus rules that alert on a fast burn.

Each module has a playground for guided practice and a graded lab. A capstone lab at the end of the section asks you to build recording rules and a burn rate alert without step-by-step guidance. A short quiz closes the section.

## Learning Outcomes

- Distinguish an SLI, an SLO and an SLA.
- Define good and valid events, a target and an evaluation window.
- Build an availability SLI and a latency SLI with PromQL.
- Calculate an error budget and the share of it that a window consumed.
- Calculate a burn rate and the time until the budget is exhausted.
- Write recording rules and a multi-window burn rate alert in Prometheus.
- Account for low traffic, exclusions and missing data.

## Modules

1. Service Level Indicators, Objectives And Agreements: SLI, SLO, SLA, windows, targets and dependencies.
2. Error Budgets And Burn Rate: budgets, burn rate, alert windows and Prometheus rules.
3. Capstone lab: Alert On Error Budget Burn Rate.
4. Knowledge check: `quiz.yaml`.
