---
draft: true
exam_objectives:
- Tracing and Spans
---
# Follow One Trace Across Two Services Solution

Select the lab cluster first.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-047-lab-030-01-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-047-lab-030-01-01" || exit 1
```

## Send The Traced Request

The `traceparent` header carries the trace id, the id of the caller span and a flags field. The last flag value `01` marks the trace as sampled, so both services write span lines. Send the request from the `shuttle` pod. The reference script in this page sends it for you, and you can also send it by hand with the `kubectl exec` form used by the helper `in_cluster` below.

```sh
kubectl -n starfleet exec shuttle -- python -c 'import urllib.request; r = urllib.request.Request("http://probe:8080/work?child_delay=0.2", headers={"traceparent": "00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01"}); print(urllib.request.urlopen(r, timeout=8).read().decode())'
```

The response is one JSON object with the fields of the `probe` span and a `child` object with the fields of the `scout` span.

## Read The Spans

Both services log the span as one JSON line. Select the lines of this trace.

```sh
kubectl -n starfleet logs deployment/probe --tail=5000 | grep 0af7651916cd43dd8448eb211c80319c
kubectl -n starfleet logs deployment/scout --tail=5000 | grep 0af7651916cd43dd8448eb211c80319c
```

Each service prints a `request_completed` line and a `span` line for the trace. The `probe` span has the parent id `b7ad6b7169203331` from the header. The `scout` span has the span id of the `probe` span as its parent id. The `probe` span includes the time spent waiting for `scout`, so its own work is its duration minus the duration of the `scout` span.

## Show The Lost Context

A request with `propagate=false` makes `probe` call `scout` without a `traceparent` header. The `scout` service then starts a new trace with a new trace id.

```sh
kubectl -n starfleet exec shuttle -- python -c 'import urllib.request; print(urllib.request.urlopen("http://probe:8080/work?propagate=false", timeout=8).read().decode())'
```

Compare `trace_id` in the response with `trace_id` inside `child`. They differ.

## Save The Evidence

Save this as `record.py`. It sends both requests, collects the span lines and writes the ConfigMap.

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


assert call('kubectl', 'config', 'current-context') == 'kind-astro-ats-047-lab-030-01-01'
TRACE = '0af7651916cd43dd8448eb211c80319c'
header = {'traceparent': '00-' + TRACE + '-b7ad6b7169203331-01'}
json.loads(in_cluster('http://probe:8080/work?child_delay=0.2', header))
orphan = json.loads(in_cluster('http://probe:8080/work?propagate=false'))
time.sleep(2)
spans = spans_for(TRACE)
assert len(spans) == 2, 'Expected one span in each service for the trace'
probe, scout = spans
report = {
    'trace_id': TRACE,
    'spans': spans,
    'probe_self_time_seconds': round(probe['duration_seconds'] - scout['duration_seconds'], 6),
    'orphan': {'probe_trace_id': orphan['trace_id'], 'scout_trace_id': orphan['child']['trace_id']},
}
save(report)
```

Run it and check the result:

```sh
python3 record.py
kubectl -n starfleet get configmap evidence -o jsonpath='{.data.report\.json}'
```

Then submit with `astrona submit`. After you finish, remove the lab with `astrona destroy ats-047-lab-030-01-01`.

## Common pitfalls

> [!WARNING]
> A `probe` span has a parent id that comes from the incoming header, and a `scout` span has the `probe` span id as its parent id. A `scout` trace id that differs from the `probe` trace id means the context was lost between the two services. If the span lines are missing, send the first request again, because the logs keep only the most recent lines.
