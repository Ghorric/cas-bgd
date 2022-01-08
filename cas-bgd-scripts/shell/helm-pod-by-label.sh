#!/bin/bash

# Args
POSITIONAL=()
while [[ $# -gt 0 ]]; do
  key="$1"

  case $key in
    -p|--prefix)
      PREFIX="$2"
      shift # past argument
      shift # past value
      ;;
    -l|--label)
      LABEL="${2}"
      shift # past argument
      shift # past value
      ;;
    *)    # unknown option
      POSITIONAL+=("$1") # save it in an array for later
      shift # past argument
      ;;
  esac
done

# Find Pod
LABEL="${LABEL:-app=img}"
OUTP=$(kubectl get pods -l $LABEL -o=jsonpath="{..metadata.name}")

# Exit -1 IF Pod NOT found...
[ -z "$OUTP" ] && exit -1

# Output
echo "$PREFIX$OUTP"