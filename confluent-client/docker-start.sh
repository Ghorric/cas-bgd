#!/bin/bash
export OPT=${1}
export DOCKER_IMAGE=wengle/confluent-client
export CONTAINER_NAME=confluent-client

# BUILD
if [ "$OPT" == "-b" ] ; then OPT="true" ; fi
./shell/docker-build.sh $OPT

# RUN
if [ "$OPT" == "-c" ] ; then export RUN_CMD="python ./consumer.py -f ../cas-bgd-scripts/secrets/confluent.config -t test1" ;
elif [ "$OPT" == "-p" ] ; then export RUN_CMD="python ./producer.py -f ../cas-bgd-scripts/secrets/confluent.config -t test1" ;
elif [ "$OPT" == "-s" ] ; then export RUN_CMD="//bin/bash" ;
 else echo "Choose mode: consumer->-c producer->-p shell->-s build->-b" && exit ;
fi

if [ `docker ps 2>&1 | grep -F $CONTAINER_NAME | wc -l` -eq 0 ]; then
    echo "RUN $CONTAINER_NAME => $RUN_CMD"
    # docker run --name=$CONTAINER_NAME --rm -d $DOCKER_IMAGE $RUN_CMD
    docker run --name=$CONTAINER_NAME --rm -it $DOCKER_IMAGE $RUN_CMD
fi
