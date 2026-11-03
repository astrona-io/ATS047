---
draft: true
exam_objectives:
- Understand logs and events
---
# Sensitive Data And Log Cost

A log record keeps whatever the developer decided to write. Records are read by many people, copied to other systems and stored for weeks. A field that was convenient while debugging can expose personal data to everyone who can read the logs. This part explains how to recognise sensitive data in records, how to reduce the exposure, and how the volume of logs creates cost.

## What Counts As Sensitive

Personal data is any information that identifies a person: a name, an email address, a phone number, an IP address or a stable user identifier together with other facts. Secrets are credentials that give access: passwords, API keys, session cookies and access tokens. Business data, such as the content of a payment request, can be confidential as well.

Logs collect this data by accident. A developer logs the whole request to debug a failure, and the request holds an authorisation header. A library logs the full URL, and the URL has a token in its query string. Each of these puts a secret or a personal fact in a system that was not designed to protect it.

## Find The Sensitive Field

The shop writes a record for each logged request. Select the cluster and read a few records.

<!-- astrona:playground:renew -->

```sh
export KUBECONFIG="$(astrona kubeconfig ats-047-playground-020-02)"
test "$(kubectl config current-context)" = "kind-astro-ats-047-playground-020-02" || exit 1
```

```sh
kubectl -n starfleet logs deployment/shop --tail=5
```

Read each field name and ask what it identifies. The fields `route`, `status` and `duration_ms` describe the request and no person. The field `user_id` is a stable identifier of a user, which is personal data when it can be linked to a person. The field `email` holds an email address, which identifies a person directly. The shop writes the address even though no investigation of a failed request needs it.

## Reduce The Exposure

The best protection is to not write the data. Apply these controls in this order.

- Do not log the field. Remove it from the record when no investigation needs it.
- Redact the field. Replace the value with a fixed text, for example `[redacted]`, or with a hash that stays the same for the same input, so that records of one user can still be grouped without showing the address.
- Restrict the readers. Give access to the log store only to the people who need it, and record who reads it.
- Protect the data in transit and at rest with encryption, and keep the retention short for records that hold personal data.

Redaction at the source is stronger than redaction in the collector, because the sensitive value never reaches the node log file. A collector filter can still help as a second layer, because it protects records from applications that nobody has fixed yet.

## Debug Logging Needs A Decision

A setting that logs complete requests and responses helps during an investigation and exposes data while it is on. Turn it on for a defined time, for a defined service and with a person who is responsible for turning it off. A debug setting that nobody removes becomes the permanent default, and the log store then holds payloads for the whole retention period.

## Volume Creates Cost

Every record costs storage, network and indexing work, and a search over more records is slower. The shop writes a record for every failed request and for one successful request in five, and the counter `shop_log_records_total` shows how many records it wrote. Ask Prometheus for the rate of records and the rate of requests.

```sh
prom_query() {
  kubectl -n starfleet exec shuttle -- python -c 'import sys,urllib.parse,urllib.request; print(urllib.request.urlopen("http://prometheus:9090/api/v1/query?"+urllib.parse.urlencode({"query":sys.argv[1]}),timeout=8).read().decode())' "$1"
}
prom_query 'sum(rate(shop_log_records_total[1m]))'
prom_query 'sum(rate(shop_http_requests_total[1m]))'
```

The record rate is about one third of the request rate, because one request in six fails and one successful request in five writes a record. Without sampling, the log would hold a record for every request, and it would be about three times larger here. In a real system with thousands of requests per second the difference is large.

Measure the size of a part of the log. The command below counts the bytes of the last 200 lines:

```sh
kubectl -n starfleet logs deployment/shop --tail=200 | wc -c
```

Multiply a line size by the rate of records and the retention period to estimate the storage. The estimate shows why levels, sampling and field choices are cost controls and not only style rules.

## Levels As A Volume Control

The level of a record decides whether it is written at all. A production service usually writes `info` and above and keeps `debug` records off, because debug records can be ten times more numerous. When an investigation needs more detail, raise the level for one service for a short time and lower it again.

A level is only useful when writers use it with the same meaning. If a harmless retry is logged as `error`, the count of `error` records rises and hides the real failures. Write `error` for a failed operation that needs attention, `warn` for a problem that the system handled, and `info` for normal events that you want to count.

## Retention And Access For Sensitive Records

Retention is also a privacy control. Personal data should be kept only as long as the purpose needs it. If the log store keeps every record for a year, every email address in it also lives for a year. Shorter retention for the most detailed records, and longer retention for aggregated metrics, limits the exposure without losing the long-term trend.

Access needs the same care. People who investigate incidents need to read records, but not everyone needs to read every service. Give read access by team and by purpose, and keep a record of who searched the store. A log store that every employee can read is a copy of the sensitive data with weaker controls than the original database.

## Choose The Right Signal For The Detail

Metrics, logs and traces carry detail at different costs. A metric label with a user identifier multiplies series and is the most expensive place for that detail. A log record holds the user identifier at the cost of one value on one line. A trace carries the identifier for a request across services. Put each fact in the signal where the cost matches how often you query it: bounded labels in metrics, request detail in logs and the path of one request in traces.

## What You Know Now

You know which fields in a record are personal data or secrets, and you know the controls: do not log, redact, restrict readers, encrypt and keep retention short. You know that log volume is a cost, that sampling and levels control it, and that high-detail facts belong in logs and not in metric labels. With the earlier parts you can now correlate signals, state what each one covers and keep the evidence safe.

## Common pitfalls

> [!WARNING]
> Do not leave a debug setting that logs full requests turned on after an investigation. Do not assume that a stable user identifier is harmless, because it can identify a person. Do not rely on the collector alone to remove secrets: remove them in the application so that they never reach a node file.
