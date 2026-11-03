# Live checks. check.py runs this file with exec(), so the helpers command(),
# kubectl() and get() from check.py are available.
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


def _declared_types(prefix):
    types = {}
    for line in _in_cluster('http://shop-a:8080/metrics').splitlines():
        parts = line.split()
        if len(parts) == 4 and parts[0] == '#' and parts[1] == 'TYPE' and parts[2].startswith(prefix):
            types[parts[2]] = parts[3]
    return types


def _live_result(report, key, required_patterns):
    """Re-run the recorded expression at the recorded time and return the series list."""
    item = report[key]
    expression = item['expression']
    assert isinstance(expression, str), key + ': the expression must be a string'
    assert 0 <= time.time() - float(item['evaluated_at']) <= 300, key + ': refresh the evidence within five minutes'
    for pattern in required_patterns:
        assert re.search(pattern, expression), key + ': the expression does not use the required series, function or grouping'
    assert 'irate(' not in expression, key + ': use rate(), not irate()'
    live = _prometheus(expression, item['evaluated_at'])
    assert live['status'] == 'success', key + ': Prometheus rejected the expression'
    assert item['data'] == live['data'], key + ': the recorded data differs from what Prometheus returns'
    assert live['data']['resultType'] == 'vector', key + ': the expression must return an instant vector'
    return live['data']['result']


def _single_value(series, key, low, high):
    assert len(series) == 1, key + ': the expression must return exactly one series'
    value = float(series[0]['value'][1])
    assert low <= value <= high, key + ': the value is outside the range the traffic produces'


def _lab_checks():
    report = json.loads(get('configmap', 'evidence')['data']['report.json'])
    assert report['unbounded_label'] == 'user_id', 'unbounded_label must name the label whose values grow with the users'
    cardinality = _live_result(report, 'cardinality', [r'count\s+by\s*\(\s*__name__\s*\)', r'job\s*=\s*"shop"'])
    assert len(cardinality) >= 4, 'cardinality: the result must list every metric name of the shop job'
    largest = max(cardinality, key=lambda series: float(series['value'][1]))
    assert largest['metric'].get('__name__') == 'shop_user_requests_total', 'cardinality: the metric with the most series is not identified'
    by_route = _live_result(report, 'fleet_route_rate', [r'(?<![a-z])rate\(', r'shop_http_requests_total', r'by\s*\(\s*route\s*\)'])
    assert len(by_route) == 3 and all(set(series['metric']) == {'route'} for series in by_route), 'fleet_route_rate: return one series per route and keep only the route label'
    total = sum(float(series['value'][1]) for series in by_route)
    assert 3.0 <= total <= 6.0, 'fleet_route_rate: the total rate is outside the range the traffic produces'
    ratio = _live_result(report, 'fleet_error_ratio', [r'(?<![a-z])rate\(', r'shop_http_requests_total', r'status\s*=\s*"500"'])
    _single_value(ratio, 'fleet_error_ratio', 0.12, 0.24)


_lab_checks()
