---
draft: true
exam_objectives:
- Understand logs and events
---
# Guided Practice: Correlate A Request Log With Its Response

Use a host shell with the private kubeconfig for this module playground. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

<!-- astrona:playground:renew -->

```sh
export KUBECONFIG="$(astrona kubeconfig ats-047-playground-020-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-047-playground-020-01" || exit 1
node_name="astro-ats-047-playground-020-01-control-plane"
worker_name="astro-ats-047-playground-020-01-worker"
```

Keep this connection selected. Host-level commands name only this environment's node containers. They do not operate on the host operating system.

## Inspect And Explain

One instrumented probe serves metrics and structured request logs. A traffic generator makes ten percent of requests fail. Prometheus scrapes every two seconds; no evidence report or learner rule exists.

Inspect the current objects before changing them:

```sh
kubectl -n starfleet get pods -o wide
kubectl get nodes -o wide
```

Record `response` and `event` objects. Use request_id to correlate a single response and log, rather than placing unbounded identifiers in metrics. For trace practice send the provided W3C traceparent header. This lightweight fixture demonstrates context propagation and a timed operation; it does not run a tracing backend or claim a distributed trace.

Record observations in `starfleet/evidence`, whose `report.json` contains the stated report. The verifier reads the live API again; invented values do not pass.


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

assert call('kubectl','config','current-context') == 'kind-astro-ats-047-playground-020-01'
script="import urllib.request,json; r=urllib.request.Request('http://probe:8080/work',headers={'traceparent':'none'}); print(urllib.request.urlopen(r,timeout=5).read().decode())"
response=json.loads(call('kubectl','-n','starfleet','exec','shuttle','--','python','-c',script))
logs=call('kubectl','-n','starfleet','logs','deployment/probe','--tail=100')
event=next(json.loads(line) for line in logs.splitlines() if json.loads(line).get('request_id')==response['request_id'])
report={'response':response,'event':event}
save(report)
```

Apply the scoped correction:

```sh
python3 record.py
```

## Verify The Result

Observe the actual result. A denied request returns a nonzero status when the denial works, so run it separately from a shell sequence that stops on error. Status convergence and a successful request establish different parts of the result.

```sh
kubectl -n starfleet get configmaps
kubectl -n starfleet get deployment probe -o yaml
```

Produce one real request and correlate its response with the structured completion record. The commands above deliberately target one environment. Keep its remaining components available so an unrelated failure cannot stand in for the required denial or correction. No example command output is presented as evidence of a completed run. A matching field alone does not establish that a process used it or that a controller reconciled it.


## Common pitfalls

> [!WARNING]
> Confirm the private context and exact node names before a change. Check the stated scope and live result. Do not change unrelated components to hide the original fault.
