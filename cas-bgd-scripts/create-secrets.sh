#!/bin/bash
SECRET_NAME=${1:-img-secrets}
KEY01="confluent.config"
VAL01=${2:-./secrets/confluent.config}
KEY02="bgd-quickaccess.json"
VAL02=${3:-./secrets/bgd-recommender.json}

kubectl create secret generic $SECRET_NAME \
   --from-file=$KEY01=$VAL01 \
   --from-file=$KEY02=$VAL02