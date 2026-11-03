---
draft: true
exam_objectives:
- Basics of SLOs, SLAs, and SLIs
---
# Guided Practice: Calculate A Traffic Weighted Error Ratio

In this practice you measure the SLI of a running service, compare it with a 99 percent objective and record the result as evidence. The `probe` Service in `starfleet` handles requests from a traffic generator, and one request in ten fails with status 500. Prometheus scrapes the probe every two seconds.

Use a host shell with the private kubeconfig for this module playground. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

<!-- astrona:playground:renew -->

```sh
export KUBECONFIG="$(astrona kubeconfig ats-047-playground-060-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-047-playground-060-01" || exit 1
node_name="astro-ats-047-playground-060-01-control-plane"
worker_name="astro-ats-047-playground-060-01-worker"
```

Keep this connection selected. Host-level commands name only this environment's node containers. They do not operate on the host operating system.

## Inspect The Environment

Look at the objects first, so you know which component does which job. The `probe` Deployment serves requests, the `traffic` Deployment sends them, the `prometheus` Deployment scrapes the probe, and the `shuttle` pod is a client from which you query the Prometheus API.

```sh
kubectl -n starfleet get pods -o wide
kubectl get nodes -o wide
```

All pods in `starfleet` should be `Running`. If a pod is not ready yet, wait and run the first command again.

## Read The Raw Counter

An SLI starts with event counts. The probe exposes its counters in the Prometheus text format on `/metrics`. The `shuttle` pod requests that page from the `probe` Service.

```sh
kubectl -n starfleet exec shuttle -- python -c "import urllib.request; print(urllib.request.urlopen('http://probe:8080/metrics', timeout=8).read().decode())"
```

The page holds the series `lab_requests_total` with `status="200"` and `status="500"`, a duration histogram and two gauges. The two counters only grow. The ratio of the status 500 counter to the sum of both counters is the share of bad events over the life of the process.

## Calculate The SLI And The Budget

A rate over a short range gives the current share of bad events. The report you record needs the expression `sum(rate(lab_requests_total{status="500"}[20s])) / sum(rate(lab_requests_total[20s]))`. Wait at least 20 seconds after the playground starts before you use a rate, because a rate needs several samples in its range.

Compare the value with the objective. A 99 percent success objective allows a bad share of 0.01. A value near 0.1 is ten times that allowance, so the objective is missed by a wide margin. The error budget of this objective is 1 percent of requests, and the next module explains how to track it. An SLA is a separate agreement, and no contract decision is graded here.

## Record The Evidence

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

assert call('kubectl','config','current-context') == 'kind-astro-ats-047-playground-060-01'
import urllib.parse
stamp=time.time()
expression='sum(rate(lab_requests_total{status="500"}[20s])) / sum(rate(lab_requests_total[20s]))'
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

Check that the evidence object exists and that the probe still runs unchanged. The commands read objects and change nothing.

```sh
kubectl -n starfleet get configmaps
kubectl -n starfleet get deployment probe -o yaml
```

The ConfigMap list includes `evidence`. The `probe` Deployment keeps one replica. The recorded `data` must match what Prometheus returns for the same expression and evaluation time, and the evaluation time must be less than five minutes old when you submit.

## Common pitfalls

> [!WARNING]
> Confirm the private context before you run a command, because a wrong context changes a different cluster. A changed expression fails the check even when its value is the same. Evidence older than five minutes fails, so record it again before you submit. Do not change the `probe` or `traffic` Deployments to make the number look better.
