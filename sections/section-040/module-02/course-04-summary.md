---
draft: true
exam_objectives:
- Push vs Pull
---
# Summary

Remote write sends samples that a Prometheus server has already collected to another endpoint. It does not instrument applications, discover targets or replace scraping. A queue reads the samples from the write-ahead log, splits them over shards and retries failed batches, so a short outage of the endpoint loses nothing, while a long outage can. The local server keeps working when the endpoint fails.

A query does not need a sample at the exact time it asks about. Prometheus uses the newest sample inside the lookback window, five minutes by default. A staleness marker ends a series earlier: Prometheus writes it when a series leaves a scrape or when a target disappears. After the marker, instant queries return nothing, and range queries still return the samples stored before it.

A deleted Pushgateway group shows this behavior. After the next scrape the series no longer appears in an instant query, although its history remains. A presence test is therefore weaker than a test on a value. A metric that holds the time of the last success, compared with `time()`, gives a result that does not depend on the lookback window.

When data looks old, the cause sits in one stage of a path: the producer, the scrape, local processing or downstream delivery. A fault affects the stages after it and none before it. Checking the stages in order, with the evidence that each one leaves, finds the first faulty stage.

- Remote write copies collected samples; it does not collect.
- The default lookback window is five minutes; staleness markers end a series sooner.
- Test freshness with a timestamp value, not with the presence of a series.
- Follow the path in order and stop at the first fault.

<!-- astrona:playground:destroy -->
