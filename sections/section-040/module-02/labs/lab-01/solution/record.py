import json, os, subprocess, tempfile, time, urllib.parse

CONTEXT = 'kind-astro-ats-047-lab-040-02-01'


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


def query(base, expression, count):
    stamp = time.time()
    answer = raw_query(base, expression, stamp)
    assert answer['status'] == 'success' and len(answer['data']['result']) == count, 'Unexpected result for ' + expression
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


def push(method, body=None):
    in_cluster('import urllib.request\nrequest = urllib.request.Request("http://pushgateway:9091/metrics/job/temp_export", data=%r, method=%r)\nurllib.request.urlopen(request, timeout=8).read()' % (body, method))


assert call('kubectl', 'config', 'current-context') == CONTEXT
PROM = 'http://prometheus:9090'
RECV = 'http://receiver:9090'

# 1. Configure remote write on the first Prometheus server and restart it.
config_map = json.loads(call('kubectl', '-n', 'starfleet', 'get', 'configmap', 'prometheus-config', '-o', 'json'))
text = config_map['data']['prometheus.yaml']
if 'remote_write' not in text:
    config_map['data']['prometheus.yaml'] = text + 'remote_write:\n- url: http://receiver:9090/api/v1/write\n'
    for key in ('resourceVersion', 'uid', 'creationTimestamp', 'managedFields'):
        config_map['metadata'].pop(key, None)
    apply(config_map)
    call('kubectl', '-n', 'starfleet', 'rollout', 'restart', 'deployment/prometheus')
    call('kubectl', '-n', 'starfleet', 'rollout', 'status', 'deployment/prometheus', '--timeout=180s')

# 2. Push a group, wait until it is scraped, delete it and wait for the stale marker.
push('PUT', b'lab_temp_value 1\n')
wait_for(lambda: raw_query(PROM, 'lab_temp_value{job="temp_export"}')['data']['result'])
push('DELETE')
wait_for(lambda: not raw_query(PROM, 'lab_temp_value{job="temp_export"}')['data']['result'])
time.sleep(10)

# 3. Wait for the receiver to hold the probe samples, then record the evidence.
wait_for(lambda: raw_query(RECV, 'up{job="probe"}')['data']['result'])
report = {
    'receiver_probe': query(RECV, 'up{job="probe"}', 1),
    'samples_sent': query(PROM, 'sum(prometheus_remote_storage_samples_total)', 1),
    'instant_after_delete': query(PROM, 'lab_temp_value{job="temp_export"}', 0),
    'history_kept': query(PROM, 'count_over_time(lab_temp_value{job="temp_export"}[10m])', 1),
}
apply({'apiVersion': 'v1', 'kind': 'ConfigMap', 'metadata': {'name': 'evidence', 'namespace': 'starfleet'}, 'data': {'report.json': json.dumps(report, sort_keys=True)}})
