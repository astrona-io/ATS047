#!/usr/bin/env bash
# Check: the job pods discovered every starfleet pod and no pod of another namespace.
set -uo pipefail
if [[ "$(kubectl config current-context)" != "kind-astro-ats-047-lab-050-01-01" ]]; then
  echo "FAIL: wrong Kubernetes context" >&2
  exit 1
fi
prom_get() {
  kubectl -n starfleet exec shuttle -- python -c 'import sys, urllib.parse, urllib.request
url = "http://prometheus:9090" + sys.argv[1]
print(urllib.request.urlopen(url, timeout=8).read().decode())' "$1"
}
expected="$(kubectl -n starfleet get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}' | sort)"
for attempt in $(seq 1 12); do
  found="$(prom_get '/api/v1/targets?state=any' | python3 -c 'import json, sys
data = json.load(sys.stdin)["data"]
names = set()
for target in data["activeTargets"] + data["droppedTargets"]:
    labels = target["discoveredLabels"]
    if target.get("scrapePool") == "pods" or labels.get("job") == "pods":
        names.add(labels.get("__meta_kubernetes_namespace", "?") + "/" + labels.get("__meta_kubernetes_pod_name", "?"))
print("\n".join(sorted(names)))' 2>/dev/null)"
  wanted="$(echo "$expected" | sed 's|^|starfleet/|' | sort)"
  if [ -n "$found" ] && [ "$found" = "$wanted" ]; then
    echo "PASS: the job pods discovered exactly the pods of starfleet"
    exit 0
  fi
  sleep 5
done
echo "FAIL: discovered pods differ from the pods of starfleet. Found: $(echo "$found" | tr '\n' ' ')"
exit 1
