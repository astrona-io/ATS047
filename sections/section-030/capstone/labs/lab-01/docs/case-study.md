---
draft: true
exam_objectives:
- Tracing and Spans
---
# Starting Environment

`probe` calls `scout`. The `traffic` Deployment adds a query parameter `api_key=sk-test-0000` to every request it sends to `probe`. Every fifth request is slow because `scout` waits 0.3 seconds. No evidence report exists.
