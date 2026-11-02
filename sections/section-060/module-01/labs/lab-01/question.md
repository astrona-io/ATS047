---
draft: true
exam_objectives:
- Basics of SLOs, SLAs, and SLIs
---
# Calculate A Traffic Weighted Error Ratio

Evaluate the required expression and preserve its labels, values and evaluation time.

## Starting state

One instrumented probe serves metrics and structured request logs. A traffic generator makes ten percent of requests fail. Prometheus scrapes every two seconds; no evidence report or learner rule exists.

Use a host shell with the private kubeconfig for this independent kind environment. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-047-lab-060-01-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-047-lab-060-01-01" || exit 1
node_name="astro-ats-047-lab-060-01-01-control-plane"
worker_name="astro-ats-047-lab-060-01-01-worker"
```

Keep this connection selected. Host-level commands name only this environment's node containers. They do not operate on the host operating system.

## Required result

Compute failures divided by all requests. Compare that SLI with a 99 percent success objective, then calculate its error budget. An SLA is a separate agreement; no contractual decision is graded.

Use the expression `sum(rate(lab_requests_total{status="500"}[20s])) / sum(rate(lab_requests_total[20s]))`. The report needs `expression`, `evaluated_at` and `data`. Data is the Prometheus API data object, not only the printed value. Wait for at least twenty seconds of collected traffic before using a rate. Record evidence within five minutes of submission. Changing the expression or claiming an empty result fails.

Record observations in `starfleet/evidence`, whose `report.json` contains the stated report. The verifier reads the live API again; invented values do not pass.

The report object uses these fields: `expression`, `evaluated_at`, `data`. Keep numeric values numeric and preserve arrays and nested objects returned by the API.

## Verify The Result

The grader checks the required object fields and actual observations. Wait for controller convergence before submitting. Preserve the task's namespace, workload names and unrelated components.
