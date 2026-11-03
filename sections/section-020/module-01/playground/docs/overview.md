---
draft: true
exam_objectives:
- Understand logs and events
---
# Logs And Events Playground

This is an ungraded environment. Nothing here is submitted or graded, and you can change anything.

## What runs

The `starfleet` namespace holds the `shop` Deployment. It serves requests on port 8080 at `/work` and metrics at `/metrics`, and it writes one JSON log record to standard output for each request it logs. It logs every failed request and one successful request in five. The `prometheus` Deployment scrapes the shop every two seconds under the job `shop`. The `traffic` Deployment sends about two requests per second to the shop: one in six returns status `500`, and every failure uses the route `/checkout`. The `shuttle` pod is a plain Python container that you use to send requests inside the cluster. The `drifter` pod in the `outpost` namespace is a second client.

## Connect

```sh
export KUBECONFIG="$(astrona kubeconfig ats-047-playground-020-01)"
test "$(kubectl config current-context)" = "kind-astro-ats-047-playground-020-01" || exit 1
```

## Things to try

Read the last records of the shop log and the Kubernetes events of the namespace.

```sh
kubectl -n starfleet logs deployment/shop --tail=10
kubectl -n starfleet get events --sort-by=.metadata.creationTimestamp
```

Send a request with a user name of your own and find its record by the `request_id` in the response. Scale the traffic down with `kubectl -n starfleet scale deployment/traffic --replicas=0`, send a few successful requests and count how many of them write a record. Scale it back to 1 afterwards. Delete the shop pod with `kubectl -n starfleet delete pod -l app=shop` and read the new events and the first lines of the new log.

Remove the playground with `astrona destroy ats-047-playground-020-01` when you are done.
