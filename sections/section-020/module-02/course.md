---
draft: true
exam_objectives:
- Understand logs and events
---
# Correlation, Sampling And Retention

A log record, a metric and an event only help together when you can connect them, and they only help while they exist. This module teaches how to correlate metrics with logs by identity, labels and time, how collection, sampling and retention decide which records exist, and how to keep personal data and cost under control.

## Learning Goals

- Correlate a metric symptom with log records using the route, the instance, the time window and a request identifier.
- Explain why a correlation in time is a candidate cause and not proof of the cause.
- Describe the stages between an application and a log search: standard output, node files, rotation, collection and storage.
- Explain how sampling changes what a log shows, and calculate the share of requests that wrote a record.
- Explain why a failure ratio from sampled logs is wrong and a failure ratio from a counter is right.
- Recognise personal data in a record, and explain redaction, access control and the cost of log volume.

## Before You Start

You need to know what a structured log record, a request identifier and a Kubernetes event are. The module repeats the facts it needs in one or two sentences. The playground starts the same shop application as before: it writes JSON log records, logs every failed request and one successful request in five, and is scraped by Prometheus.

## What The Module Contains

The first part joins a metric to log records by route, instance and time. The second part follows a record from standard output to a search and shows what sampling and retention remove. The third part covers sensitive data in records and the cost of log volume.

A graded lab follows the third part. It asks you to measure the sampling, find the field with personal data and compare two ways to calculate a failure ratio. The module ends with a summary.

<!-- astrona:playground -->
