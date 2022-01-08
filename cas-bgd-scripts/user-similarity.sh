#!/bin/bash

echo 'Example: python mapstore/redis_service.py -u '"'"'"Genevieve Graham"'"'"''
POD=`./shell/helm-pod-by-label.sh -p pod/` && echo $POD && winpty kubectl exec -it "$POD" -c cas-bgd-chart -- //bin//bash
