#!/usr/bin/env bash
# Check: every target of the job pods has namespace, pod and app with the right values.
set -uo pipefail
if [[ "$(kubectl config current-context)" != "kind-astro-ats-047-capstone-050" ]]; then
  echo "FAIL: wrong Kubernetes context" >&2
  exit 1
fi
prom_get() {
  kubectl -n starfleet exec shuttle -- python -c 'import sys, urllib.request
print(urllib.request.urlopen("http://prometheus:9090" + sys.argv[1], timeout=8).read().decode())' "$1"
}
for attempt in $(seq 1 12); do
  if prom_get '/api/v1/targets' | python3 -c 'import json, sys
targets = [t for t in json.load(sys.stdin)["data"]["activeTargets"] if t["scrapePool"] == "pods"]
assert targets
for target in targets:
    found = target["discoveredLabels"]
    labels = target["labels"]
    assert labels.get("namespace") == found["__meta_kubernetes_namespace"]
    assert labels.get("pod") == found["__meta_kubernetes_pod_name"]
    assert labels.get("app") == found["__meta_kubernetes_pod_label_app"]' 2>/dev/null; then
    echo "PASS: namespace, pod and app labels are set on every target"
    exit 0
  fi
  sleep 5
done
echo "FAIL: each target needs the labels namespace, pod and app copied from the pod metadata"
exit 1
