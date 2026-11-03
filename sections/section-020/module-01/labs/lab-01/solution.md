---
draft: true
exam_objectives:
- Understand logs and events
---
# Correlate A Failed Request With Its Log Record And Route Metric Solution

The solution sends one failing request, finds its log record by the request identifier and asks Prometheus which route fails. Select the lab cluster first.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-047-lab-020-01-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-047-lab-020-01-01" || exit 1
```

## Send The Request

Define a helper that sends a request from the `shuttle` pod and prints the HTTP status code and the response body. A failing request returns status `500`, and Python raises an error for that status, so the helper catches it and prints the body anyway.

```sh
send_request() {
  kubectl -n starfleet exec shuttle -- python -c '
import sys, urllib.error, urllib.request
try:
    reply = urllib.request.urlopen(sys.argv[1], timeout=8)
    print(reply.status, reply.read().decode())
except urllib.error.HTTPError as error:
    print(error.code, error.read().decode())
' "$1"
}
```

Send the failing request:

```sh
send_request "http://shop:8080/work?route=/checkout&status=500&user=lab-user"
```

The output has the status code `500` and a JSON body with the fields `request_id`, `route` and `status`. Note the value of `request_id`.

## Find The Record

The shop writes each logged request as one JSON line to standard output. Read the last lines and search for your request identifier. Replace `<REQUEST_ID>` with the value from the response.

```sh
kubectl -n starfleet logs deployment/shop --tail=500 | grep '<REQUEST_ID>'
```

The shop writes a record for every failed request. The line holds the fields `ts`, `level`, `route`, `status`, `user_id` and `request_id`, among others. Copy the line unchanged into the report.

## Ask Prometheus Which Route Fails

The metric `shop_http_requests_total` has the labels `route` and `status`. Filter on `status="500"`, apply `rate()` to each series and sum by `route`:

```text
sum by (route) (rate(shop_http_requests_total{status="500"}[1m]))
```

Only `/checkout` returns a result, with about 0.3 failed requests per second.

## Save The Evidence

Save this as `record.py`. It sends the request, finds the record, evaluates the expression at one moment and writes the ConfigMap.

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


assert call('kubectl', 'config', 'current-context') == 'kind-astro-ats-047-lab-020-01-01'

response = send_request('/work?route=/checkout&status=500&user=%USER%')
record = next(item for item in shop_records() if item['request_id'] == response['request_id'])

now = time.time()
failing_routes = result('sum by (route) (rate(shop_http_requests_total{status="500"}[1m]))', now)

save({'response': response, 'record': record, 'failing_routes': failing_routes})
```

Run it and check the result:

```sh
python3 record.py
kubectl -n starfleet get configmap evidence -o jsonpath='{.data.report\.json}'
```

Then submit with `astrona submit`. After you finish, remove the lab with `astrona destroy ats-047-lab-020-01-01`.

## Common pitfalls

> [!WARNING]
> A request with status `200` is logged only one time in five, so a successful request may have no record. Use `status=500` for this task. Copy the record unchanged: a re-formatted line no longer matches the shop log. An `evaluated_at` older than five minutes fails the check.
