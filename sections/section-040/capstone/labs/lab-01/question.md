---
draft: true
exam_objectives:
- Push vs Pull
---
# Pull Versus Push Capstone: Retire Stale Groups And Ship Batch Metrics

The `starfleet` namespace runs a Pushgateway that holds leftovers of retired batch jobs. The team needs the Pushgateway to hold only the current `nightly_report` result, needs Prometheus to keep the job name of every pushed group, and needs the samples copied to a second Prometheus server named `receiver`.

## Starting state

The Pushgateway holds two stale groups, `old_export` and `legacy_sync`. Each has a metric `lab_batch_last_success_timestamp_seconds` with an old timestamp. Prometheus scrapes the Pushgateway in the job `pushgateway` without `honor_labels`, and the `prometheus-config` ConfigMap has no `remote_write` section. The `receiver` server accepts remote write on `http://receiver:9090/api/v1/write`. No evidence report exists. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-047-lab-040-capstone-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-047-lab-040-capstone-01" || exit 1
```

Keep this connection selected for the whole task.

## Required result

- Delete the groups `old_export` and `legacy_sync` from the Pushgateway.
- Push a group with the job name `nightly_report` that holds `lab_batch_last_success_timestamp_seconds` with the current Unix time in seconds.
- Set `honor_labels: true` on the `pushgateway` scrape job.
- Add a `remote_write` section that sends samples to `http://receiver:9090/api/v1/write`.
- Make the `prometheus` Deployment load the new configuration.

Create a ConfigMap named `evidence` in `starfleet`. Its key `report.json` holds one JSON object with three fields. Each field is an object with the keys `expression`, `evaluated_at` and `data`, where `data` is the `data` object that `/api/v1/query` returned, unchanged, and `evaluated_at` is the Unix time you passed as the `time` parameter.

- `groups`: the number of pushed groups, from `count by (job)` over the batch timestamp metric, on `http://prometheus:9090`. The only result is the job `nightly_report`.
- `batch_age`: the age in seconds of the last successful batch, `time()` minus the timestamp metric for `nightly_report`, on `http://prometheus:9090`.
- `downstream`: the timestamp metric for `job="nightly_report"` queried on `http://receiver:9090`, which proves that the sample arrived through remote write.

Each expression must return exactly one series, and the evidence must be younger than five minutes when you submit.

## Verify The Result

Run `astrona submit` after the ConfigMap exists. Wait for the first samples to reach the `receiver` before you record the evidence.
