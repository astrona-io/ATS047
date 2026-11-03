import json, os, subprocess, tempfile, time, urllib.parse

CONTEXT = 'kind-astro-ats-047-lab-040-01-01'


def call(*args):
    result = subprocess.run(list(args), text=True, capture_output=True, timeout=200)
    assert result.returncode == 0, 'Command failed: ' + ' '.join(args[:4]) + ' ' + result.stderr
    return result.stdout.strip()


def in_cluster(script):
    return call('kubectl', '-n', 'starfleet', 'exec', 'shuttle', '--', 'python', '-c', script)


def api(path):
    return json.loads(in_cluster('import urllib.request; print(urllib.request.urlopen(%r, timeout=8).read().decode())' % ('http://prometheus:9090' + path)))


def query(expression):
    stamp = time.time()
    answer = api('/api/v1/query?' + urllib.parse.urlencode({'query': expression, 'time': stamp}))
    assert answer['status'] == 'success' and len(answer['data']['result']) == 1, 'Wait for the series: ' + expression
    return {'expression': expression, 'evaluated_at': stamp, 'data': answer['data']}


def apply(resource):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as handle:
        json.dump(resource, handle)
        path = handle.name
    try:
        call('kubectl', 'apply', '-f', path)
    finally:
        os.unlink(path)


assert call('kubectl', 'config', 'current-context') == CONTEXT

# 1. Push the batch result as one group.
body = 'lab_batch_records_processed 42\nlab_batch_last_success_timestamp_seconds %d\n' % int(time.time())
in_cluster('import urllib.request\nrequest = urllib.request.Request("http://pushgateway:9091/metrics/job/nightly_report", data=%r, method="PUT")\nurllib.request.urlopen(request, timeout=8).read()' % body.encode())

# 2. Keep the pushed job label: set honor_labels on the pushgateway scrape job.
config_map = json.loads(call('kubectl', '-n', 'starfleet', 'get', 'configmap', 'prometheus-config', '-o', 'json'))
text = config_map['data']['prometheus.yaml']
if 'honor_labels' not in text:
    text = text.replace('- job_name: pushgateway\n', '- job_name: pushgateway\n  honor_labels: true\n')
    config_map['data']['prometheus.yaml'] = text
    for key in ('resourceVersion', 'uid', 'creationTimestamp', 'managedFields'):
        config_map['metadata'].pop(key, None)
    apply(config_map)
    call('kubectl', '-n', 'starfleet', 'rollout', 'restart', 'deployment/prometheus')
    call('kubectl', '-n', 'starfleet', 'rollout', 'status', 'deployment/prometheus', '--timeout=180s')

# 3. Wait until Prometheus has scraped the group, then record the evidence.
for attempt in range(40):
    try:
        if api('/api/v1/query?' + urllib.parse.urlencode({'query': 'lab_batch_records_processed{job="nightly_report"}'}))['data']['result']:
            break
    except (AssertionError, subprocess.SubprocessError, ValueError):
        pass
    time.sleep(3)
report = {
    'batch_records': query('lab_batch_records_processed{job="nightly_report"}'),
    'batch_age': query('time() - lab_batch_last_success_timestamp_seconds{job="nightly_report"}'),
    'gateway_up': query('up{job="pushgateway"}'),
}
apply({'apiVersion': 'v1', 'kind': 'ConfigMap', 'metadata': {'name': 'evidence', 'namespace': 'starfleet'}, 'data': {'report.json': json.dumps(report, sort_keys=True)}})
