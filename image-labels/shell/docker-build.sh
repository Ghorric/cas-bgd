#!/bin/bash
export BUILD=${1:-true}
export DOCKER_IMAGE=${2:-wengle/image-labels}
export COMMAND="${3:-docker stop image-labels}"

# Build Docker Image
if [ "$BUILD" == "true" ] || [[ "$(docker images -q $DOCKER_IMAGE 2> /dev/null)" == "" ]]; then
  echo "Build $DOCKER_IMAGE"
  eval "$COMMAND"
  docker build -t $DOCKER_IMAGE .
fi