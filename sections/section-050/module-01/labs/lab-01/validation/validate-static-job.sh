#!/usr/bin/env bash
# Check: the static probe job still has an active target that is up.
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
for attempt in $(seq 1 12); do
  if prom_get '/api/v1/targets' | python3 -c 'import json, sys
targets = json.load(sys.stdin)["data"]["activeTargets"]
jobs = {t["labels"]["job"]: t["health"] for t in targets if t["labels"]["job"] in ("probe", "prometheus")}
assert jobs.get("probe") == "up" and jobs.get("prometheus") == "up"' 2>/dev/null; then
    echo "PASS: the static jobs prometheus and probe are up"
    exit 0
  fi
  sleep 5
done
echo "FAIL: the static jobs prometheus and probe must stay and be up"
exit 1
