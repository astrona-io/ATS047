---
draft: true
exam_objectives:
- Understand logs and events
---
# Prerequisites

Use astrona, kubectl, kind, Python 3, Podman and a shell. Node inspection exercises use the containers in this environment, not the physical host.

```sh
export KUBECONFIG="$(astrona kubeconfig ats-047-lab-020-02-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-047-lab-020-02-01" || exit 1
```
