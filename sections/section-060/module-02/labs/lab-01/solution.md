---
draft: true
exam_objectives:
- Basics of SLOs, SLAs, and SLIs
---
# Calculate The Error Budget Burn Rate Solution

This walkthrough calculates the burn rate and records it as the task requires.

## Connect to the lab

```sh
export KUBECONFIG="$(astrona kubeconfig ats-047-lab-060-02-01)"
test "$(kubectl config current-context)" = "kind-ats-047-lab-060-02-01" || exit 1
```

Keep this connection selected.

## Inspect the starting state

Check that all pods run before you query Prometheus.

```sh
kubectl -n starfleet get pods -o wide
```

The pods `probe`, `traffic`, `prometheus` and `shuttle` run in `starfleet`. The `shuttle` pod is the client that sends requests to the Prometheus API, because the Prometheus Service is only reachable inside the cluster.

## Calculate and record the burn rate

One request in ten fails, so the error ratio is 0.1. The 99 percent objective allows 0.01. The burn rate is 0.1 divided by 0.01, which is about 10. The expression below calculates the same value from the counters.

Save this as `record.py`:

```python
import json,subprocess,time,sys,tempfile,os

def call(*args):
 r=subprocess.run(list(args),text=True,capture_output=True,timeout=20)
 assert r.returncode==0, 'Observation command failed: '+args[0]
 return r.stdout.strip()
def obj(kind,name,ns='starfleet'):
 return json.loads(call('kubectl',*(['-n',ns] if ns else []),'get',kind,name,'-o','json'))
def api(path):
 script='import urllib.request; print(urllib.request.urlopen('+repr('http://prometheus:9090'+path)+',timeout=8).read().decode())'
 return json.loads(call('kubectl','-n','starfleet','exec','shuttle','--','python','-c',script))
def save(data):
 resource={'apiVersion':'v1','kind':'ConfigMap','metadata':{'name':'evidence','namespace':'starfleet'},'data':{'report.json':json.dumps(data,sort_keys=True)}}
 with tempfile.NamedTemporaryFile(mode='w',suffix='.json',delete=False) as f:json.dump(resource,f);path=f.name
 try:call('kubectl','apply','-f',path)
 finally:os.unlink(path)

assert call('kubectl','config','current-context') == 'kind-astro-ats-047-lab-060-02-01'
import urllib.parse
stamp=time.time()
expression='(sum(rate(lab_requests_total{status="500"}[20s])) / sum(rate(lab_requests_total[20s]))) / (1 - 0.99)'
answer=api('/api/v1/query?'+urllib.parse.urlencode({'query':expression,'time':stamp}))
assert answer['status']=='success' and answer['data']['result'], 'Wait for enough scrapes'
report={'expression':expression,'evaluated_at':stamp,'data':answer['data']}
save(report)
```

Run it:

```sh
python3 record.py
```

If it stops with "Wait for enough scrapes", wait 20 seconds and run it again.

## Check the result

```sh
kubectl -n starfleet get configmap evidence -o yaml
```

The ConfigMap holds `report.json` with the three fields. Submit within five minutes, or run `record.py` again to refresh the evaluation time.

After recording your result, remove the independent lab with `astrona destroy ats-047-lab-060-02-01`.

## Common pitfalls

> [!WARNING]
> A changed expression fails the check even when the value is the same. A missing parenthesis changes the order of the division and the value, and the grader rejects values outside 5 to 15. Old evidence fails, so refresh it before you submit.
