---
draft: true
exam_objectives:
- Push vs Pull
---
# Summary

In the pull model, Prometheus starts every collection. It sends a request to each target on its own schedule, stamps the samples with the time of the scrape and stores the series `up` for each target. The value of `up` shows whether the scrape worked. It does not show whether the application does its work, and it does not exist for a target that is no longer discovered.

In the push model, the producer starts the delivery, and a producer that stops sending leaves no trace. A reader cannot tell a stopped producer from a producer that had nothing to report. Freshness has to be stored as a value, such as the Unix time of the last successful run, and a query has to test it.

The Pushgateway holds the latest result of service-level batch jobs and serves it to Prometheus as a normal target. A PUT request replaces a group, a POST request replaces only the metrics it names and a DELETE request removes the group. The Pushgateway never removes a group by itself, so its `up` series describes the gateway and not the jobs behind it.

The scrape job of a Pushgateway needs `honor_labels: true`, or Prometheus renames the pushed `job` label to `exported_job`. The grouping labels decide how many series the gateway creates, so they must stay stable and the owner of a job must delete its group when the job ends.

- Pull gives target health for free; push needs an explicit freshness metric.
- Use the Pushgateway for service-level batch results, not for services that can be scraped.
- Set `honor_labels: true` on the Pushgateway scrape job.
- Delete the groups of retired jobs.

<!-- astrona:playground:destroy -->
