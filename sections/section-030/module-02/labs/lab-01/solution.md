---
draft: true
exam_objectives:
- Tracing and Spans
---
# Find A Slow Trace With An Exemplar Solution

Select the lab cluster first.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-047-lab-030-02-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-047-lab-030-02-01" || exit 1
```

## Measure The Sampling Ratio

`lab_traces_started_total` counts every trace a service starts, split by the label `sampled`. The ratio of the sampled rate to the total rate is the share of traces that were kept.

```text
sum(rate(lab_traces_started_total{sampled="true"}[1m])) / sum(rate(lab_traces_started_total[1m]))
```

The services sample one trace in four, so the value is near 0.25.

## Query The Exemplars

An exemplar is a sample of one real request that Prometheus stores next to a histogram bucket. It carries a `trace_id` label. Ask Prometheus for the exemplars of the `probe` bucket series with the `query_exemplars` endpoint, with a `start` and an `end` in Unix seconds.

```sh
kubectl -n starfleet exec shuttle -- python -c 'import time, urllib.parse, urllib.request; now = time.time(); q = urllib.parse.urlencode({"query": "lab_request_duration_seconds_bucket{service=\"probe\"}", "start": now - 300, "end": now}); print(urllib.request.urlopen("http://prometheus:9090/api/v1/query_exemplars?" + q, timeout=8).read().decode())'
```

The response lists series and, for each series, its exemplars with `labels`, `value` and `timestamp`. The exemplar with the highest `value` is the slowest sampled request. Its `trace_id` is the key to the logs.

## Count The Spans

Select the span lines with that trace id from the logs of both services.

```sh
kubectl -n starfleet logs deployment/probe --tail=5000 | grep '"event": "span"'
```

Count the lines that carry the trace id in both logs.

## Save The Evidence

Save this as `record.py`. It evaluates the ratio, picks the slowest exemplar and counts its spans.

```python
import json, os, subprocess, tempfile, time, urllib.parse


def call(*args):
    result = subprocess.run(list(args), text=True, capture_output=True, timeout=30)
    assert result.returncode == 0, 'Observation command failed: ' + args[0]
    return result.stdout.strip()


def in_cluster(url, headers=None):
    script = 'import urllib.request; print(urllib.request.urlopen(urllib.request.Request(%r, headers=%r), timeout=8).read().decode())' % (url, headers or {})
    return call('kubectl', '-n', 'starfleet', 'exec', 'shuttle', '--', 'python', '-c', script)


def spans_for(trace_id):
    found = []
    for deployment in ('probe', 'scout'):
        for line in call('kubectl', '-n', 'starfleet', 'logs', 'deployment/' + deployment, '--tail=5000').splitlines():
            try:
                record = json.loads(line)
            except ValueError:
                continue
            if record.get('event') == 'span' and record.get('trace_id') == trace_id:
                found.append(record)
    return sorted(found, key=lambda record: record['service'])


def prometheus(path, **params):
    return json.loads(in_cluster('http://prometheus:9090' + path + '?' + urllib.parse.urlencode(params)))


def slowest_exemplar(expression, now):
    answer = prometheus('/api/v1/query_exemplars', query=expression, start=now - 300, end=now)
    candidates = [(float(item['value']), item['labels']['trace_id']) for series in answer['data'] for item in series['exemplars']]
    assert candidates, 'Wait for exemplars to be scraped'
    value, trace_id = max(candidates)
    return value, trace_id


def save(report):
    resource = {'apiVersion': 'v1', 'kind': 'ConfigMap', 'metadata': {'name': 'evidence', 'namespace': 'starfleet'}, 'data': {'report.json': json.dumps(report, sort_keys=True)}}
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as handle:
        json.dump(resource, handle)
        path = handle.name
    call('kubectl', 'apply', '-f', path)
    os.unlink(path)


def ratio(expression, now):
    answer = prometheus('/api/v1/query', query=expression, time=now)
    assert answer['status'] == 'success' and answer['data']['result'], 'Wait for enough scrapes'
    return {'expression': expression, 'evaluated_at': now, 'data': answer['data']}


assert call('kubectl', 'config', 'current-context') == 'kind-astro-ats-047-lab-030-02-01'
now = time.time()
report = {'sampling_ratio': ratio('sum(rate(lab_traces_started_total{sampled="true"}[1m])) / sum(rate(lab_traces_started_total[1m]))', now)}
expression = 'lab_request_duration_seconds_bucket{service="probe"}'
value, trace_id = slowest_exemplar(expression, now)
report['exemplar'] = {'expression': expression, 'evaluated_at': now, 'trace_id': trace_id, 'value': value}
report['span_count'] = len(spans_for(trace_id))
save(report)
```

Run it and check the result:

```sh
python3 record.py
kubectl -n starfleet get configmap evidence -o jsonpath='{.data.report\.json}'
```

Then submit with `astrona submit`. After you finish, remove the lab with `astrona destroy ats-047-lab-030-02-01`.

## Common pitfalls

> [!WARNING]
> The exemplar belongs to a bucket series, so query `lab_request_duration_seconds_bucket`, not the `_sum` or `_count` series. The `query_exemplars` endpoint needs a `start` and an `end` time. A sampling ratio built from `lab_requests_total` counts every request, not every started trace, so it does not measure sampling.
