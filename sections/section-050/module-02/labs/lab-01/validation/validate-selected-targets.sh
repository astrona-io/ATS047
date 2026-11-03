#!/usr/bin/env bash
# Check: active targets of the job pods are exactly the probe and scout pods, all up.
set -uo pipefail
if [[ "$(kubectl config current-context)" != "kind-astro-ats-047-lab-050-02-01" ]]; then
  echo "FAIL: wrong Kubernetes context" >&2
  exit 1
fi
prom_get() {
  kubectl -n starfleet exec shuttle -- python -c 'import sys, urllib.request
print(urllib.request.urlopen("http://prometheus:9090" + sys.argv[1], timeout=8).read().decode())' "$1"
}
expected="$(kubectl -n starfleet get pods -l 'app in (probe,scout)' -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}' | sort)"
for attempt in $(seq 1 12); do
  found="$(prom_get '/api/v1/targets' | python3 -c 'import json, sys
targets = json.load(sys.stdin)["data"]["activeTargets"]
rows = []
for target in targets:
    if target["scrapePool"] == "pods":
        pod = target["discoveredLabels"].get("__meta_kubernetes_pod_name", "?")
        rows.append(pod if target["health"] == "up" else pod + ":" + target["health"])
print("\n".join(sorted(rows)))' 2>/dev/null)"
  if [ -n "$found" ] && [ "$found" = "$expected" ]; then
    echo "PASS: the job pods scrapes exactly the probe and scout pods and all are up"
    exit 0
  fi
  sleep 5
done
echo "FAIL: active targets do not match the probe and scout pods. Found: $(echo "$found" | tr '\n' ' ')"
exit 1
