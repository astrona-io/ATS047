---
draft: true
exam_objectives:
- Tracing and Spans
---
# Summary

A trace connects spans that describe operations in one distributed request. Context propagation allows participating services to preserve that relationship, while span timing and attributes help locate expensive or failed work.

Missing instrumentation, sampling and propagation errors can leave an incomplete picture. Concurrent spans must be interpreted by their timing and relationships rather than summed blindly, and trace attributes need controlled cost and confidentiality.
