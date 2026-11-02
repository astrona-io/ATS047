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

recorded=json.loads(obj("configmap","evidence")["data"]["report.json"])
response=recorded['response'];event=recorded['event']
assert event['request_id']==response['request_id'] and response['traceparent']=='00-0123456789abcdef0123456789abcdef-0123456789abcdef-01'
assert event['status']==200 and event['duration_seconds']>0
logs=call('kubectl','-n','starfleet','logs','deployment/probe','--since=5m')
assert event in [json.loads(line) for line in logs.splitlines()], 'Recorded request log no longer exists'
