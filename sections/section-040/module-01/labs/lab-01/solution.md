---
draft: true
exam_objectives:
- Push vs Pull
---
# Push A Batch Result And Keep Its Job Label Solution

Select the cluster of this lab first.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-047-lab-040-01-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-047-lab-040-01-01" || exit 1
```

## Inspect the starting state

The pushed group does not exist yet. Read the current scrape job for the Pushgateway.

```sh
kubectl -n starfleet get configmap prometheus-config -o jsonpath='{.data.prometheus\.yaml}'
```

The job `pushgateway` has no `honor_labels` line. Without it, Prometheus renames a pushed `job` label to `exported_job` and sets `job="pushgateway"` from the scrape job.

## Push the group

A PUT request to `/metrics/job/nightly_report` replaces every metric in the group with the request body. The `shuttle` pod has Python, so it sends the request.

```sh
kubectl -n starfleet exec shuttle -- python -c '
import time, urllib.request
body = ("lab_batch_records_processed 42\nlab_batch_last_success_timestamp_seconds %d\n" % int(time.time())).encode()
request = urllib.request.Request("http://pushgateway:9091/metrics/job/nightly_report", data=body, method="PUT")
print(urllib.request.urlopen(request, timeout=8).status)
'
```

The Pushgateway answers with status 200. The body ends with a newline because the text format requires it.

## Keep the pushed job label

Add `honor_labels: true` to the scrape job and apply the change. A mounted ConfigMap can take about a minute to reach the pod, so restart the Deployment to load the new file at once.

```sh
kubectl -n starfleet get configmap prometheus-config -o json | python3 -c '
import json, sys
cm = json.load(sys.stdin)
text = cm["data"]["prometheus.yaml"]
cm["data"]["prometheus.yaml"] = text.replace("- job_name: pushgateway\n", "- job_name: pushgateway\n  honor_labels: true\n")
json.dump(cm, sys.stdout)
' | kubectl apply -f -
kubectl -n starfleet rollout restart deployment/prometheus
kubectl -n starfleet rollout status deployment/prometheus --timeout=180s
```

## Record the evidence

Save this as `record.py`. It evaluates the three expressions once, at one time, and stores the answers.

```python
import json, subprocess, tempfile, time, urllib.parse

def call(*args):
    result = subprocess.run(list(args), text=True, capture_output=True, timeout=60)
    assert result.returncode == 0, result.stderr
    return result.stdout

def query(expression):
    stamp = time.time()
    url = 'http://prometheus:9090/api/v1/query?' + urllib.parse.urlencode({'query': expression, 'time': stamp})
    script = 'import urllib.request; print(urllib.request.urlopen(%r, timeout=8).read().decode())' % url
    answer = json.loads(call('kubectl', '-n', 'starfleet', 'exec', 'shuttle', '--', 'python', '-c', script))
    assert answer['status'] == 'success' and len(answer['data']['result']) == 1, 'Wait for more scrapes: ' + expression
    return {'expression': expression, 'evaluated_at': stamp, 'data': answer['data']}

report = {
    'batch_records': query('lab_batch_records_processed{job="nightly_report"}'),
    'batch_age': query('time() - lab_batch_last_success_timestamp_seconds{job="nightly_report"}'),
    'gateway_up': query('up{job="pushgateway"}'),
}
resource = {'apiVersion': 'v1', 'kind': 'ConfigMap', 'metadata': {'name': 'evidence', 'namespace': 'starfleet'}, 'data': {'report.json': json.dumps(report, sort_keys=True)}}
with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as handle:
    json.dump(resource, handle)
call('kubectl', 'apply', '-f', handle.name)
```

```sh
python3 record.py
```

If the script stops with "Wait for more scrapes", wait ten seconds and run it again. Then run `astrona submit`.

After you record your result, remove the lab with `astrona destroy ats-047-lab-040-01-01`.

## Common pitfalls

> [!WARNING]
> Do not push with POST and a different group each run: a group stays in the Pushgateway until you replace or delete it. Do not edit the ConfigMap without restarting or reloading Prometheus, because the running server keeps its old configuration.
