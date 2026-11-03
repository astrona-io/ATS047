---
draft: true
exam_objectives:
- Understand logs and events
---
# Logs And Events Capstone: Investigate A Failing Shop

Capstone lab for the section on logs and events. The learner joins a log record, route failure metrics, the sampling fraction, the sensitive field and the Kubernetes event of the shop pod. `testing/live.py` re-reads the shop log and the events, and re-runs the expressions at the recorded time. Events expire after one hour by default, so a smoke run late in the life of the cluster can fail on the event.

Status: UNTESTED. Only static checks (`astrona validate`, `bash -n`, `py_compile`) have run. Runtime verification is pending: `testing/smoke.sh` has not been run on a live cluster.
