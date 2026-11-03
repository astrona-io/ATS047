# Service Level Indicators, Objectives And Agreements Playground

This private environment runs a kind cluster with a `probe` Service, a traffic generator, Prometheus and a `shuttle` client pod in the `starfleet` namespace. The traffic generator makes one request in ten fail with status 500, and Prometheus scrapes the probe every two seconds.

Use it to build an availability SLI and a latency SLI, and to compare an SLI with a 99 percent objective. Query Prometheus from the `shuttle` pod, because the Prometheus Service is only reachable inside the cluster. Nothing here is graded.
