#!/bin/bash

KEY=${1:-sasl.username}
PROP_FILE=${2:-./secrets/confluent.config}

ls $PROP_FILE

function prop {
    cat $PROP_FILE | grep "${1}" | cut -d'=' -f2
}

echo $(prop "$KEY")