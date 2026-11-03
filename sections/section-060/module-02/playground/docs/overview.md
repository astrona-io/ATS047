# Error Budgets And Burn Rate Playground

This private environment runs a kind cluster with a `probe` Service, a traffic generator, Prometheus and a `shuttle` client pod in the `starfleet` namespace. The traffic generator makes one request in ten fail with status 500, and Prometheus scrapes the probe every two seconds.

Use the exercises to calculate an error budget, a burn rate and a burn rate alert for a 99 percent objective. Query Prometheus from the `shuttle` pod, because the Prometheus Service is only reachable inside the cluster. Nothing here is graded, and you can change the Prometheus rule ConfigMap and restart its Deployment freely.
