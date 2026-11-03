---
draft: true
exam_objectives:
- Push vs Pull
---
# Push A Batch Result And Keep Its Job Label

A nightly report job in the `starfleet` namespace finishes before Prometheus can scrape it, so it must deliver its result to a Pushgateway. The Pushgateway is a small server that stores pushed metrics and exposes them on `/metrics` so that Prometheus can scrape them. The team needs the result of the job to show up in Prometheus with the job name `nightly_report`.

## Starting state

The `pushgateway` Deployment and Service listen on port 9091 in `starfleet`. Prometheus already scrapes the Pushgateway in a scrape job named `pushgateway`, but that job does not set `honor_labels`. The scrape configuration lives in the ConfigMap `prometheus-config` in the key `prometheus.yaml`. The `shuttle` pod can reach the `pushgateway` and `prometheus` Services. No evidence report exists. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-047-lab-040-01-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-047-lab-040-01-01" || exit 1
```

Keep this connection selected for the whole task.

## Required result

Push one group to the Pushgateway with the job name `nightly_report`. The group holds two metrics: `lab_batch_records_processed` with the value `42`, and `lab_batch_last_success_timestamp_seconds` with the current Unix time in seconds.

Change the `pushgateway` scrape job so the labels of the pushed metrics are kept, and make the Prometheus server use the new configuration. Prometheus must then return the pushed metrics with the label `job="nightly_report"`.

Create a ConfigMap named `evidence` in `starfleet`. Its key `report.json` holds one JSON object with three fields. Each field is an object with the keys `expression`, `evaluated_at` and `data`. The key `expression` holds the PromQL (Prometheus Query Language) text you ran. The key `evaluated_at` holds the Unix time you passed as the `time` parameter. The key `data` holds the `data` object that `/api/v1/query` returned, unchanged.

- `batch_records`: the number of records pushed by the group `nightly_report`.
- `batch_age`: the age in seconds of the last successful batch, calculated as `time()` minus the pushed timestamp metric for the group `nightly_report`.
- `gateway_up`: the `up` series for the scrape job `pushgateway`.

Each expression must return exactly one series, and the evidence must be younger than five minutes when you submit. The grader reads the Pushgateway and the live configuration, and runs your expressions again.

## Verify The Result

Run `astrona submit` after the ConfigMap exists. Wait for several scrapes after the Prometheus Deployment restarts, so the pushed metrics are present before you record the evidence.
