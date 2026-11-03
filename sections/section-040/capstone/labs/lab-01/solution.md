---
draft: true
exam_objectives:
- Push vs Pull
---
# Pull Versus Push Capstone Solution

Select the cluster of this lab first.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-047-lab-040-capstone-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-047-lab-040-capstone-01" || exit 1
```

## Replace the stale groups with the fresh result

A DELETE request on `/metrics/job/<name>` removes every metric of a group, and a PUT request creates or replaces one. The Pushgateway answers a DELETE with status 202 because it queues the deletion.

```sh
kubectl -n starfleet exec shuttle -- python -c '
import time, urllib.request
for job in ("old_export", "legacy_sync"):
    request = urllib.request.Request("http://pushgateway:9091/metrics/job/" + job, method="DELETE")
    print(job, urllib.request.urlopen(request, timeout=8).status)
body = ("lab_batch_last_success_timestamp_seconds %d\n" % int(time.time())).encode()
request = urllib.request.Request("http://pushgateway:9091/metrics/job/nightly_report", data=body, method="PUT")
print("nightly_report", urllib.request.urlopen(request, timeout=8).status)
'
```

## Change the Prometheus configuration

Add `honor_labels: true` to the `pushgateway` job and append the `remote_write` section. Then restart the Deployment so it loads the file.

```sh
kubectl -n starfleet get configmap prometheus-config -o json | python3 -c '
import json, sys
cm = json.load(sys.stdin)
text = cm["data"]["prometheus.yaml"]
text = text.replace("- job_name: pushgateway\n", "- job_name: pushgateway\n  honor_labels: true\n")
text += "remote_write:\n- url: http://receiver:9090/api/v1/write\n"
cm["data"]["prometheus.yaml"] = text
json.dump(cm, sys.stdout)
' | kubectl apply -f -
kubectl -n starfleet rollout restart deployment/prometheus
kubectl -n starfleet rollout status deployment/prometheus --timeout=180s
```

## Record the evidence

Wait about thirty seconds so the group is scraped and forwarded. Save this as `record.py`.

```python
import json, subprocess, tempfile, time, urllib.parse

def call(*args):
    result = subprocess.run(list(args), text=True, capture_output=True, timeout=60)
    assert result.returncode == 0, result.stderr
    return result.stdout

def query(base, expression):
    stamp = time.time()
    url = base + '/api/v1/query?' + urllib.parse.urlencode({'query': expression, 'time': stamp})
    script = 'import urllib.request; print(urllib.request.urlopen(%r, timeout=8).read().decode())' % url
    answer = json.loads(call('kubectl', '-n', 'starfleet', 'exec', 'shuttle', '--', 'python', '-c', script))
    assert answer['status'] == 'success' and len(answer['data']['result']) == 1, 'Wait and retry: ' + expression
    return {'expression': expression, 'evaluated_at': stamp, 'data': answer['data']}

local, receiver = 'http://prometheus:9090', 'http://receiver:9090'
report = {
    'groups': query(local, 'count by (job) (lab_batch_last_success_timestamp_seconds)'),
    'batch_age': query(local, 'time() - lab_batch_last_success_timestamp_seconds{job="nightly_report"}'),
    'downstream': query(receiver, 'lab_batch_last_success_timestamp_seconds{job="nightly_report"}'),
}
resource = {'apiVersion': 'v1', 'kind': 'ConfigMap', 'metadata': {'name': 'evidence', 'namespace': 'starfleet'}, 'data': {'report.json': json.dumps(report, sort_keys=True)}}
with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as handle:
    json.dump(resource, handle)
call('kubectl', 'apply', '-f', handle.name)
```

```sh
python3 record.py
```

Then run `astrona submit`. After you record your result, remove the lab with `astrona destroy ats-047-lab-040-capstone-01`.

## Common pitfalls

> [!WARNING]
> Do not delete the group `nightly_report` or the `receiver` Deployment while you work. A restart of `prometheus` empties its storage, so wait for new scrapes before you record the evidence.
