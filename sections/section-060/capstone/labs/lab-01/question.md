---
draft: true
exam_objectives:
- Basics of SLOs, SLAs, and SLIs
---
# Alert On Error Budget Burn Rate

Solve this task in the private kind environment of this lab. It combines everything about service level indicators, objectives and error budgets in one exercise, and it gives no step-by-step guidance.

## Starting state

The `probe` Service in the `starfleet` namespace serves requests and exposes the counter `lab_requests_total` with the label `status`. A traffic generator sends a steady stream of requests, and one request in ten returns status 500. Prometheus scrapes the probe every two seconds and evaluates rules every two seconds. The ConfigMap `prometheus-rules` in `starfleet` holds the key `rules.yaml`, and it contains no rules yet.

The team promised a service level objective (SLO) of 99 percent successful requests. The error budget is therefore 1 percent of requests. Nobody gets a notification when the probe uses that budget too fast.

## Required result

Change the rules so that Prometheus evaluates a rule group with exactly these three rules:

1. A recording rule named `sli:request_error_ratio:rate20s`. It records the share of requests with status 500 among all requests, calculated with `rate` over a 20 second range and summed over all series.
2. A recording rule named `slo:error_budget_burn_rate:rate20s`. It records the burn rate: the first recording rule divided by the error budget of the 99 percent objective. It must use the first recording rule by name.
3. An alerting rule named `ErrorBudgetFastBurn`. It fires when the burn rate rule is above 5 for 10 seconds. It has the label `severity` with the value `page` and an annotation named `summary` that explains the problem in one sentence. It must use the burn rate rule by name.

Prometheus must load the new rules, evaluate them without error and show `ErrorBudgetFastBurn` as firing, because the probe currently burns its budget about ten times faster than allowed.

## Constraints

- Keep the Prometheus configuration, the `probe` Deployment and the traffic generator as they are.
- Do not hard-code a ratio or a burn rate value. Every value comes from a query.
- Use a bounded wait: Prometheus needs a few evaluation cycles after it loads the rules.

## Verify the result

The grader asks the Prometheus rules, query and alerts endpoints. It checks the rule names, types, health, the dependency between the rules, the label, the annotation, the `for` duration, the recorded values and the firing alert.
