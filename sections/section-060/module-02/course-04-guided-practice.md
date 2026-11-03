---
draft: true
exam_objectives:
- Basics of SLOs, SLAs, and SLIs
---
# Guided Practice: Record The Error Budget Burn Rate

In this practice you measure how fast a service uses its error budget and record the result as evidence. The `probe` Service in `starfleet` handles requests from a traffic generator, and one request in ten fails with status 500. The objective is 99 percent successful requests, so the error budget is 1 percent of requests. Prometheus scrapes the probe every two seconds.

Use a host shell with the private kubeconfig for this module playground. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

<!-- astrona:playground:renew -->

```sh
export KUBECONFIG="$(astrona kubeconfig ats-047-playground-060-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-047-playground-060-02" || exit 1
node_name="astro-ats-047-playground-060-02-control-plane"
worker_name="astro-ats-047-playground-060-02-worker"
```

Keep this connection selected. Host-level commands name only this environment's node containers. They do not operate on the host operating system.

## Inspect The Environment

Look at the objects first. The `probe` Deployment serves requests, the `traffic` Deployment sends them, the `prometheus` Deployment scrapes the probe, and the `shuttle` pod is the client that sends requests to the Prometheus API.

```sh
kubectl -n starfleet get pods -o wide
kubectl get nodes -o wide
```

All pods in `starfleet` should be `Running`. If one is not ready, wait and run the first command again.

## Think Through The Numbers

Before you query anything, calculate the expected result by hand. One request in ten fails, so the error ratio is 0.1. The 99 percent objective allows an error ratio of 0.01, which is one minus 0.99. The burn rate is 0.1 divided by 0.01, so it is about 10.

At a burn rate of 10, a 30 day budget lasts 30 days divided by 10, which is 3 days. If the query returns a value far from 10, the cause is usually too few samples in the range or a changed traffic pattern, so check the numerator and the denominator separately.

## Calculate The Burn Rate

The report needs the expression `(sum(rate(lab_requests_total{status="500"}[20s])) / sum(rate(lab_requests_total[20s]))) / (1 - 0.99)`. It divides the error ratio over a 20 second range by the allowed error ratio. Wait at least 20 seconds after the playground starts, because a rate needs several samples in its range.

The report has three fields: `expression`, `evaluated_at` and `data`. The field `data` is the whole `data` object that the Prometheus API returns, not only the printed value. The script below queries Prometheus through the `shuttle` pod and stores the report in the ConfigMap `evidence` in `starfleet`, under the key `report.json`. The verifier reads the live API again, so invented values do not pass.

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

assert call('kubectl','config','current-context') == 'kind-astro-ats-047-playground-060-02'
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

If the script stops with "Wait for enough scrapes", Prometheus has too few samples. Wait 20 seconds and run it again.

## Verify The Result

Check that the evidence object exists and that the probe still runs unchanged. These commands read objects and change nothing.

```sh
kubectl -n starfleet get configmaps
kubectl -n starfleet get configmap evidence -o yaml
```

The ConfigMap list includes `evidence`, and the `report.json` key holds the three fields. The recorded `data` must match what Prometheus returns for the same expression and evaluation time. The evaluation time must be less than five minutes old when you submit. The burn rate value must lie between 5 and 15, which fits a 10 percent error ratio and a 99 percent objective.

## Common pitfalls

> [!WARNING]
> Confirm the private context before you run a command, because a wrong context changes a different cluster. A changed expression fails the check even when its value is the same. Evidence older than five minutes fails, so record it again before you submit. A missing parenthesis changes the order of the division and the value.
