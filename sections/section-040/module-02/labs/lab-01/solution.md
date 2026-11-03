---
draft: true
exam_objectives:
- Push vs Pull
---
# Configure Remote Write And Observe A Stale Series Solution

Select the cluster of this lab first.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-047-lab-040-02-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-047-lab-040-02-01" || exit 1
```

## Add remote write

The `remote_write` section is a top-level list in the Prometheus configuration. Append it to the file in the ConfigMap, apply the ConfigMap and restart the Deployment so the server reads the file.

```sh
kubectl -n starfleet get configmap prometheus-config -o json | python3 -c '
import json, sys
cm = json.load(sys.stdin)
cm["data"]["prometheus.yaml"] += "remote_write:\n- url: http://receiver:9090/api/v1/write\n"
json.dump(cm, sys.stdout)
' | kubectl apply -f -
kubectl -n starfleet rollout restart deployment/prometheus
kubectl -n starfleet rollout status deployment/prometheus --timeout=180s
```

## Push a group and delete it

The first request creates the group. After a few scrapes, check that Prometheus returns the series, then delete the group.

```sh
kubectl -n starfleet exec shuttle -- python -c '
import urllib.request
request = urllib.request.Request("http://pushgateway:9091/metrics/job/temp_export", data=b"lab_temp_value 1\n", method="PUT")
print(urllib.request.urlopen(request, timeout=8).status)
'
```

```sh
kubectl -n starfleet exec shuttle -- python -c '
import urllib.request
print(urllib.request.urlopen("http://prometheus:9090/api/v1/query?query=lab_temp_value", timeout=8).read().decode())
'
```

When the result is not empty, send the DELETE request. The Pushgateway answers with status 202 because it queues the deletion.

```sh
kubectl -n starfleet exec shuttle -- python -c '
import urllib.request
request = urllib.request.Request("http://pushgateway:9091/metrics/job/temp_export", method="DELETE")
print(urllib.request.urlopen(request, timeout=8).status)
'
```

Wait at least ten seconds. The next scrape no longer contains the series, so Prometheus writes a staleness marker and the instant query returns nothing, although the samples before the marker are still stored.

## Record the evidence

Save this as `record.py`.

```python
import json, subprocess, tempfile, time, urllib.parse

def call(*args):
    result = subprocess.run(list(args), text=True, capture_output=True, timeout=60)
    assert result.returncode == 0, result.stderr
    return result.stdout

def query(base, expression, count):
    stamp = time.time()
    url = base + '/api/v1/query?' + urllib.parse.urlencode({'query': expression, 'time': stamp})
    script = 'import urllib.request; print(urllib.request.urlopen(%r, timeout=8).read().decode())' % url
    answer = json.loads(call('kubectl', '-n', 'starfleet', 'exec', 'shuttle', '--', 'python', '-c', script))
    assert answer['status'] == 'success' and len(answer['data']['result']) == count, 'Unexpected result for ' + expression
    return {'expression': expression, 'evaluated_at': stamp, 'data': answer['data']}

local, receiver = 'http://prometheus:9090', 'http://receiver:9090'
report = {
    'receiver_probe': query(receiver, 'up{job="probe"}', 1),
    'samples_sent': query(local, 'sum(prometheus_remote_storage_samples_total)', 1),
    'instant_after_delete': query(local, 'lab_temp_value{job="temp_export"}', 0),
    'history_kept': query(local, 'count_over_time(lab_temp_value{job="temp_export"}[10m])', 1),
}
resource = {'apiVersion': 'v1', 'kind': 'ConfigMap', 'metadata': {'name': 'evidence', 'namespace': 'starfleet'}, 'data': {'report.json': json.dumps(report, sort_keys=True)}}
with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as handle:
    json.dump(resource, handle)
call('kubectl', 'apply', '-f', handle.name)
```

```sh
python3 record.py
```

Then run `astrona submit`. After you record your result, remove the lab with `astrona destroy ats-047-lab-040-02-01`.

## Common pitfalls

> [!WARNING]
> Do not restart the `receiver` Deployment: the new pod starts with empty storage. Do not delete the group before Prometheus has scraped it once, because then no samples exist to count.
