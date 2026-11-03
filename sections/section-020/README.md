---
draft: true
exam_objectives:
- Understand logs and events
---
# Understand logs and events

This section covers logs and events as evidence beside metrics. It has two modules. The first teaches what metrics, logs and events each hold, how a structured log record and a request identifier work, and how Kubernetes events record changes. The second teaches how to correlate metrics with logs, how collection, sampling and retention decide which records exist, and how to handle sensitive data and log cost.

Each module has a landing page, readings with hands-on steps in a private playground, a graded lab and a summary. The section ends with a capstone lab and a knowledge check.

## Learning Outcomes

- Explain the difference between a metric, a log record and an event, and say which question each answers.
- Read a structured JSON log record and find the record of one request from its request identifier.
- Read Kubernetes events with `kubectl`, filter them by reason and involved object, and explain their retention.
- Correlate a metric symptom with log records by route, instance and time, and explain why a match in time is not proof of a cause.
- Describe the path from standard output to a central store, and explain how rotation, sampling and retention remove records.
- Calculate a failure ratio from a counter, and explain why a ratio from sampled logs is wrong.
- Recognise personal data in log records, and apply redaction, access control and volume controls.
