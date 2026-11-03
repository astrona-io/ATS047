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
    assert report['metric_types'] == _declared_types('shop_'), 'metric_types must match the # TYPE lines of the shop metrics'
    assert report['unbounded_label'] == 'user_id', 'unbounded_label must name the label whose values grow with the users'
    assert report['naming_issue'] == 'shop_latency_ms', 'naming_issue must name the metric that breaks the unit naming convention'
    quantile = _live_result(report, 'p95_latency', [r'histogram_quantile\(\s*0\.95', r'(?<![a-z])rate\(', r'shop_request_duration_seconds_bucket', r'by\s*\(\s*le\s*\)'])
    _single_value(quantile, 'p95_latency', 0.1, 0.25)
    ratios = _live_result(report, 'error_ratio_by_instance', [r'(?<![a-z])rate\(', r'shop_http_requests_total', r'status\s*=\s*"500"', r'by\s*\(\s*instance\s*\)'])
    assert len(ratios) == 2 and all(set(series['metric']) == {'instance'} for series in ratios), 'error_ratio_by_instance: return one series per instance and keep only the instance label'
    values = {series['metric']['instance']: float(series['value'][1]) for series in ratios}
    assert 0.05 <= values.get('shop-a:8080', -1) <= 0.15, 'error_ratio_by_instance: the ratio for shop-a is outside the range the traffic produces'
    assert 0.4 <= values.get('shop-b:8080', -1) <= 0.6, 'error_ratio_by_instance: the ratio for shop-b is outside the range the traffic produces'


_lab_checks()
