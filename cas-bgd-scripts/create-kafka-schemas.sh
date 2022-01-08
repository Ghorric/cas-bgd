#!/bin/bash

kubectl apply -f ./k8s/create-kafka-schemas.yaml \
  && sleep 3 \
  && kubectl logs pod/create-kafka-schema \
  && echo '' \
  && kubectl delete -f ./k8s/create-kafka-schemas.yaml