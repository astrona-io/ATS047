---
draft: true
exam_objectives:
- Understand logs and events
---
# Summary

Metrics, logs and events are three kinds of evidence. A metric is a number that Prometheus reads at an interval and stores with a timestamp. It counts a whole group of events and costs the same however many requests happen. A log record describes one event with detail, and the volume of logs grows with the traffic. An event is an object that a Kubernetes component creates when a resource changes. Each kind answers a different question: how many, what happened and what changed.

A structured log record writes its facts as named fields, usually one JSON object on each line. The fields that make a record useful are the time in UTC, the level, a fixed message, the service, the instance and the details of the request. A request identifier that the application returns in the response and writes in the record joins the two. With the identifier, one response leads to exactly one record. The identifier belongs in the log and not in a metric label, because a label with a new value for every request creates a new series for every request.

Kubernetes events record changes of resources. An event has a type of `Normal` or `Warning`, a fixed reason, a message, the involved object and the component that reported it. Several components create events for one pod: the deployment controller, the ReplicaSet controller, the scheduler and the kubelet. Events are namespaced, they live for one hour by default, and repeated events are combined into one object with a count.

Every source keeps only part of the history. The shop writes a record for every failed request and for a fraction of the successful ones, the container log is replaced when the pod is replaced, and events expire. A record that you cannot find does not prove that nothing happened.

- Metrics count, logs describe single cases, events record changes.
- A request identifier links a response to its log record.
- Filter events by reason and involved object, not by message text.
- Events are kept for one hour by default.

<!-- astrona:playground:destroy -->
