---
draft: true
exam_objectives:
- Metrics
---
# Find The Costly Label And Calculate Fleet Rates Solution

The solution finds the metric with the most series, sums rates across both instances and divides the fleet failure rate by the fleet request rate. Select the lab cluster first.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-047-lab-010-02-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-047-lab-010-02-01" || exit 1
```

## Look At The Labels

Fetch the metrics text of one instance and read the label names on each sample line.

```sh
kubectl -n starfleet exec shuttle -- python -c 'import urllib.request; print(urllib.request.urlopen("http://shop-a:8080/metrics", timeout=8).read().decode())'
```

The metric `shop_http_requests_total` has the labels `route` and `status`. The metric `shop_user_requests_total` has the label `user_id`, and it has one line for every user that sent a request. That label is the unbounded one.

## Write The Expressions

The cardinality expression counts series for each metric name. Grouping by the internal label `__name__` returns one result per metric name:

```text
count by (__name__) ({job="shop"})
```

The route rate applies `rate()` to every series first and then sums by route, which removes the `status` and `instance` labels:

```text
sum by (route) (rate(shop_http_requests_total[1m]))
```

The fleet error ratio divides two sums, so that the instance with more traffic counts for more. An average of the two per-instance ratios would be wrong, because the instances do not carry the same traffic:

```text
sum(rate(shop_http_requests_total{status="500"}[1m])) / sum(rate(shop_http_requests_total[1m]))
```

The expected fleet ratio is about 0.18, while the plain average of the two instance ratios would be about 0.30.

## Save The Evidence

Save this as `record.py`. It evaluates the three expressions at one moment and writes the ConfigMap.

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


now = time.time()
expressions = {
    'cardinality': 'count by (__name__) ({job="shop"})',
    'fleet_route_rate': 'sum by (route) (rate(shop_http_requests_total[1m]))',
    'fleet_error_ratio': 'sum(rate(shop_http_requests_total{status="500"}[1m])) / sum(rate(shop_http_requests_total[1m]))',
}
report = {'unbounded_label': 'user_id'}
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

Then submit with `astrona submit`. After you finish, remove the lab with `astrona destroy ats-047-lab-010-02-01`.

## Common pitfalls

> [!WARNING]
> Averaging the two instance ratios gives a wrong fleet ratio. A `sum by (route)` placed inside `rate()` is invalid, so apply `rate()` first. An expression that keeps the `instance` or `status` label does not meet the `route`-only requirement. An `evaluated_at` older than five minutes fails the check.
