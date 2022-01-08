#!/bin/bash

# Command:
# ./topic-mgt.sh [-v] [-c <cfg>] [-a <action>] [-t <topic>] [-k <kind>] [-d <display>]
#
# Options:
#  -v           verbose flag
#  -c <cfg>     Either path to config file or some predefined values: container (or c), wsl (or w)
#  -a <action>  Choose one: list-schemas, create-schema, get-latest-schema
#  -t <topic>   Kafka topic name
#  -k <kind>    Choose the schema type: either 'key' or 'value'
#  -d           Defines the output format. Choose one: <empty>, pretty, id, version, subject, schema
#
#  Example usage:
#   ./topic-mgt.sh -c wsl -a list-schemas
#   ./topic-mgt.sh -c wsl -a create-schema -t user-events -k key
#   ./topic-mgt.sh -c wsl -a create-schema -t user-events-out -k value
#   ./topic-mgt.sh -c wsl -a get-latest-schema -t user-events-out -k value
#   ./topic-mgt.sh -c container -a create-schema -t user-events -k value
#   ./topic-mgt.sh -c wsl -a get-latest-schema -t user-events -k value
#   ./topic-mgt.sh -c wsl -a get-latest-schema -t user-events -k value -d pretty
#   ./topic-mgt.sh -c wsl -a get-latest-schema -t user-events -k value -d id -v
#


DEFAULT_CFG_FILE="/secrets/confluent.config"
CFG_FILE="${DEFAULT_CFG_FILE}"

POSITIONAL=()
while [[ $# -gt 0 ]]; do
  key="$1"

  case $key in
    -c|--cfg)
      CFG_FILE="${2}"
      if [[ "$CFG_FILE" == "c" || "$CFG_FILE" == "container" ]] ; then CFG_FILE="${DEFAULT_CFG_FILE}"; fi
      if [[ "$CFG_FILE" == "w" || "$CFG_FILE" == "wsl" ]] ; then CFG_FILE="../../cas-bgd-scripts/secrets/confluent.config"; fi
      shift # past argument
      shift # past value
      ;;
    -a|--action)
      ACTION="${2}"
      shift # past argument
      shift # past value
      ;;
    -f|--filename)
      FILENAME="${2}"
      shift # past argument
      shift # past value
      ;;
    -t|--topic)
      TOPIC="${2}"
      shift # past argument
      shift # past value
      ;;
    -k|--kind)
      SCHEMA_KIND="${2}"
      shift # past argument
      shift # past value
      ;;
    -d|--display)
      DISPLAY="${2}"
      shift # past argument
      shift # past value
      ;;
    -v|--verbose)
      VERBOSE="1"
      shift # past argument
      # shift # past value
      ;;
    *)    # unknown option
      POSITIONAL+=("$1") # save it in an array for later
      shift # past argument
      ;;
  esac
done


if [[ "$TOPIC" == "user-events" && "$SCHEMA_KIND" == "key" ]] ; then FILENAME="./reg/user-events-key.avsc" ;  fi
if [[ "$TOPIC" == "user-events" && "$SCHEMA_KIND" == "value" ]] ; then FILENAME="./reg/user-events-value.avsc" ;  fi
if [[ "$TOPIC" == "user-events-out" && "$SCHEMA_KIND" == "value" ]] ; then FILENAME="./reg/user-events-out-value.avsc" ;  fi
if [[ "$TOPIC" == "dummy" && "$SCHEMA_KIND" == "key" ]] ; then FILENAME="./reg/user-events-key.avsc" ;  fi
if [[ "$TOPIC" == "dummy" && "$SCHEMA_KIND" == "value" ]] ; then FILENAME="./reg/user-events-value.avsc" ;  fi

[[ ! -z "$VERBOSE" ]] && echo "ACTION=$ACTION, TOPIC=$TOPIC, SCHEMA_kind=$SCHEMA_KIND, CFG_FILE=$CFG_FILE, FILENAME=$FILENAME"

function prop {
    cat $CFG_FILE | grep "${1}" | cut -d'=' -f2
}

[[ -z "$ACTION" ]] && echo "Please specify an action for the command (e.g., -a list-schemas)."

if [[ "$ACTION" == "list-schemas" ]] ; then
  CMD_CURL="curl -s -u $(prop "basic.auth.user.info") $(prop "schema.registry.url")/subjects"
  [[ ! -z "$VERBOSE" ]] && echo "Execute command: $CMD_CURL"
  eval $CMD_CURL
fi

if [[ "$ACTION" == "create-schema" && ! -z "$TOPIC" && ! -z "$SCHEMA_KIND" && ! -z "$FILENAME" ]] ; then
  [[ ! -z "$VERBOSE" ]] && echo "Create schema: $TOPIC-$SCHEMA_KIND ($FILENAME)"
  jq '. | {schema: tojson}' $FILENAME | \
      curl -s -X POST -u $(prop "basic.auth.user.info") -H 'Content-Type: application/vnd.schemaregistry.v1+json' \
          -d @- $(prop 'schema.registry.url')/subjects/$TOPIC-$SCHEMA_KIND/versions
fi

if [[ "$ACTION" == "get-latest-schema" && ! -z "$TOPIC" && ! -z "$SCHEMA_KIND" ]] ; then
  [[ ! -z "$VERBOSE" ]] && echo "Get latest schema: $TOPIC-$SCHEMA_KIND"
  curl -s -X GET -u $(prop "basic.auth.user.info") \
          $(prop 'schema.registry.url')/subjects/$TOPIC-$SCHEMA_KIND/versions/latest \
            | if [[ "$DISPLAY" == "pretty" ]] ; then \
                jq '.schema | fromjson' ; \
              elif [[ "$DISPLAY" == "id" ]] ; then \
                jq '.id' ; \
              elif [[ "$DISPLAY" == "version" ]] ; then \
                jq '.version' ; \
              elif [[ "$DISPLAY" == "subject" ]] ; then \
                jq '.subject' ; \
              elif [[ "$DISPLAY" == "schema" ]] ; then \
                jq '.schema' ; \
              else \
                jq -r ; \
              fi
fi

