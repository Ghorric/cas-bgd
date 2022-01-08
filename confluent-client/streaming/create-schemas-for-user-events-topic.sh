#!/bin/bash

printf '\nlist-schemas:'
./topic-mgt.sh -c wsl -a list-schemas

#printf '\n\n create-schema: user-events-key: \n'
#./topic-mgt.sh -c container -a create-schema -t user-events -k key

printf '\n\n create-schema: user-events-value: \n'
./topic-mgt.sh -c container -a create-schema -t user-events -k value

printf '\n\n get-latest-schema: \n'
#./topic-mgt.sh -c container -a get-latest-schema -t user-events -k key
./topic-mgt.sh -c container -a get-latest-schema -t user-events -k value