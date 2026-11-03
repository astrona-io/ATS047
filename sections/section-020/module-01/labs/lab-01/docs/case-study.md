---
draft: true
exam_objectives:
- Understand logs and events
---
# Starting Environment

The `shop` Deployment handles about two requests per second. One request in six fails with status `500`, always on the route `/checkout`. The shop logs every failed request and one successful request in five. No evidence report exists.