import json, os, subprocess, tempfile, time, urllib.parse


def call(*args):
    result = subprocess.run(list(args), text=True, capture_output=True, timeout=20)
    assert result.returncode == 0, 'Observation command failed: ' + args[0]
    return result.stdout.strip()


def in_cluster(script, *arguments):
    return call('kubectl', '-n', 'starfleet', 'exec', 'shuttle', '--', 'python', '-c', script, *arguments)


def query(expression, when):
    script = 'import sys, urllib.request; print(urllib.request.urlopen(sys.argv[1], timeout=8).read().decode())'
    url = 'http://prometheus:9090/api/v1/query?' + urllib.parse.urlencode({'query': expression, 'time': when})
    return json.loads(in_cluster(script, url))


def result(expression, when):
    answer = query(expression, when)
    assert answer['status'] == 'success' and answer['data']['result'], 'Wait for enough scrapes'
    return {'expression': expression, 'evaluated_at': when, 'data': answer['data']}


def send_request(path):
    script = (
        'import sys, urllib.error, urllib.request\n'
        'try:\n'
        '    print(urllib.request.urlopen(sys.argv[1], timeout=8).read().decode())\n'
        'except urllib.error.HTTPError as error:\n'
        '    print(error.read().decode())\n'
    )
    return json.loads(in_cluster(script, 'http://shop:8080' + path))


def shop_records(lines=500):
    records = []
    for line in call('kubectl', '-n', 'starfleet', 'logs', 'deployment/shop', '--tail=%d' % lines).splitlines():
        try:
            record = json.loads(line)
        except ValueError:
            continue
        if record.get('message') == 'request completed':
            records.append(record)
    return records


def save(report):
    resource = {'apiVersion': 'v1', 'kind': 'ConfigMap', 'metadata': {'name': 'evidence', 'namespace': 'starfleet'}, 'data': {'report.json': json.dumps(report, sort_keys=True)}}
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as handle:
        json.dump(resource, handle)
        path = handle.name
    call('kubectl', 'apply', '-f', path)
    os.unlink(path)


assert call('kubectl', 'config', 'current-context') == 'kind-astro-ats-047-lab-020-capstone-01'

response = send_request('/work?route=/checkout&status=500&user=%USER%')
record = next(item for item in shop_records() if item['request_id'] == response['request_id'])

now = time.time()
failing_routes = result('sum by (route) (rate(shop_http_requests_total{status="500"}[1m]))', now)

fraction = result('sum(shop_log_records_total{level="info"}) / sum(shop_http_requests_total{status="200"})', now)
live = shop_records()
sample_every = {
    'success': next(item['sample_every'] for item in live if item['level'] == 'info'),
    'error': next(item['sample_every'] for item in live if item['level'] == 'error'),
}

error_ratio = result('sum(rate(shop_http_requests_total{status="500"}[1m])) / sum(rate(shop_http_requests_total[1m]))', now)

pod = json.loads(call('kubectl', '-n', 'starfleet', 'get', 'pods', '-l', 'app=shop', '-o', 'json'))['items'][0]['metadata']['name']
events = json.loads(call('kubectl', '-n', 'starfleet', 'get', 'events', '-o', 'json'))['items']
started = next(item for item in events if item['involvedObject']['name'] == pod and item['reason'] == 'Started')
save({
    'response': response,
    'record': record,
    'failing_routes': failing_routes,
    'logged_success_fraction': fraction,
    'sample_every': sample_every,
    'sensitive_field': 'email',
    'error_ratio': error_ratio,
    'event': {'pod': pod, 'reason': started['reason'], 'uid': started['metadata']['uid']},
})
