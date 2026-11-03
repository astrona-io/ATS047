---
draft: true
exam_objectives:
- Push vs Pull
---
# Remote Write And Downstream Delivery

A single Prometheus server stores its data locally for a limited time. Teams often need the same samples in another system, for long-term storage, for a view across many clusters or for a second copy. Remote write is the Prometheus feature that sends samples to another endpoint. This part explains what it sends, which component does the work and how it fails, so that you do not confuse it with instrumentation or with the Pushgateway.

## Remote Write Starts After Collection

Remote write is not a way to get data out of an application. The application exposes metrics, and Prometheus scrapes them and stores them. Remote write then sends a copy of the samples that Prometheus has already collected to a configured URL (Uniform Resource Locator) over HTTP (Hypertext Transfer Protocol). It does not discover targets, it does not instrument code and it does not change the local storage. The local server keeps working if the remote endpoint fails.

Two Prometheus servers run in the playground. The server `prometheus` scrapes the `probe`, the Pushgateway and itself. The server `receiver` has no scrape jobs of its own. It runs with the flag `--web.enable-remote-write-receiver`, which makes it accept samples on the path `/api/v1/write`. The `receiver` stands for any remote system that speaks the remote write protocol.

```mermaid
flowchart LR
  A["probe"] -->|"scrape"| P["prometheus"]
  P -->|"remote write"| R["receiver"]
```

The diagram shows that the first server collects by pull and the second receives by push. The producer is the first Prometheus server, not the application.

## The Path From Scrape To Remote Endpoint

When Prometheus ingests a scrape, it writes the samples to the write-ahead log (WAL), a file on disk that records every sample before it is compacted into blocks. A remote write queue reads the samples from the WAL, not from the scrape directly. Because of this design, a short outage of the remote endpoint does not lose data: the queue waits and the WAL keeps the samples.

The queue splits the work over shards. A shard is a parallel sender with its own in-memory buffer. Each shard collects samples into a batch and sends one request with many samples. Prometheus changes the number of shards on its own, based on the rate of new samples and the time that a send takes. When the endpoint answers with an error that can be retried, Prometheus retries the batch with a growing wait between attempts. When the buffer of a shard is full, Prometheus stops reading the WAL for all shards until space is free.

## Turn On Remote Write

Select the playground cluster and define the query helper. Check that the `receiver` starts empty.

<!-- astrona:playground:renew -->

```sh
export KUBECONFIG="$(astrona kubeconfig ats-047-playground-040-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-047-playground-040-02" || exit 1
query() {
  kubectl -n starfleet exec shuttle -- python -c 'import sys,urllib.parse,urllib.request; print(urllib.request.urlopen(sys.argv[1]+"/api/v1/query?"+urllib.parse.urlencode({"query":sys.argv[2]}),timeout=8).read().decode())' "$1" "$2"
}
query http://receiver:9090 'up'
```

The result has no series, because nothing has written to the `receiver` yet. Now add a `remote_write` list to the configuration of the first server. The setting `url` names the endpoint. Edit the ConfigMap, add the lines below at the end of the file `prometheus.yaml` and save.

```yaml
remote_write:
- url: http://receiver:9090/api/v1/write
```

```sh
kubectl -n starfleet edit configmap prometheus-config
kubectl -n starfleet rollout restart deployment/prometheus
kubectl -n starfleet rollout status deployment/prometheus --timeout=180s
```

Prometheus reads its configuration file at start or when it receives a reload request. The restart makes the server read the new file. After about twenty seconds, query the `receiver` again.

```sh
query http://receiver:9090 'up{job="probe"}'
```

The `receiver` now returns the series `up` for the job `probe`, with the labels `job`, `instance` and `team` that the first server attached when it scraped. The labels travel with the samples. The `receiver` did not scrape anything, so it knows nothing about the `probe`.

## Watch The Queue With Metrics

The first server describes its own remote write queue in metrics with the prefix `prometheus_remote_storage_`. The metric `prometheus_remote_storage_samples_pending` holds the number of samples that wait in the queues. It stays near zero when the sender keeps up and grows when the endpoint is slow. The counters `prometheus_remote_storage_samples_total` and `prometheus_remote_storage_samples_failed_total` count the samples sent and the samples that failed.

```sh
query http://prometheus:9090 'sum(prometheus_remote_storage_samples_total)'
query http://prometheus:9090 'sum(prometheus_remote_storage_samples_pending)'
```

The first result is a counter and rises while the server sends samples. The second stays low in the playground, which has a small number of series. A growing pending value is an early sign that the endpoint cannot keep up.

## Authentication And Selection

A remote endpoint outside the cluster needs protection. A `remote_write` entry accepts settings such as `basic_auth`, `authorization` and `tls_config`, which add credentials and certificate checks to every request. The playground uses a plain HTTP path inside the cluster, so it needs none. You can list several `remote_write` entries, and each one gets its own queue, so a slow endpoint does not delay the others.

## Limits And Costs

Remote write adds memory, CPU and network use to the sending server. The memory use of the shards grows with the number of shards and with the size of each buffer. If the endpoint is down for a long time, the WAL is compacted, and samples that were never sent are lost. The documentation names two hours as the typical limit. Remote write is also not a backup: it copies samples forward, and the receiving system decides how long to keep them.

You can reduce the volume with `write_relabel_configs`, a list of relabeling rules that drop or change series before they are sent. Prometheus can also run in agent mode, a mode that scrapes and forwards samples without a local query engine, for use with a remote write destination only.

You now know that remote write forwards what is already collected, and that its failures are separate from the failures of the scrape. The next question is how a series ends in Prometheus, and what a query returns when a producer stops.

## Common pitfalls

> [!WARNING]
> Remote write does not collect anything and does not create series that the server did not scrape. A healthy remote endpoint does not prove that local collection works, and a failing endpoint does not stop local queries. Editing the ConfigMap does not change the running server until it restarts or reloads.
