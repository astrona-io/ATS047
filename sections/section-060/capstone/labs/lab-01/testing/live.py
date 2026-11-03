import json
import subprocess
import time
import urllib.parse


def call(*args):
    result = subprocess.run(list(args), text=True, capture_output=True, timeout=20)
    assert result.returncode == 0, 'Observation command failed: ' + args[0]
    return result.stdout.strip()


def api(path):
    script = 'import urllib.request; print(urllib.request.urlopen(' + repr('http://prometheus:9090' + path) + ',timeout=8).read().decode())'
    return json.loads(call('kubectl', '-n', 'starfleet', 'exec', 'shuttle', '--', 'python', '-c', script))


def rules_by_name():
    answer = api('/api/v1/rules')
    assert answer['status'] == 'success', 'The rules API did not answer'
    found = {}
    for group in answer['data']['groups']:
        for rule in group['rules']:
            found[rule['name']] = rule
    return found


def instant_value(name):
    answer = api('/api/v1/query?' + urllib.parse.urlencode({'query': name}))
    assert answer['status'] == 'success' and answer['data']['result'], 'No series for ' + name
    return float(answer['data']['result'][0]['value'][1])


RATIO = 'sli:request_error_ratio:rate20s'
BURN = 'slo:error_budget_burn_rate:rate20s'
ALERT = 'ErrorBudgetFastBurn'

rules = rules_by_name()
for name in (RATIO, BURN):
    assert name in rules, 'Recording rule is missing: ' + name
    assert rules[name]['type'] == 'recording', name + ' must be a recording rule'
    assert rules[name]['health'] == 'ok', name + ' does not evaluate without error'
assert 'lab_requests_total' in rules[RATIO]['query'], 'The ratio rule must use lab_requests_total'
assert RATIO in rules[BURN]['query'], 'The burn rate rule must build on the ratio rule'
assert ALERT in rules, 'Alerting rule is missing'
alert_rule = rules[ALERT]
assert alert_rule['type'] == 'alerting', ALERT + ' must be an alerting rule'
assert BURN in alert_rule['query'], 'The alert must use the burn rate rule'
assert alert_rule['labels'].get('severity') == 'page', 'The alert needs the label severity="page"'
assert 5 <= alert_rule['duration'] <= 60, 'The alert for duration must be between 5 and 60 seconds'
assert 'summary' in alert_rule.get('annotations', {}), 'The alert needs a summary annotation'

assert 0.05 <= instant_value(RATIO) <= 0.15, 'The error ratio is outside the expected range'
assert 5 <= instant_value(BURN) <= 15, 'The burn rate is outside the expected range'

firing = False
for attempt in range(10):
    alerts = api('/api/v1/alerts')['data']['alerts']
    firing = any(a['labels'].get('alertname') == ALERT and a['state'] == 'firing' for a in alerts)
    if firing:
        break
    time.sleep(4)
assert firing, 'The alert is not firing although the burn rate is above its threshold'
