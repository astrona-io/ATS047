---
draft: true
exam_objectives:
- Push vs Pull
---
# Pull Collection And The Pushgateway

Prometheus collects metrics by scraping targets, but some producers, such as batch jobs, finish before a scrape can reach them. This module compares pull collection with push delivery, shows what each model proves about the health of a producer and teaches how the Pushgateway keeps the result of a short-lived job.

## Learning Goals

- Explain what a scrape is, which component starts it and what the `up` series proves.
- Compare the failure evidence of pull collection with the failure evidence of push delivery.
- Push a group to a Pushgateway with PUT, POST and DELETE and explain the grouping key.
- Explain what `honor_labels` does and why a Pushgateway scrape job needs it.
- Describe the lifecycle of a pushed group and make its age visible with a timestamp metric.

## Before You Start

You need to read a command line and to know what an HTTP request is and what a Kubernetes pod and a Service are. You do not need to know PromQL beyond reading a simple selector.

The playground starts the `probe` application, a Prometheus server that scrapes it every two seconds, a traffic generator and a Pushgateway on port 9091. The Prometheus server scrapes the Pushgateway in a job named `pushgateway`.

## What The Module Contains

The first part explains pull collection, the `up` series and what target health proves. The second part explains push delivery, the Pushgateway and its HTTP API. The third part covers the labels of a pushed group, the lifetime of a group and the rules for using the gateway well.

A graded lab follows the third part. It asks you to push a group, keep its job label and record three PromQL results. The module ends with a summary.

<!-- astrona:playground -->
