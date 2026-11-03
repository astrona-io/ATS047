---
draft: true
exam_objectives:
- Understand logs and events
---
# Summary

Correlation joins a metric symptom to the log records that explain it. The join uses the same facts in both sources: the route, the status, the instance and a time window that is wider than the symptom. A request identifier then picks one request. Clocks, time zones and replaced pod names can break the join. A match in time makes an event or a change a candidate explanation, and only a hypothesis that survives a search for contrary records is a conclusion.

A log record travels from standard output to a node file, through rotation, to a collector and a central store, and it is deleted at the end of retention. `kubectl logs` reads the current file of one pod, and a central search reads only what the collector shipped. Each stage can lose records. A search that finds nothing describes the coverage of that stage and does not prove that nothing happened.

Sampling keeps only some records. The shop keeps every failed request and one successful request in five, and each record states its rule in the field `sample_every`. Counts from sampled records need weights. A failure ratio from the log is wrong because the log holds more failures than successes in proportion, while a counter counts every request and gives the true ratio.

Records can hold personal data and secrets. The controls are to not log the field, to redact it at the source, to restrict readers, to encrypt and to keep retention short. A debug setting that logs full requests needs a time limit and an owner. Log volume is a cost that levels, sampling and careful fields control. Bounded labels belong in metrics, request detail belongs in logs and the path of one request across services belongs in traces.

- Join metrics and logs by shared field names and a wide time window.
- A coincidence in time is not a proof of a cause.
- Sampling and retention decide which records exist.
- Calculate ratios from counters, not from sampled logs.
- Do not write personal data or secrets to logs.

<!-- astrona:playground:destroy -->
