import json, os, subprocess, tempfile, time, urllib.parse


def call(*args):
    result = subprocess.run(list(args), text=True, capture_output=True, timeout=20)
    assert result.returncode == 0, 'Observation command failed: ' + args[0]
    return result.stdout.strip()


def in_cluster(url):
    script = 'import urllib.request; print(urllib.request.urlopen(%r, timeout=8).read().decode())' % url
    return call('kubectl', '-n', 'starfleet', 'exec', 'shuttle', '--', 'python', '-c', script)


def query(expression, when):
    return json.loads(in_cluster('http://prometheus:9090/api/v1/query?' + urllib.parse.urlencode({'query': expression, 'time': when})))


assert call('kubectl', 'config', 'current-context') == 'kind-astro-ats-047-lab-010-02-01'
now = time.time()
expressions = {
    'cardinality': 'count by (__name__) ({job="shop"})',
    'fleet_route_rate': 'sum by (route) (rate(shop_http_requests_total[1m]))',
    'fleet_error_ratio': 'sum(rate(shop_http_requests_total{status="500"}[1m])) / sum(rate(shop_http_requests_total[1m]))',
}
report = {'unbounded_label': 'user_id'}
for key, expression in expressions.items():
    answer = query(expression, now)
    assert answer['status'] == 'success' and answer['data']['result'], 'Wait for enough scrapes'
    report[key] = {'expression': expression, 'evaluated_at': now, 'data': answer['data']}
resource = {'apiVersion': 'v1', 'kind': 'ConfigMap', 'metadata': {'name': 'evidence', 'namespace': 'starfleet'}, 'data': {'report.json': json.dumps(report, sort_keys=True)}}
with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as handle:
    json.dump(resource, handle)
    path = handle.name
call('kubectl', 'apply', '-f', path)
os.unlink(path)
