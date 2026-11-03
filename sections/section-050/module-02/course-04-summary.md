---
draft: true
exam_objectives:
- Service Discovery
---
# Summary

Target relabeling turns discovered candidates into scrape targets. Prometheus runs the rules of `relabel_configs` in order for each candidate. A rule joins its source labels with a separator, matches the result against a regular expression that must cover the whole string, and then acts. The default action `replace` writes a label. If the expression does not match, the rule does nothing and reports nothing.

Labels that start with two underscores exist only during relabeling and are removed after the last rule. A pod name or a namespace reaches stored series only when a rule copies it into a public label. The `instance` label defaults to the final `__address__`, and the `job` label comes from the job name.

The actions `keep` and `drop` select targets. A `keep` rule lists what is allowed, and a `drop` rule lists what is excluded. A dropped candidate is not scraped and has no `up` series, but it stays visible under `droppedTargets` in the targets API with its discovered labels. A missing label counts as an empty string, so a `keep` rule removes pods that lack the label.

The labels `__address__`, `__scheme__` and `__metrics_path__` define the scrape request, and rules can rewrite them. A common convention puts the scrape switch, the port and the path in pod annotations that the rules read. Prometheus gives these annotations no meaning by itself.

Metric relabeling uses `metric_relabel_configs` and runs on each sample after the scrape. It can drop a metric by `__name__` or change sample labels. It saves storage but not the cost of producing and transferring the metric, and it cannot change targets. Two jobs that scrape the same endpoint store the same observations twice under different `job` labels.

Key facts:

- Rules run in order, and each rule sees the result of the previous rules.
- Regular expressions are anchored: `probe` does not match `probe-v2`.
- Defaults: action `replace`, regex `(.*)`, replacement `$1`, separator `;`.
- Target relabeling runs before the scrape. Metric relabeling runs after it.

<!-- astrona:playground:destroy -->
