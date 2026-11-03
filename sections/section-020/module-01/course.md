---
draft: true
exam_objectives:
- Understand logs and events
---
# Metrics, Logs And Events As Evidence

Metrics, logs and events are three kinds of data that describe a running system. Each kind answers a different question, and each has its own cost and its own blind spots. This module teaches what each kind holds, how a structured log record is built, and how Kubernetes events record changes in the cluster.

## Learning Goals

- Explain the difference between a metric sample, a log record and an event, and say which question each one answers.
- Read a structured log record in JSON format and name the fields that make it useful: time, level, service, instance, message and request identifier.
- Find the log record of one request from the request identifier in its response.
- Read Kubernetes events with `kubectl`, and explain their fields, their types and their retention.
- Explain why an event or a log is evidence for one moment and not a complete history.

## Before You Start

You need to know that a Prometheus server scrapes a metrics endpoint and stores samples. The module repeats the facts it needs in one or two sentences. The playground starts a shop application that writes JSON log records, a Prometheus server that scrapes it, and a traffic generator.

## What The Module Contains

The first part compares the three kinds of data on one application: the numbers on the metrics endpoint, the lines on standard output and the events of the cluster. The second part covers the structure of a log record and how a request identifier connects a response to its record. The third part covers Kubernetes events: what creates them, what they contain and how long they live.

A graded lab follows the second part. It asks you to send one failing request and to find its record and the failing route. The module ends with a summary.

<!-- astrona:playground -->
