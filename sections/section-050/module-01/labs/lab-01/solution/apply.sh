#!/usr/bin/env bash
# Reference solution: add the pods job limited to starfleet and restart Prometheus.
set -euo pipefail
kubectl apply -f - <<'YAML'
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: starfleet
data:
  prometheus.yaml: |
    global:
      scrape_interval: 5s
      evaluation_interval: 5s
    scrape_configs:
    - job_name: prometheus
      static_configs:
      - targets:
        - localhost:9090
    - job_name: probe
      static_configs:
      - targets:
        - probe:8080
    - job_name: pods
      kubernetes_sd_configs:
      - role: pod
        namespaces:
          names:
          - starfleet
YAML
kubectl -n starfleet rollout restart deployment/prometheus
kubectl -n starfleet rollout status deployment/prometheus --timeout=180s
sleep 15
