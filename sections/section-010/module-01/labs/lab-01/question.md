---
draft: true
exam_objectives:
- Metrics
---
# Distinguish A Counter From A Gauge

Evaluate the required expression and preserve its labels, values and evaluation time.

## Starting state

One instrumented probe serves metrics and structured request logs. A traffic generator makes ten percent of requests fail. Prometheus scrapes every two seconds; no evidence report or learner rule exists.

Use a host shell with the private kubeconfig for this independent kind environment. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-047-lab-010-01-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-047-lab-010-01-01" || exit 1
node_name="astro-ats-047-lab-010-01-01-control-plane"
worker_name="astro-ats-047-lab-010-01-01-worker"
```

Keep this connection selected. Host-level commands name only this environment's node containers. They do not operate on the host operating system.

## Required result

Inspect the exposition TYPE declarations and compare the current queue gauge with the accumulating request counter. The queue is a current value; counters measure completed events. The fixture exposes a classic histogram, not a native histogram or client summary.

Use the expression `lab_queue_depth`. The report needs `expression`, `evaluated_at` and `data`. Data is the Prometheus API data object, not only the printed value. Wait for at least twenty seconds of collected traffic before using a rate. Record evidence within five minutes of submission. Changing the expression or claiming an empty result fails.

Record observations in `starfleet/evidence`, whose `report.json` contains the stated report. The verifier reads the live API again; invented values do not pass.

The report object uses these fields: `expression`, `evaluated_at`, `data`. Keep numeric values numeric and preserve arrays and nested objects returned by the API.

## Verify The Result

The grader checks the required object fields and actual observations. Wait for controller convergence before submitting. Preserve the task's namespace, workload names and unrelated components.
