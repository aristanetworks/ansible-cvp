#!/bin./bash

RESULT=$(python -c "from cvprac.cvp_apiV2 import CvpApi" && echo $?)

if [ "$RESULT" -eq "0" ]; then
    echo 'cvprac has been updated sucessfuly'
    exit 0
fi
echo 'You are not using custom version of cvprac'
exit 1
