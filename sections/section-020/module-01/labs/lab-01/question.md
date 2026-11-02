---
draft: true
exam_objectives:
- Understand logs and events
---
# Correlate A Request Log With Its Response

Produce one real request and correlate its response with the structured completion record.

## Starting state

One instrumented probe serves metrics and structured request logs. A traffic generator makes ten percent of requests fail. Prometheus scrapes every two seconds; no evidence report or learner rule exists.

Use a host shell with the private kubeconfig for this independent kind environment. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-047-lab-020-01-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-047-lab-020-01-01" || exit 1
node_name="astro-ats-047-lab-020-01-01-control-plane"
worker_name="astro-ats-047-lab-020-01-01-worker"
```

Keep this connection selected. Host-level commands name only this environment's node containers. They do not operate on the host operating system.

## Required result

Record `response` and `event` objects. Use request_id to correlate a single response and log, rather than placing unbounded identifiers in metrics. For trace practice send the provided W3C traceparent header. This lightweight fixture demonstrates context propagation and a timed operation; it does not run a tracing backend or claim a distributed trace.

Record observations in `starfleet/evidence`, whose `report.json` contains the stated report. The verifier reads the live API again; invented values do not pass.

The report object uses these fields: `response`, `event`. Keep numeric values numeric and preserve arrays and nested objects returned by the API.

## Verify The Result

The grader checks the required object fields and actual observations. Wait for controller convergence before submitting. Preserve the task's namespace, workload names and unrelated components.
