# Live checks. check.py runs this file with exec(), so the helpers command(),
# kubectl() and get() from check.py are available.
import calendar
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


def _shop_records():
    """Return every JSON request record that the shop wrote to standard output."""
    lines = kubectl('-n', 'starfleet', 'logs', 'deployment/shop', '--tail=-1').splitlines()
    records = []
    for line in lines:
        try:
            record = json.loads(line)
        except ValueError:
            continue
        if isinstance(record, dict) and record.get('message') == 'request completed':
            records.append(record)
    return records


def _record_age(record):
    parsed = time.strptime(record['ts'], '%Y-%m-%dT%H:%M:%S.%fZ')
    return time.time() - calendar.timegm(parsed)


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
    return value


def _check_request_and_record(report, user):
    response = report['response']
    record = report['record']
    assert response.get('route') == '/checkout' and response.get('status') == 500, 'response: send one failing request to /checkout'
    assert record.get('request_id') == response.get('request_id'), 'record: the request_id must match the response'
    assert record.get('user_id') == user, 'record: the request must use the user ' + user
    assert record.get('level') == 'error' and record.get('route') == '/checkout' and record.get('status') == 500, 'record: it must be the error record of the failed request'
    assert record in _shop_records(), 'record: copy the record unchanged from the shop log'
    assert 0 <= _record_age(record) <= 900, 'record: send a new request, the record is older than fifteen minutes'


def _check_failing_routes(report):
    failing = _live_result(report, 'failing_routes', [r'(?<![a-z])rate\(', r'shop_http_requests_total', r'status\s*=\s*"500"', r'by\s*\(\s*route\s*\)'])
    assert len(failing) == 1 and failing[0]['metric'] == {'route': '/checkout'}, 'failing_routes: only /checkout fails, keep only the route label'
    assert 0.15 <= float(failing[0]['value'][1]) <= 0.6, 'failing_routes: the rate is outside the range the traffic produces'


def _check_sampling(report):
    fraction = _live_result(report, 'logged_success_fraction', [r'shop_log_records_total', r'level\s*=\s*"info"', r'shop_http_requests_total', r'status\s*=\s*"200"'])
    _single_value(fraction, 'logged_success_fraction', 0.15, 0.25)
    assert report['sample_every'] == {'success': 5, 'error': 1}, 'sample_every: read the sample_every field of an info record and of an error record'
    live = _shop_records()
    assert {record['sample_every'] for record in live if record['level'] == 'info'} == {5}, 'the log has changed; check sample_every again'


def _check_sensitive(report):
    assert report['sensitive_field'] == 'email', 'sensitive_field must name the log field that holds personal data'


def _check_metric_error_ratio(report, key):
    ratio = _live_result(report, key, [r'(?<![a-z])rate\(', r'shop_http_requests_total', r'status\s*=\s*"500"'])
    _single_value(ratio, key, 0.10, 0.24)


def _lab_checks():
    report = json.loads(get('configmap', 'evidence')['data']['report.json'])
    _check_sampling(report)
    _check_sensitive(report)
    _check_metric_error_ratio(report, 'error_ratio')
    share = report['log_error_share']
    errors, total = share['errors'], share['total']
    assert isinstance(errors, int) and isinstance(total, int) and total >= 20, 'log_error_share: count at least 20 request records'
    live = _shop_records()
    assert errors <= sum(1 for record in live if record['level'] == 'error') and total <= len(live), 'log_error_share: the counts are larger than the log holds'
    assert 0.35 <= errors / total <= 0.65, 'log_error_share: the share of error records is outside the range the sampling produces'


_lab_checks()
