#!/bin/bash

# ./run-img-label-processor.sh -t \'user-events\' -c \'"index < 1"\'

echo "Start consuming events with img_label_processor.py"

set -x;
python -u img_label_processor.py \
            -v \'/secrets/bgd-quickaccess.json\' \
            -f \'/secrets/confluent.config\' \
            "$@"
set +x;
