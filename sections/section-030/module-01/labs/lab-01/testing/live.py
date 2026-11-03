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
    trace = '0af7651916cd43dd8448eb211c80319c'
    assert report['trace_id'] == trace, 'trace_id must be the id sent in the traceparent header'
    live = _live_spans(trace)
    assert len(live) == 2, 'The logs of probe and scout must each hold one span of the trace; send the request again'
    assert report['spans'] == live, 'spans must be the span records from the logs of probe and scout'
    probe, scout = live
    assert probe['parent_span_id'] == 'b7ad6b7169203331', 'The probe span must name the parent id from the header'
    assert scout['parent_span_id'] == probe['span_id'], 'The scout span must name the probe span as its parent'
    assert scout['duration_seconds'] >= 0.2, 'The scout span must include the child_delay of 0.2 seconds'
    expected = probe['duration_seconds'] - scout['duration_seconds']
    assert abs(float(report['probe_self_time_seconds']) - expected) < 1e-5, 'probe_self_time_seconds must be the probe duration minus the scout duration'
    orphan = report['orphan']
    ids = (orphan['probe_trace_id'], orphan['scout_trace_id'])
    assert all(re.fullmatch(r'[0-9a-f]{32}', value) for value in ids) and ids[0] != ids[1], 'The orphan request must show two different trace ids'
    assert any(r.get('event') == 'request_completed' and r.get('trace_id') == ids[0] for r in _log_records('probe')), 'probe_trace_id is not in the probe log'
    assert any(r.get('event') == 'request_completed' and r.get('trace_id') == ids[1] and r.get('parent_span_id') is None for r in _log_records('scout')), 'scout_trace_id must be a trace that scout started itself'


_lab_checks()
