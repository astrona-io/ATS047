# Live checks. check.py runs this file with exec(), so the helpers command(),
# kubectl() and get() from check.py are available.
import json
import re
import time
import urllib.parse


def _in_cluster(url):
    script = 'import urllib.request; print(urllib.request.urlopen(%r, timeout=8).read().decode())' % url
    return command(['kubectl', '-n', 'starfleet', 'exec', 'shuttle', '--', 'python', '-c', script]).stdout


def _prometheus(path, **params):
    return json.loads(_in_cluster('http://prometheus:9090' + path + '?' + urllib.parse.urlencode(params)))


def _log_records(service):
    records = []
    for line in kubectl('-n', 'starfleet', 'logs', 'deployment/' + service, '--tail=5000').splitlines():
        try:
            records.append(json.loads(line))
        except ValueError:
            continue
    return records


def _live_spans(trace_id):
    found = [r for service in ('probe', 'scout') for r in _log_records(service) if r.get('event') == 'span' and r.get('trace_id') == trace_id]
    return sorted(found, key=lambda record: record['service'])


def _fresh(item, key):
    assert 0 <= time.time() - float(item['evaluated_at']) <= 300, key + ': refresh the evidence within five minutes'


def _live_ratio(report, key, required_patterns, low, high):
    item = report[key]
    expression = item['expression']
    assert isinstance(expression, str), key + ': the expression must be a string'
    _fresh(item, key)
    for pattern in required_patterns:
        assert re.search(pattern, expression), key + ': the expression does not use the required series, function or label'
    assert 'irate(' not in expression, key + ': use rate(), not irate()'
    live = _prometheus('/api/v1/query', query=expression, time=item['evaluated_at'])
    assert live['status'] == 'success', key + ': Prometheus rejected the expression'
    assert item['data'] == live['data'], key + ': the recorded data differs from what Prometheus returns'
    series = live['data']['result']
    assert len(series) == 1, key + ': the expression must return exactly one series'
    value = float(series[0]['value'][1])
    assert low <= value <= high, key + ': the value is outside the range the traffic produces'


def _live_exemplar(item, key, minimum):
    expression = item['expression']
    assert isinstance(expression, str) and 'lab_request_duration_seconds_bucket' in expression, key + ': query the histogram bucket series'
    _fresh(item, key)
    when = float(item['evaluated_at'])
    live = _prometheus('/api/v1/query_exemplars', query=expression, start=when - 900, end=when)
    assert live['status'] == 'success', key + ': Prometheus rejected the exemplar query'
    matches = [e for series in live['data'] for e in series['exemplars'] if e['labels'].get('trace_id') == item['trace_id']]
    assert matches, key + ': the trace id is not an exemplar of this query'
    assert any(abs(float(e['value']) - float(item['value'])) < 1e-6 for e in matches), key + ': the exemplar value differs from Prometheus'
    assert float(item['value']) >= minimum, key + ': pick the exemplar of a slow request'


def _lab_checks():
    report = json.loads(get('configmap', 'evidence')['data']['report.json'])
    item = report['exemplar']
    _live_exemplar(item, 'exemplar', 0.25)
    live = _live_spans(item['trace_id'])
    assert len(live) == 2, 'The logs must hold one span per service for the exemplar trace'
    assert report['spans'] == live, 'spans must be the span records from the logs of probe and scout'
    probe, scout = live
    assert scout['parent_span_id'] == probe['span_id'], 'The scout span must be a child of the probe span'
    expected = {'probe': probe['duration_seconds'] - scout['duration_seconds'], 'scout': scout['duration_seconds']}
    for service, value in expected.items():
        assert abs(float(report['self_time_seconds'][service]) - value) < 1e-5, 'self_time_seconds.' + service + ' is wrong'
    assert report['critical_service'] == max(expected, key=expected.get), 'critical_service must be the service with the largest self time'
    leaking = [s['service'] for s in live if 'api_key=' in s['attributes'].get('http.target', '')]
    assert leaking, 'The chosen trace has no span that records the secret'
    assert report['leaking_attribute'] == {'service': leaking[0], 'key': 'http.target'}, 'leaking_attribute must name the service and the attribute key that records the secret'
    _live_ratio(report, 'unsampled_share', [r'(?<![a-z])rate\(', r'lab_traces_started_total', r'sampled\s*=\s*"false"'], 0.65, 0.85)


_lab_checks()
