---
draft: true
exam_objectives:
- Service Discovery
---
# Summary

Service discovery supplies candidate endpoints and metadata. Target relabeling turns those candidates into the addresses and labels that Prometheus actually scrapes, while metric relabeling processes individual samples later.

Discovery access, selection rules and target uniqueness determine coverage. A discovered object is not automatically a healthy scrape target, and metadata must be deliberately retained before internal labels disappear from stored series.
