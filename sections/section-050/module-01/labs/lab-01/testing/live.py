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
import urllib.parse
assert recorded['expression']=='count by (job,team) (up{job="probe"})'
assert 0 <= time.time()-float(recorded['evaluated_at']) <= 300, 'Refresh evidence within five minutes'
answer=api('/api/v1/query?'+urllib.parse.urlencode({'query':recorded['expression'],'time':recorded['evaluated_at']}))
assert answer['status']=='success' and answer['data']['result'], 'Required series are absent'
assert recorded['data']==answer['data'], 'Query evidence differs'
