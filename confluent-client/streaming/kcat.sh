#!/bin/bash

#  ./helm-exec.sh -- ./streaming/kcat.sh -t test1 -L
#  ./helm-exec.sh -- ./streaming/kcat.sh -t user-events -L
#  ./helm-exec.sh -- ./streaming/kcat.sh -t user-events -C -o beginning -K :::

CFG_FILE="/secrets/confluent.config"
#CFG_FILE="../../cas-bgd-scripts/secrets/confluent.config"

function prop {
    cat $CFG_FILE | grep "${1}" | cut -d'=' -f2
}

#set -x;
kafkacat -b $(prop "bootstrap.servers") \
  -X security.protocol=$(prop "security.protocol") -X sasl.mechanisms=$(prop "sasl.mechanisms") \
  -X sasl.username=$(prop "sasl.username")  -X sasl.password=$(prop "sasl.password") \
  "$@"
#set +x;