# Live checks for the remote write and staleness lab. check.py runs this file
# with exec(), so the helpers command(), kubectl() and get() from check.py are available.
import json
import re
import time
import urllib.parse


def _in_cluster(url):
    script = 'import urllib.request; print(urllib.request.urlopen(%r, timeout=8).read().decode())' % url
    return command(['kubectl', '-n', 'starfleet', 'exec', 'shuttle', '--', 'python', '-c', script]).stdout


def _prometheus(base, expression, when):
    query = urllib.parse.urlencode({'query': expression, 'time': when})
    return json.loads(_in_cluster(base + '/api/v1/query?' + query))


def _checked_query(report, key, base, required_patterns, count, low=None, high=None):
    item = report[key]
    expression = item['expression']
    assert isinstance(expression, str), key + ': the expression must be a string'
    assert 0 <= time.time() - float(item['evaluated_at']) <= 300, key + ': refresh the evidence within five minutes'
    for pattern in required_patterns:
        assert re.search(pattern, expression), key + ': the expression does not use the required series'
    live = _prometheus(base, expression, item['evaluated_at'])
    assert live['status'] == 'success', key + ': Prometheus rejected the expression'
    assert item['data'] == live['data'], key + ': the recorded data differs from what Prometheus returns'
    result = live['data']['result']
    assert live['data']['resultType'] == 'vector' and len(result) == count, key + ': the expression returned the wrong number of series'
    if count == 1:
        value = float(result[0]['value'][1])
        assert low <= value <= high, key + ': the value is outside the expected range'


def _lab_checks():
    config = command(['kubectl', '-n', 'starfleet', 'get', 'configmap', 'prometheus-config', '-o', 'jsonpath={.data.prometheus\\.yaml}']).stdout
    assert re.search(r'remote_write:', config) and 'http://receiver:9090/api/v1/write' in config, 'prometheus-config must send remote write to the receiver'
    gateway = _in_cluster('http://pushgateway:9091/metrics')
    assert 'job="temp_export"' not in gateway, 'The temp_export group must be deleted from the Pushgateway'
    report = json.loads(get('configmap', 'evidence')['data']['report.json'])
    receiver = 'http://receiver:9090'
    local = 'http://prometheus:9090'
    _checked_query(report, 'receiver_probe', receiver, [r'\bup\b', r'job\s*=\s*"probe"'], 1, 1, 1)
    _checked_query(report, 'samples_sent', local, [r'prometheus_remote_storage_samples_total'], 1, 1, 1e12)
    _checked_query(report, 'instant_after_delete', local, [r'lab_temp_value', r'job\s*=\s*"temp_export"'], 0)
    assert 'count_over_time' not in report['instant_after_delete']['expression'], 'instant_after_delete must be a plain selector'
    _checked_query(report, 'history_kept', local, [r'count_over_time\(', r'lab_temp_value', r'job\s*=\s*"temp_export"'], 1, 1, 1e6)


_lab_checks()
