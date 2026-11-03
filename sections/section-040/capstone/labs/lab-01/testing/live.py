# Live checks for the pull versus push capstone. check.py runs this file
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
    assert re.search(r'honor_labels:\s*true', config), 'The pushgateway scrape job must set honor_labels: true'
    assert 'remote_write:' in config and 'http://receiver:9090/api/v1/write' in config, 'prometheus-config must send remote write to the receiver'
    gateway = _in_cluster('http://pushgateway:9091/metrics')
    for stale in ('old_export', 'legacy_sync'):
        assert 'job="%s"' % stale not in gateway, 'The group %s must be deleted from the Pushgateway' % stale
    assert re.search(r'^lab_batch_last_success_timestamp_seconds\{[^}]*job="nightly_report"[^}]*\} ', gateway, re.M), 'The Pushgateway holds no fresh nightly_report group'
    report = json.loads(get('configmap', 'evidence')['data']['report.json'])
    receiver = 'http://receiver:9090'
    local = 'http://prometheus:9090'
    _checked_query(report, 'groups', local, [r'lab_batch_last_success_timestamp_seconds', r'count'], 1, 1, 1)
    assert re.search(r'job', report['groups']['expression']), 'groups: aggregate by the job label'
    assert report['groups']['data']['result'][0]['metric'].get('job') == 'nightly_report', 'groups: the only remaining job must be nightly_report'
    _checked_query(report, 'batch_age', local, [r'time\(\)', r'lab_batch_last_success_timestamp_seconds', r'job\s*=\s*"nightly_report"'], 1, 0, 900)
    _checked_query(report, 'downstream', receiver, [r'lab_batch_last_success_timestamp_seconds', r'job\s*=\s*"nightly_report"'], 1, 1e9, 1e11)


_lab_checks()
