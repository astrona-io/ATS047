#!/usr/bin/env bash
# Check: lab_queue_depth is not stored for the job pods; lab_requests_total is, for probe and scout.
set -uo pipefail
if [[ "$(kubectl config current-context)" != "kind-astro-ats-047-capstone-050" ]]; then
  echo "FAIL: wrong Kubernetes context" >&2
  exit 1
fi
prom_get() {
  kubectl -n starfleet exec shuttle -- python -c 'import sys, urllib.request
print(urllib.request.urlopen("http://prometheus:9090" + sys.argv[1], timeout=8).read().decode())' "$1"
}
prom_query() {
  kubectl -n starfleet exec shuttle -- python -c 'import sys, urllib.parse, urllib.request
url = "http://prometheus:9090/api/v1/query?query=" + urllib.parse.quote(sys.argv[1])
print(urllib.request.urlopen(url, timeout=8).read().decode())' "$1"
}
for attempt in $(seq 1 12); do
  queue="$(prom_query 'count(lab_queue_depth{job="pods"})' | python3 -c 'import json, sys; print(len(json.load(sys.stdin)["data"]["result"]))' 2>/dev/null)"
  apps="$(prom_query 'count by (app) (lab_requests_total{job="pods"})' | python3 -c 'import json, sys
print(",".join(sorted(r["metric"].get("app", "") for r in json.load(sys.stdin)["data"]["result"])))' 2>/dev/null)"
  if [ "$queue" = "0" ] && [ "$apps" = "probe,scout" ]; then
    echo "PASS: lab_queue_depth is dropped and lab_requests_total is stored for probe and scout"
    exit 0
  fi
  sleep 5
done
echo "FAIL: lab_queue_depth must be absent for the job pods and lab_requests_total present with app probe and scout (queue results: $queue, apps: $apps)"
exit 1
