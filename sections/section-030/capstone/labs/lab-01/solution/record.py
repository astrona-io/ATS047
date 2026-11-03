import json, os, subprocess, tempfile, time, urllib.parse


def call(*args):
    result = subprocess.run(list(args), text=True, capture_output=True, timeout=30)
    assert result.returncode == 0, 'Observation command failed: ' + args[0]
    return result.stdout.strip()


def in_cluster(url, headers=None):
    script = 'import urllib.request; print(urllib.request.urlopen(urllib.request.Request(%r, headers=%r), timeout=8).read().decode())' % (url, headers or {})
    return call('kubectl', '-n', 'starfleet', 'exec', 'shuttle', '--', 'python', '-c', script)


def spans_for(trace_id):
    found = []
    for deployment in ('probe', 'scout'):
        for line in call('kubectl', '-n', 'starfleet', 'logs', 'deployment/' + deployment, '--tail=5000').splitlines():
            try:
                record = json.loads(line)
            except ValueError:
                continue
            if record.get('event') == 'span' and record.get('trace_id') == trace_id:
                found.append(record)
    return sorted(found, key=lambda record: record['service'])


def prometheus(path, **params):
    return json.loads(in_cluster('http://prometheus:9090' + path + '?' + urllib.parse.urlencode(params)))


def slowest_exemplar(expression, now):
    answer = prometheus('/api/v1/query_exemplars', query=expression, start=now - 300, end=now)
    candidates = [(float(item['value']), item['labels']['trace_id']) for series in answer['data'] for item in series['exemplars']]
    assert candidates, 'Wait for exemplars to be scraped'
    value, trace_id = max(candidates)
    return value, trace_id


def save(report):
    resource = {'apiVersion': 'v1', 'kind': 'ConfigMap', 'metadata': {'name': 'evidence', 'namespace': 'starfleet'}, 'data': {'report.json': json.dumps(report, sort_keys=True)}}
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as handle:
        json.dump(resource, handle)
        path = handle.name
    call('kubectl', 'apply', '-f', path)
    os.unlink(path)


def ratio(expression, now):
    answer = prometheus('/api/v1/query', query=expression, time=now)
    assert answer['status'] == 'success' and answer['data']['result'], 'Wait for enough scrapes'
    return {'expression': expression, 'evaluated_at': now, 'data': answer['data']}


assert call('kubectl', 'config', 'current-context') == 'kind-astro-ats-047-lab-030-capstone-01'
now = time.time()
expression = 'lab_request_duration_seconds_bucket{service="probe"}'
value, trace_id = slowest_exemplar(expression, now)
spans = spans_for(trace_id)
assert len(spans) == 2, 'Expected one span in each service for the trace'
probe, scout = spans
self_time = {'probe': round(probe['duration_seconds'] - scout['duration_seconds'], 6), 'scout': scout['duration_seconds']}
report = {
    'exemplar': {'expression': expression, 'evaluated_at': now, 'trace_id': trace_id, 'value': value},
    'spans': spans,
    'self_time_seconds': self_time,
    'critical_service': max(self_time, key=self_time.get),
    'leaking_attribute': {'service': 'probe', 'key': 'http.target'},
    'unsampled_share': ratio('sum(rate(lab_traces_started_total{sampled="false"}[1m])) / sum(rate(lab_traces_started_total[1m]))', now),
}
save(report)
