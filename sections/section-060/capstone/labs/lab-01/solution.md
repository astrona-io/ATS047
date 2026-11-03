---
draft: true
exam_objectives:
- Basics of SLOs, SLAs, and SLIs
---
# Alert On Error Budget Burn Rate Solution

This walkthrough builds the rules in the order the task lists them. Each step ends with a check, so you can submit after any step and read the feedback.

## Connect to the lab

Use a host shell with the private kubeconfig for this independent kind environment. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-047-capstone-060)"
test "$(kubectl config current-context)" = "kind-astro-ats-047-capstone-060" || exit 1
```

Keep this connection selected.

## Inspect the starting state

Prometheus reads its rule files from the ConfigMap `prometheus-rules`. Look at the current content and at the current error ratio.

```sh
kubectl -n starfleet get configmap prometheus-rules -o yaml
kubectl -n starfleet get pods
```

The ConfigMap holds `groups: []`, so Prometheus has no rule to evaluate. The ratio of 500 responses is about 0.1, and a 99 percent objective allows 0.01. The burn rate is therefore about 10.

## Write the rules

The `expr` of the second rule divides the first recording rule by the error budget `1 - 0.99`. The alerting rule compares the second recording rule with 5 and waits 10 seconds before it fires.

Save this as `configmap-prometheus-rules.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-rules
  namespace: starfleet
data:
  rules.yaml: |
    groups:
    - name: checkout-slo
      rules:
      - record: sli:request_error_ratio:rate20s
        expr: sum(rate(lab_requests_total{status="500"}[20s])) / sum(rate(lab_requests_total[20s]))
      - record: slo:error_budget_burn_rate:rate20s
        expr: sli:request_error_ratio:rate20s / (1 - 0.99)
      - alert: ErrorBudgetFastBurn
        expr: slo:error_budget_burn_rate:rate20s > 5
        for: 10s
        labels:
          severity: page
        annotations:
          summary: The probe is using its error budget more than five times faster than allowed.
```

Apply it:

```sh
kubectl apply -f configmap-prometheus-rules.yaml
```

Prometheus reads the rule files when it starts or when it reloads its configuration. A ConfigMap volume also updates only after a delay. Restart the Deployment so that the new file is loaded at once:

```sh
kubectl -n starfleet rollout restart deployment/prometheus
kubectl -n starfleet rollout status deployment/prometheus --timeout=180s
```

## Check the result

The Prometheus API runs inside the cluster, so the `shuttle` pod sends the requests. Wait about 30 seconds after the restart, so that Prometheus has collected enough samples for a 20 second rate and has waited for the `for` duration.

```sh
kubectl -n starfleet exec shuttle -- python -c "import urllib.request; print(urllib.request.urlopen('http://prometheus:9090/api/v1/rules', timeout=8).read().decode())"
kubectl -n starfleet exec shuttle -- python -c "import urllib.request; print(urllib.request.urlopen('http://prometheus:9090/api/v1/alerts', timeout=8).read().decode())"
```

The rules response lists the group `checkout-slo` with three rules, each with `health` set to `ok`. The alerts response contains `ErrorBudgetFastBurn` with `state` set to `firing`. If the state is `pending`, the `for` duration has not passed yet, so run the second command again.

After recording your result, remove the independent lab with `astrona destroy ats-047-capstone-060`.

## Common pitfalls

> [!WARNING]
> A recording rule name that differs from the name used in the next rule makes the dependent rule return no data. A new ConfigMap does not reach Prometheus until it reloads, and a rule file with a YAML error leaves the old rules in place or stops Prometheus from starting, so read the Pod status after the restart.
