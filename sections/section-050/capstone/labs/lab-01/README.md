# Relabel Annotated Pods And Drop A Metric (Section Capstone)

Graded capstone for the section. Status: UNTESTED. Static checks only; the lab has not been booted.

It combines pod discovery, target relabeling (keep, address and path rewrite, public labels) and metric relabeling. The `scout` pod declares no container port, so the address must come from the port annotation. The validation scripts read the live Prometheus API through the `shuttle` pod.
