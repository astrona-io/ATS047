---
draft: true
exam_objectives:
- Understand logs and events
---
# Measure Log Sampling And Find The Sensitive Field Solution

The solution compares what the log holds with what the metrics count. The shop logs every failed request and only one successful request in five, so the log gives a different failure share than the metric. Select the lab cluster first.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-047-lab-020-02-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-047-lab-020-02-01" || exit 1
```

## Read The Log

Read the last lines of the shop log. Each request record is one JSON line.

```sh
kubectl -n starfleet logs deployment/shop --tail=20
```

Look at the field `sample_every` in a record with level `info` and in a record with level `error`. The `info` records have `sample_every` 5, which means that the shop wrote one record for every five successful requests. The `error` records have `sample_every` 1, which means that every failed request has a record. One field holds personal data: the `email` field holds an address built from the user identifier.

## Calculate The Share From The Log

Count the request records in the last 200 lines and the records with level `error`. A short way to count with `grep`:

```sh
kubectl -n starfleet logs deployment/shop --tail=200 | grep -c '"message": "request completed"'
kubectl -n starfleet logs deployment/shop --tail=200 | grep -c '"level": "error"'
```

The first count is `total` and the second is `errors`. The share is about one half, because the log holds all failed requests and only a fifth of the successful ones. That share is not the failure ratio of the traffic.

## Ask Prometheus

The metric counts every request. These two expressions give the fraction of successful requests that wrote a record and the true failure ratio:

```text
sum(shop_log_records_total{level="info"}) / sum(shop_http_requests_total{status="200"})
sum(rate(shop_http_requests_total{status="500"}[1m])) / sum(rate(shop_http_requests_total[1m]))
```

The first value is close to 0.2. The second is close to 0.17, because one request in six fails.

## Save The Evidence

Save this as `record.py`. It evaluates the expressions at one moment, reads the sampling fields from the log and writes the ConfigMap.

```python
import json, os, subprocess, tempfile, time, urllib.parse


def call(*args):
    result = subprocess.run(list(args), text=True, capture_output=True, timeout=20)
    assert result.returncode == 0, 'Observation command failed: ' + args[0]
    return result.stdout.strip()


def in_cluster(script, *arguments):
    return call('kubectl', '-n', 'starfleet', 'exec', 'shuttle', '--', 'python', '-c', script, *arguments)


def query(expression, when):
    script = 'import sys, urllib.request; print(urllib.request.urlopen(sys.argv[1], timeout=8).read().decode())'
    url = 'http://prometheus:9090/api/v1/query?' + urllib.parse.urlencode({'query': expression, 'time': when})
    return json.loads(in_cluster(script, url))


def result(expression, when):
    answer = query(expression, when)
    assert answer['status'] == 'success' and answer['data']['result'], 'Wait for enough scrapes'
    return {'expression': expression, 'evaluated_at': when, 'data': answer['data']}


def send_request(path):
    script = (
        'import sys, urllib.error, urllib.request\n'
        'try:\n'
        '    print(urllib.request.urlopen(sys.argv[1], timeout=8).read().decode())\n'
        'except urllib.error.HTTPError as error:\n'
        '    print(error.read().decode())\n'
    )
    return json.loads(in_cluster(script, 'http://shop:8080' + path))


def shop_records(lines=500):
    records = []
    for line in call('kubectl', '-n', 'starfleet', 'logs', 'deployment/shop', '--tail=%d' % lines).splitlines():
        try:
            record = json.loads(line)
        except ValueError:
            continue
        if record.get('message') == 'request completed':
            records.append(record)
    return records


def save(report):
    resource = {'apiVersion': 'v1', 'kind': 'ConfigMap', 'metadata': {'name': 'evidence', 'namespace': 'starfleet'}, 'data': {'report.json': json.dumps(report, sort_keys=True)}}
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as handle:
        json.dump(resource, handle)
        path = handle.name
    call('kubectl', 'apply', '-f', path)
    os.unlink(path)


assert call('kubectl', 'config', 'current-context') == 'kind-astro-ats-047-lab-020-02-01'

now = time.time()
fraction = result('sum(shop_log_records_total{level="info"}) / sum(shop_http_requests_total{status="200"})', now)
live = shop_records()
sample_every = {
    'success': next(item['sample_every'] for item in live if item['level'] == 'info'),
    'error': next(item['sample_every'] for item in live if item['level'] == 'error'),
}

error_ratio = result('sum(rate(shop_http_requests_total{status="500"}[1m])) / sum(rate(shop_http_requests_total[1m]))', now)

recent = shop_records(200)
share = {'errors': sum(1 for item in recent if item['level'] == 'error'), 'total': len(recent)}
save({
    'logged_success_fraction': fraction,
    'sample_every': sample_every,
    'sensitive_field': 'email',
    'error_ratio': error_ratio,
    'log_error_share': share,
})
```

Run it and check the result:

```sh
python3 record.py
kubectl -n starfleet get configmap evidence -o jsonpath='{.data.report\.json}'
```

Then submit with `astrona submit`. After you finish, remove the lab with `astrona destroy ats-047-lab-020-02-01`.

## Common pitfalls

> [!WARNING]
> Do not calculate the failure ratio from log lines: the shop samples successful requests, so the log shows about 0.5 instead of 0.17. A `sum` of the label sets on the two sides is needed, because a division matches series with the same labels. Count only request records, not the line that says that the shop started.
