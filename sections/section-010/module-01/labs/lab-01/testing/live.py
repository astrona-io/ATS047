# Live checks for the metric-types lab. check.py runs this file with exec(),
# so the helpers command(), kubectl() and get() from check.py are available.
import json
import re
import time
import urllib.parse


def _in_cluster(url):
    script = 'import urllib.request; print(urllib.request.urlopen(%r, timeout=8).read().decode())' % url
    return command(['kubectl', '-n', 'starfleet', 'exec', 'shuttle', '--', 'python', '-c', script]).stdout


def _prometheus(expression, when):
    query = urllib.parse.urlencode({'query': expression, 'time': when})
    return json.loads(_in_cluster('http://prometheus:9090/api/v1/query?' + query))


def _declared_types():
    types = {}
    for line in _in_cluster('http://probe:8080/metrics').splitlines():
        parts = line.split()
        if len(parts) == 4 and parts[0] == '#' and parts[1] == 'TYPE' and parts[2].startswith('lab_'):
            types[parts[2]] = parts[3]
    return types


def _checked_query(report, key, required_patterns, low, high):
    item = report[key]
    expression = item['expression']
    assert isinstance(expression, str), key + ': the expression must be a string'
    assert 0 <= time.time() - float(item['evaluated_at']) <= 300, key + ': refresh the evidence within five minutes'
    for pattern in required_patterns:
        assert re.search(pattern, expression), key + ': the expression does not use the required series or function'
    assert 'irate(' not in expression, key + ': use rate(), not irate()'
    live = _prometheus(expression, item['evaluated_at'])
    assert live['status'] == 'success', key + ': Prometheus rejected the expression'
    assert item['data'] == live['data'], key + ': the recorded data differs from what Prometheus returns'
    result = live['data']['result']
    assert live['data']['resultType'] == 'vector' and len(result) == 1, key + ': the expression must return exactly one series'
    value = float(result[0]['value'][1])
    assert low <= value <= high, key + ': the value is outside the range the traffic produces'


def _lab_checks():
    evidence = get('configmap', 'evidence')
    report = json.loads(evidence['data']['report.json'])
    assert report['metric_types'] == _declared_types(), 'metric_types must match the # TYPE lines of the probe'
    _checked_query(report, 'failure_rate', [r'(?<![a-z])rate\(', r'lab_requests_total', r'status\s*=\s*"500"'], 0.2, 0.6)
    _checked_query(report, 'fast_fraction', [r'(?<![a-z])rate\(', r'lab_request_duration_seconds_bucket', r'le\s*=\s*"0\.05"', r'lab_request_duration_seconds_count'], 0.9, 1.000001)


_lab_checks()
