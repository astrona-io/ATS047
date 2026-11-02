---
draft: true
exam_objectives:
- Push vs Pull
---
# Guided Practice: Observe A Pulled Target

Use a host shell with the private kubeconfig for this module playground. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

<!-- astrona:playground:renew -->

```sh
export KUBECONFIG="$(astrona kubeconfig ats-047-playground-040-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-047-playground-040-01" || exit 1
node_name="astro-ats-047-playground-040-01-control-plane"
worker_name="astro-ats-047-playground-040-01-worker"
```

Keep this connection selected. Host-level commands name only this environment's node containers. They do not operate on the host operating system.

## Inspect And Explain

One instrumented probe serves metrics and structured request logs. A traffic generator makes ten percent of requests fail. Prometheus scrapes every two seconds; no evidence report or learner rule exists.

Inspect the current objects before changing them:

```sh
kubectl -n starfleet get pods -o wide
kubectl get nodes -o wide
```

Prometheus owns scrape timing. Inspect target health before interpreting application samples; this exercise observes pull collection, while Pushgateway lifetime is discussed in the reading.

Use the expression `up{job="probe"}`. The report needs `expression`, `evaluated_at` and `data`. Data is the Prometheus API data object, not only the printed value. Wait for at least twenty seconds of collected traffic before using a rate. Record evidence within five minutes of submission. Changing the expression or claiming an empty result fails.

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

assert call('kubectl','config','current-context') == 'kind-astro-ats-047-playground-040-01'
import urllib.parse
stamp=time.time()
expression='up{job="probe"}'
answer=api('/api/v1/query?'+urllib.parse.urlencode({'query':expression,'time':stamp}))
assert answer['status']=='success' and answer['data']['result'], 'Wait for enough scrapes'
report={'expression':expression,'evaluated_at':stamp,'data':answer['data']}
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

Evaluate the required expression and preserve its labels, values and evaluation time. The commands above deliberately target one environment. Keep its remaining components available so an unrelated failure cannot stand in for the required denial or correction. No example command output is presented as evidence of a completed run. A matching field alone does not establish that a process used it or that a controller reconciled it.


## Common pitfalls

> [!WARNING]
> Confirm the private context and exact node names before a change. Check the stated scope and live result. Do not change unrelated components to hide the original fault.
