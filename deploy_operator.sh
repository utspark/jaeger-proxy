#!/bin/bash
git clone git@github.com:jaegertracing/jaeger-operator.git
cd jaeger-operator

#deploy jaeger operator
kubectl create ns observability
kubectl create -n observability -f deploy/crds/jaegertracing.io_jaegers_crd.yaml
kubectl create -n observability -f deploy/service_account.yaml
kubectl create -n observability -f deploy/role.yaml
kubectl create -n observability -f deploy/role_binding.yaml
kubectl create -n observability -f deploy/operator.yaml

kubectl apply -n observability -f deploy/examples/simplest.yaml
