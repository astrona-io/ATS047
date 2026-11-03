#!/usr/bin/env bash
# Check: the running configuration reads the annotations and keeps the scrape annotation rule.
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
  if prom_get '/api/v1/status/config' | python3 -c 'import json, sys
text = json.load(sys.stdin)["data"]["yaml"]
for needle in ("prometheus_io_scrape", "prometheus_io_port", "prometheus_io_path", "action: keep"):
    assert needle in text, needle' 2>/dev/null; then
    echo "PASS: the rules read the scrape, port and path annotations"
    exit 0
  fi
  sleep 5
done
echo "FAIL: the running configuration must read prometheus_io_scrape, prometheus_io_port and prometheus_io_path and keep the keep rule"
exit 1
