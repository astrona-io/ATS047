---
draft: true
exam_objectives:
- Basics of SLOs, SLAs, and SLIs
---
# Calculate The Error Budget Burn Rate

Solve this task in the private kind environment of this lab.

## Starting state

The `probe` Service in the `starfleet` namespace serves requests, and a traffic generator sends a steady stream of them. One request in ten fails with status 500. Prometheus scrapes the probe every two seconds. The team promised 99 percent successful requests, so the error budget is 1 percent of requests. Nobody has measured how fast the budget is used.

Use a host shell with the private kubeconfig for this independent kind environment. A kubeconfig identifies the cluster and credentials used by kubectl, the Kubernetes command-line tool.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-047-lab-060-02-01)"
test "$(kubectl config current-context)" = "kind-ats-047-lab-060-02-01" || exit 1
```

Keep this connection selected.

## Required result

Calculate the burn rate of the probe as a Prometheus expression and record it as evidence. The burn rate is the error ratio over a 20 second range divided by the allowed error ratio of the 99 percent objective.

Use exactly the expression `(sum(rate(lab_requests_total{status="500"}[20s])) / sum(rate(lab_requests_total[20s]))) / (1 - 0.99)`. Record the report in the ConfigMap `evidence` in `starfleet`, under the key `report.json`. The report is a JSON object with the fields `expression`, `evaluated_at` and `data`. The field `data` is the `data` object that the Prometheus API returns, with numbers kept as returned.

Wait at least 20 seconds after the environment starts before you query a rate. Record the evidence less than five minutes before you submit. A changed expression or an empty result fails.

## Verify the result

The grader reads the ConfigMap, repeats your query against the live Prometheus API for the stored evaluation time and compares the results. It also checks that the burn rate lies between 5 and 15. Do not change the `probe`, `traffic` or `prometheus` Deployments.
