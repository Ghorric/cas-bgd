#!/bin/bash

# Example calls ->   
#                   ./helm-exec.sh
#                   ./helm-exec.sh -l app.kubernetes.io/name=minio -- ls -al
#                   ./helm-exec.sh -- python mapstore/redis_service.py
#                   ./helm-exec.sh -- python streaming/producer.py -f /secrets/confluent.config -t test1
#                   ./helm-exec.sh -- python streaming/consumer.py -f /secrets/confluent.config -t test1
#                   ./helm-exec.sh -- python labels/google_vision.py
#                   ./helm-exec.sh -- ./streaming/kcat.sh -t test1 -L
#                   ./helm-exec.sh -- ./streaming/kcat.sh -t user-events -C -K ::: -o beginning
#                   ./helm-exec.sh -- python streaming/event_consumer.py -f /secrets/confluent.config -t user-events
#                   ./helm-exec.sh -- python mapstore/redis_service.py -u ''"'"'"Genevieve Graham"'"'"''
#
#   Windows -> Git Bash -> kubectl exec:
#   POD=`./shell/helm-pod-by-label.sh -p pod/` && echo $POD && winpty kubectl exec -it "$POD" -c cas-bgd-chart -- //bin//bash
#   >> python mapstore/redis_service.py -u '"Genevieve Graham"'

# Args
FIND_POD_CMD="./shell/helm-pod-by-label.sh -p pod/"
for arg in "$@"
do
    [ "$arg" == "--" ] && break
    FIND_POD_CMD="$FIND_POD_CMD $arg"
    shift
done

# Find Pod & Stop if Pod not set
POD=`eval "$FIND_POD_CMD"`
[ $? -ne 0 ] && echo "Pod NOT found.." && exit -1
[ -z "$POD" ] && echo "Pod NOT found..." && exit -1

# Prepare command
ALL=$@
[ -z "$1" ] && ALL="-- bash"
FULL_CMD="kubectl exec -it $POD $ALL"

# Run command in container
echo "$FULL_CMD"
eval "$FULL_CMD"