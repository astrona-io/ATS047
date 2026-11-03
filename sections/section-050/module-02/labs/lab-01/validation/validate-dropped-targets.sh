#!/usr/bin/env bash
# Check: pods other than probe and scout are dropped targets and have no up series.
set -uo pipefail
if [[ "$(kubectl config current-context)" != "kind-astro-ats-047-lab-050-02-01" ]]; then
  echo "FAIL: wrong Kubernetes context" >&2
  exit 1
fi
prom_get() {
  kubectl -n starfleet exec shuttle -- python -c 'import sys, urllib.request
print(urllib.request.urlopen("http://prometheus:9090" + sys.argv[1], timeout=8).read().decode())' "$1"
}
for attempt in $(seq 1 12); do
  if prom_get '/api/v1/targets?state=any' | python3 -c 'import json, sys
data = json.load(sys.stdin)["data"]
dropped = {t["discoveredLabels"].get("__meta_kubernetes_pod_name", "") for t in data["droppedTargets"] if t.get("scrapePool") == "pods"}
active = {t["discoveredLabels"].get("__meta_kubernetes_pod_name", "") for t in data["activeTargets"] if t.get("scrapePool") == "pods"}
assert "shuttle" in dropped and "drifter" in dropped
assert not any(name.startswith(("shuttle", "drifter", "traffic", "prometheus")) for name in active)' 2>/dev/null; then
    echo "PASS: the other pods are dropped and not scraped"
    exit 0
  fi
  sleep 5
done
echo "FAIL: shuttle, traffic, drifter and prometheus pods must be dropped by the keep rule"
exit 1
