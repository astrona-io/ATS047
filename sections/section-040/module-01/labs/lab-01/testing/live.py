# Live checks for the Pushgateway lab. check.py runs this file with exec(),
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


def _checked_query(report, key, required_patterns, low, high):
    item = report[key]
    expression = item['expression']
    assert isinstance(expression, str), key + ': the expression must be a string'
    assert 0 <= time.time() - float(item['evaluated_at']) <= 300, key + ': refresh the evidence within five minutes'
    for pattern in required_patterns:
        assert re.search(pattern, expression), key + ': the expression does not use the required series'
    live = _prometheus(expression, item['evaluated_at'])
    assert live['status'] == 'success', key + ': Prometheus rejected the expression'
    assert item['data'] == live['data'], key + ': the recorded data differs from what Prometheus returns'
    result = live['data']['result']
    assert live['data']['resultType'] == 'vector' and len(result) == 1, key + ': the expression must return exactly one series'
    value = float(result[0]['value'][1])
    assert low <= value <= high, key + ': the value is outside the expected range'


def _lab_checks():
    gateway = _in_cluster('http://pushgateway:9091/metrics')
    assert re.search(r'^lab_batch_records_processed\{[^}]*job="nightly_report"[^}]*\} 42$', gateway, re.M), 'The Pushgateway holds no group job=nightly_report with 42 records'
    config = command(['kubectl', '-n', 'starfleet', 'get', 'configmap', 'prometheus-config', '-o', 'jsonpath={.data.prometheus\\.yaml}']).stdout
    assert re.search(r'honor_labels:\s*true', config), 'The pushgateway scrape job must set honor_labels: true'
    report = json.loads(get('configmap', 'evidence')['data']['report.json'])
    _checked_query(report, 'batch_records', [r'lab_batch_records_processed', r'job\s*=\s*"nightly_report"'], 42, 42)
    _checked_query(report, 'batch_age', [r'time\(\)', r'lab_batch_last_success_timestamp_seconds', r'job\s*=\s*"nightly_report"'], 0, 900)
    _checked_query(report, 'gateway_up', [r'\bup\b', r'job\s*=\s*"pushgateway"'], 1, 1)


_lab_checks()
