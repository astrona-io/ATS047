#!/usr/bin/env bash
# Check: probe and scout are active targets that are up; scout is scraped on :8080/stats.
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
expected="$(kubectl -n starfleet get pods -l 'app in (probe,scout)' -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}' | sort)"
for attempt in $(seq 1 12); do
  found="$(prom_get '/api/v1/targets' | python3 -c 'import json, sys
rows = []
for target in json.load(sys.stdin)["data"]["activeTargets"]:
    if target["scrapePool"] == "pods":
        pod = target["discoveredLabels"].get("__meta_kubernetes_pod_name", "?")
        ok = target["health"] == "up"
        if pod.startswith("scout"):
            ok = ok and target["scrapeUrl"].endswith(":8080/stats")
        rows.append(pod if ok else pod + ":bad")
print("\n".join(sorted(rows)))' 2>/dev/null)"
  if [ -n "$found" ] && [ "$found" = "$expected" ]; then
    echo "PASS: probe and scout are scraped successfully, scout on :8080/stats"
    exit 0
  fi
  sleep 5
done
echo "FAIL: targets are not all up on the right address and path. Found: $(echo "$found" | tr '\n' ' ')"
exit 1
