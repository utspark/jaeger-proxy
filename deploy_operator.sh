#!/bin/bash
action=$1

if [ $action == "create" ]
then
  git clone git@github.com:jaegertracing/jaeger-operator.git
  action='apply'
fi

if [ $action == "apply" ]
then
  
  cd jaeger-operator

  #deploy jaeger operator
  kubectl create ns observability
  kubectl create -n observability -f deploy/crds/jaegertracing.io_jaegers_crd.yaml
  kubectl create -n observability -f deploy/service_account.yaml
  kubectl create -n observability -f deploy/role.yaml
  kubectl create -n observability -f deploy/role_binding.yaml
  kubectl create -n observability -f deploy/operator.yaml

  cd ../
  kubectl apply -f all-in-one-with-options.yaml
elif [ $action == "delete" ]
then
  cd jaeger-operator

  kubectl delete -n observability -f deploy/crds/jaegertracing.io_jaegers_crd.yaml
  kubectl delete -n observability -f deploy/service_account.yaml
  kubectl delete -n observability -f deploy/role.yaml
  kubectl delete -n observability -f deploy/role_binding.yaml
  kubectl delete -n observability -f deploy/operator.yaml

  cd ../
  kubectl delete -f all-in-one-with-options.yaml
  kubectl delete ns observability
fi
