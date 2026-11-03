---
draft: true
exam_objectives:
- Metrics
---
# Identify Metric Types And Write Rate And Histogram Expressions Solution

The solution reads the types from the endpoint, evaluates two expressions at one moment and saves everything in the `evidence` ConfigMap. Select the lab cluster first.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-047-lab-010-01-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-047-lab-010-01-01" || exit 1
```

## Read The Declared Types

Fetch the metrics text from inside the cluster and keep the `# TYPE` lines.

```sh
kubectl -n starfleet exec shuttle -- python -c 'import urllib.request; print(urllib.request.urlopen("http://probe:8080/metrics", timeout=8).read().decode())' | grep '^# TYPE'
```

The fixture declares `lab_requests_total` as a counter, `lab_queue_depth` and `lab_last_success_timestamp_seconds` as gauges and `lab_request_duration_seconds` as a histogram. Copy exactly what your own output shows.

## Write The Two Expressions

The failure rate is the per-second rate of the counter series with status 500. Summing the result gives exactly one series.

```text
sum(rate(lab_requests_total{status="500"}[1m]))
```

The fast fraction divides the rate of the bucket with the bound 0.05 by the rate of the total count. Both sides use the same window.

```text
sum(rate(lab_request_duration_seconds_bucket{le="0.05"}[1m])) / sum(rate(lab_request_duration_seconds_count[1m]))
```

The expected failure rate is near 0.4 requests per second, and the expected fast fraction is close to 1. Run each expression through the Prometheus HTTP API from the `shuttle` pod and keep the returned `data` object.

## Save The Evidence

Save this as `record.py`. It repeats the steps above and writes the ConfigMap.

```python
import json, os, subprocess, tempfile, time, urllib.parse


def call(*args):
    result = subprocess.run(list(args), text=True, capture_output=True, timeout=20)
    assert result.returncode == 0, 'Observation command failed: ' + args[0]
    return result.stdout.strip()


def in_cluster(url):
    script = 'import urllib.request; print(urllib.request.urlopen(%r, timeout=8).read().decode())' % url
    return call('kubectl', '-n', 'starfleet', 'exec', 'shuttle', '--', 'python', '-c', script)


def query(expression, when):
    return json.loads(in_cluster('http://prometheus:9090/api/v1/query?' + urllib.parse.urlencode({'query': expression, 'time': when})))


types = {}
for line in in_cluster('http://probe:8080/metrics').splitlines():
    parts = line.split()
    if len(parts) == 4 and parts[1] == 'TYPE' and parts[2].startswith('lab_'):
        types[parts[2]] = parts[3]
now = time.time()
expressions = {
    'failure_rate': 'sum(rate(lab_requests_total{status="500"}[1m]))',
    'fast_fraction': 'sum(rate(lab_request_duration_seconds_bucket{le="0.05"}[1m])) / sum(rate(lab_request_duration_seconds_count[1m]))',
}
report = {'metric_types': types}
for key, expression in expressions.items():
    answer = query(expression, now)
    assert answer['status'] == 'success' and answer['data']['result'], 'Wait for enough scrapes'
    report[key] = {'expression': expression, 'evaluated_at': now, 'data': answer['data']}
resource = {'apiVersion': 'v1', 'kind': 'ConfigMap', 'metadata': {'name': 'evidence', 'namespace': 'starfleet'}, 'data': {'report.json': json.dumps(report, sort_keys=True)}}
with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as handle:
    json.dump(resource, handle)
    path = handle.name
call('kubectl', 'apply', '-f', path)
os.unlink(path)
```

Run it and check the ConfigMap:

```sh
python3 record.py
kubectl -n starfleet get configmap evidence -o jsonpath='{.data.report\.json}'
```

Then submit with `astrona submit`. After you finish, remove the lab with `astrona destroy ats-047-lab-010-01-01`.

## Common pitfalls

> [!WARNING]
> A `data` object copied by hand or an `evaluated_at` older than five minutes fails the check. An expression that applies `rate()` after a sum, or that uses `irate()`, is rejected. A fraction that drops the `le="0.05"` matcher does not measure the requested bound.
