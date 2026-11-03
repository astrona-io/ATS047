import json, os, subprocess, tempfile, time, urllib.parse

CONTEXT = 'kind-astro-ats-047-lab-040-capstone-01'
PROM = 'http://prometheus:9090'
RECV = 'http://receiver:9090'


def call(*args):
    result = subprocess.run(list(args), text=True, capture_output=True, timeout=200)
    assert result.returncode == 0, 'Command failed: ' + ' '.join(args[:4]) + ' ' + result.stderr
    return result.stdout.strip()


def in_cluster(script):
    return call('kubectl', '-n', 'starfleet', 'exec', 'shuttle', '--', 'python', '-c', script)


def api(base, path):
    return json.loads(in_cluster('import urllib.request; print(urllib.request.urlopen(%r, timeout=8).read().decode())' % (base + path)))


def raw_query(base, expression, when=None):
    params = {'query': expression}
    if when:
        params['time'] = when
    return api(base, '/api/v1/query?' + urllib.parse.urlencode(params))


def query(base, expression):
    stamp = time.time()
    answer = raw_query(base, expression, stamp)
    assert answer['status'] == 'success' and len(answer['data']['result']) == 1, 'Unexpected result for ' + expression
    return {'expression': expression, 'evaluated_at': stamp, 'data': answer['data']}


def apply(resource):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as handle:
        json.dump(resource, handle)
        path = handle.name
    try:
        call('kubectl', 'apply', '-f', path)
    finally:
        os.unlink(path)


def wait_for(check):
    for attempt in range(60):
        try:
            if check():
                return
        except (AssertionError, subprocess.SubprocessError, ValueError, KeyError):
            pass
        time.sleep(3)
    raise AssertionError('Condition did not hold in time')


def gateway(method, job, body=None):
    in_cluster('import urllib.request\nrequest = urllib.request.Request("http://pushgateway:9091/metrics/job/" + %r, data=%r, method=%r)\nurllib.request.urlopen(request, timeout=8).read()' % (job, body, method))


assert call('kubectl', 'config', 'current-context') == CONTEXT

# 1. Delete the stale groups and push a fresh result.
for job in ('old_export', 'legacy_sync'):
    gateway('DELETE', job)
gateway('PUT', 'nightly_report', ('lab_batch_last_success_timestamp_seconds %d\n' % int(time.time())).encode())

# 2. Keep the pushed job label and send samples to the receiver.
config_map = json.loads(call('kubectl', '-n', 'starfleet', 'get', 'configmap', 'prometheus-config', '-o', 'json'))
text = config_map['data']['prometheus.yaml']
if 'honor_labels' not in text:
    text = text.replace('- job_name: pushgateway\n', '- job_name: pushgateway\n  honor_labels: true\n')
if 'remote_write' not in text:
    text += 'remote_write:\n- url: http://receiver:9090/api/v1/write\n'
config_map['data']['prometheus.yaml'] = text
for key in ('resourceVersion', 'uid', 'creationTimestamp', 'managedFields'):
    config_map['metadata'].pop(key, None)
apply(config_map)
call('kubectl', '-n', 'starfleet', 'rollout', 'restart', 'deployment/prometheus')
call('kubectl', '-n', 'starfleet', 'rollout', 'status', 'deployment/prometheus', '--timeout=180s')

# 3. Wait for the group on both servers, then record the evidence.
wait_for(lambda: raw_query(PROM, 'lab_batch_last_success_timestamp_seconds{job="nightly_report"}')['data']['result'])
wait_for(lambda: raw_query(RECV, 'lab_batch_last_success_timestamp_seconds{job="nightly_report"}')['data']['result'])
report = {
    'groups': query(PROM, 'count by (job) (lab_batch_last_success_timestamp_seconds)'),
    'batch_age': query(PROM, 'time() - lab_batch_last_success_timestamp_seconds{job="nightly_report"}'),
    'downstream': query(RECV, 'lab_batch_last_success_timestamp_seconds{job="nightly_report"}'),
}
apply({'apiVersion': 'v1', 'kind': 'ConfigMap', 'metadata': {'name': 'evidence', 'namespace': 'starfleet'}, 'data': {'report.json': json.dumps(report, sort_keys=True)}})
