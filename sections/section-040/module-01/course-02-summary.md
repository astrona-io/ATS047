---
draft: true
exam_objectives:
- Push vs Pull
---
# Summary

Pull collection lets Prometheus control scrape timing and observe whether a target responds. Push delivery can suit particular producer lifecycles, but it changes ownership of freshness and failure evidence.

The Pushgateway serves selected short-lived batch use cases and retains pushed data until managed otherwise. Remote write sends collected samples to another system; neither mechanism should be confused with universal replacement of normal application scraping.
