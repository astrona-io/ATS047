---
draft: true
exam_objectives:
- Basics of SLOs, SLAs, and SLIs
---
# Summary

An error budget is the failure that an SLO allows in its window. It equals one minus the target, applied to the events of the window. A request-based budget counts failed events and grows with traffic. A time-based budget counts bad minutes. The consumed share is the bad events divided by the budget, and a value above 1 means the objective is missed. Teams agree a policy in advance that says what to do as the budget shrinks.

The burn rate is the observed error ratio divided by the allowed error ratio. A burn rate of 1 uses exactly the whole budget over the whole window, and a higher value uses it faster. The window length divided by the burn rate gives the time until the budget is gone. The range of the query decides how quickly the value reacts and how noisy it is, and low traffic makes it unstable.

An alert on the burn rate has the same meaning for every objective. A good alert needs a long window above the threshold, which shows that the loss matters, and a short window above it, which shows that the loss continues. Different burn rates and window pairs give pages for fast losses and tickets for slow losses. In Prometheus, recording rules store the burn rates, and an alerting rule with a `for` duration, a `severity` label and a `summary` annotation sends the notification.

Key facts:

- Error budget = (1 - target) times the valid events in the window.
- Burn rate = observed error ratio divided by (1 - target).
- Time to exhaustion = window divided by burn rate.
- Fast burn alerts check a long window and a short window together.

<!-- astrona:playground:destroy -->
