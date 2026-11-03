---
draft: true
exam_objectives:
- Metrics
---
# Metrics Capstone: Review The Shop Metrics Solution

Select the lab cluster first.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-047-lab-010-capstone-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-047-lab-010-capstone-01" || exit 1
```

## Read Types, Names And Labels

Fetch the metrics text of one instance.

```sh
kubectl -n starfleet exec shuttle -- python -c 'import urllib.request; print(urllib.request.urlopen("http://shop-a:8080/metrics", timeout=8).read().decode())'
```

The `# TYPE` lines declare `shop_http_requests_total` and `shop_user_requests_total` as counters, `shop_request_duration_seconds` as a histogram and `shop_latency_ms` as a gauge. Copy the declarations exactly as your own output shows them.

The name `shop_latency_ms` uses milliseconds, while the convention is to use the base unit seconds, so the metric would be named `shop_latency_seconds`. The metric `shop_user_requests_total` has the label `user_id` with one value per user. That label is unbounded, and each new user creates a new series.

## Write The Expressions

The fleet p95 sums the bucket rates across both instances and keeps the `le` label for `histogram_quantile()`:

```text
histogram_quantile(0.95, sum by (le) (rate(shop_request_duration_seconds_bucket[1m])))
```

The error ratio for each instance divides two sums that are both grouped by `instance`. Prometheus matches the two sides on the `instance` label:

```text
sum by (instance) (rate(shop_http_requests_total{status="500"}[1m])) / sum by (instance) (rate(shop_http_requests_total[1m]))
```

The expected ratio is near 0.1 for `shop-a` and near 0.5 for `shop-b`.

## Save The Evidence

Save this as `record.py`. It reads the types, evaluates both expressions at one moment and writes the ConfigMap.

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
for line in in_cluster('http://shop-a:8080/metrics').splitlines():
    parts = line.split()
    if len(parts) == 4 and parts[1] == 'TYPE' and parts[2].startswith('shop_'):
        types[parts[2]] = parts[3]
now = time.time()
expressions = {
    'p95_latency': 'histogram_quantile(0.95, sum by (le) (rate(shop_request_duration_seconds_bucket[1m])))',
    'error_ratio_by_instance': 'sum by (instance) (rate(shop_http_requests_total{status="500"}[1m])) / sum by (instance) (rate(shop_http_requests_total[1m]))',
}
report = {'metric_types': types, 'unbounded_label': 'user_id', 'naming_issue': 'shop_latency_ms'}
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

Run it and check the result:

```sh
python3 record.py
kubectl -n starfleet get configmap evidence -o jsonpath='{.data.report\.json}'
```

Then submit with `astrona submit`. After you finish, remove the lab with `astrona destroy ats-047-lab-010-capstone-01`.

## Common pitfalls

> [!WARNING]
> A quantile estimated from per-instance buckets without `sum by (le)` is not a fleet value. A ratio whose two sides use different groupings does not match series. A `metric_types` object that is typed by hand and differs from the endpoint fails the check.
