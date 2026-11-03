---
draft: true
exam_objectives:
- Push vs Pull
---
# Configure Remote Write And Observe A Stale Series

The platform team wants the samples of the Prometheus server in `starfleet` copied to a second Prometheus server named `receiver`, and wants proof of how a deleted pushed series behaves in queries. Remote write is the Prometheus feature that sends collected samples to another endpoint over HTTP (Hypertext Transfer Protocol).

## Starting state

The `receiver` Deployment and Service in `starfleet` run Prometheus with the flag `--web.enable-remote-write-receiver`, so it accepts samples on `/api/v1/write` at port 9090. The Prometheus server `prometheus` has no `remote_write` section. It already scrapes a Pushgateway with `honor_labels: true`. The scrape configuration lives in the key `prometheus.yaml` of the ConfigMap `prometheus-config`. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-047-lab-040-02-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-047-lab-040-02-01" || exit 1
```

Keep this connection selected for the whole task.

## Required result

Add a `remote_write` section to `prometheus-config` that sends samples to `http://receiver:9090/api/v1/write`, and make the `prometheus` Deployment load it.

Push one group with the job name `temp_export` to the Pushgateway. The group holds one metric, `lab_temp_value`, with the value `1`. Wait until Prometheus returns it, then delete the group from the Pushgateway with a DELETE request. Wait at least ten seconds after the delete before you record the evidence.

Create a ConfigMap named `evidence` in `starfleet`. Its key `report.json` holds one JSON object with four fields. Each field is an object with the keys `expression`, `evaluated_at` and `data`, where `data` is the `data` object that `/api/v1/query` returned, unchanged, and `evaluated_at` is the Unix time you passed as the `time` parameter.

- `receiver_probe`: the `up` series of the job `probe`, queried on the `receiver` server at `http://receiver:9090`.
- `samples_sent`: the total number of samples the `prometheus` server sent, from `prometheus_remote_storage_samples_total` summed over all its series, queried on `http://prometheus:9090`.
- `instant_after_delete`: a plain selector for `lab_temp_value` with the label `job="temp_export"`, queried on `prometheus` after the delete. The result must be empty.
- `history_kept`: the number of samples of `lab_temp_value` with `job="temp_export"` stored in the last ten minutes, from `count_over_time` with a `[10m]` range. The result is one series.

The evidence must be younger than five minutes when you submit. The grader re-runs every expression at the recorded time.

## Verify The Result

Run `astrona submit` after the ConfigMap exists. Remote write needs a few seconds after the restart before the first samples reach the `receiver`.
