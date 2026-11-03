---
draft: true
exam_objectives:
- Push vs Pull
---
# Push vs Pull

This section covers the two ways metrics reach Prometheus. It has two modules. The first compares pull collection with push delivery and teaches the Pushgateway. The second teaches remote write, staleness and a method for tracing old data through the collection path.

Each module has a landing page, readings with hands-on steps in a private playground, a graded lab and a summary. The section ends with a capstone lab and a knowledge check.

## Learning Outcomes

- Explain what a scrape is and what the `up` series proves about a target.
- Compare the failure evidence of pull collection with the failure evidence of push delivery.
- Push, replace and delete Pushgateway groups, and explain the grouping key.
- Explain `honor_labels`, group cleanup and the timestamp metric that makes the age of a batch result visible.
- Explain what remote write sends, how its queue works and how to confirm delivery at a receiver.
- Predict what instant and range queries return after a series ends, using the lookback window and staleness markers.
- Trace stale data through the producer, the scrape, local processing and downstream delivery.
