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

assert call('kubectl','config','current-context') == 'kind-astro-ats-047-lab-030-01-01'
script="import urllib.request,json; r=urllib.request.Request('http://probe:8080/work',headers={'traceparent':'00-0123456789abcdef0123456789abcdef-0123456789abcdef-01'}); print(urllib.request.urlopen(r,timeout=5).read().decode())"
response=json.loads(call('kubectl','-n','starfleet','exec','shuttle','--','python','-c',script))
logs=call('kubectl','-n','starfleet','logs','deployment/probe','--tail=100')
event=next(json.loads(line) for line in logs.splitlines() if json.loads(line).get('request_id')==response['request_id'])
report={'response':response,'event':event}
save(report)
