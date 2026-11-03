# Discover Pods In One Namespace

Graded lab for the discovery module. Status: UNTESTED. Static checks only; the lab has not been booted.

The learner adds a `pods` job with `kubernetes_sd_configs` (role `pod`) limited to `starfleet`. The validation scripts read the live Prometheus API through the `shuttle` pod. Run `astrona test -c .` to apply the reference solution once labs are tested.
