#!/bin/bash -ex

minikube mount ./logs:/mnt/logs > /dev/null&
kubectl apply -f fluent-bit-collector.yaml
kubectl apply -f pv.yaml
kubectl create -f https://raw.githubusercontent.com/fluent/fluent-bit-kubernetes-logging/master/fluent-bit-service-account.yaml
kubectl create -f https://raw.githubusercontent.com/fluent/fluent-bit-kubernetes-logging/master/fluent-bit-role-1.22.yaml
kubectl create -f https://raw.githubusercontent.com/fluent/fluent-bit-kubernetes-logging/master/fluent-bit-role-binding-1.22.yaml
kubectl create -f fluent-bit-configmap.yaml
kubectl create -f https://raw.githubusercontent.com/fluent/fluent-bit-kubernetes-logging/master/output/elasticsearch/fluent-bit-ds-minikube.yaml
kubectl rollout status daemonset/fluent-bit -n logging
kubectl port-forward --namespace logging service/log-collector 8080:80 > /dev/null&
