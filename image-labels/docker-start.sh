#!/bin/bash
export OPT=${1}
export DOCKER_IMAGE=wengle/image-labels
export CONTAINER_NAME=image-labels

# BUILD
if [ "$OPT" == "-b" ] ; then OPT="true" ; fi
./shell/docker-build.sh $OPT

