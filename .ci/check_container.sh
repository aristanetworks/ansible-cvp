#!/bin./bash

# Following VARS must be defined in your CI/CD server to use correct information
# - CVP_SERVER
# - CVP_USERNAME
# - CVP_PASSWORD

if [ -z ${CVP_SERVER} ]; then
    CVP_SERVER='10.73.1.139'
    CVP_USERNAME='tom'
    CVP_PASSWORD='nomios101'
fi

CONTAINER='ansible_cvp'
COOKIE='cookie.txt'

echo 'CVP Server: '$CVP_SERVER
echo 'Authenticate user: '$CVP_USERNAME
curl -k -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d '{"userId": "'${CVP_USERNAME}'","password": "'${CVP_PASSWORD}'"}' 'https://'$CVP_SERVER'/cvpservice/login/authenticate.do' -c $COOKIE 2>/dev/null
echo ''
echo '-----------------'
echo 'Query CVP server: '$CONTAINER
echo '-----------------'
RESULT=$(curl -s -k -X GET --header 'Accept: application/json' 'https://'${CVP_SERVER}'/cvpservice/inventory/containers?name=ansible_container' -b $COOKIE)
NB_ITEM=$(echo "${RESULT}" | jq length)
echo "$RESULT"
echo ''
if [ "${NB_ITEM}" == '1' ]; then
    echo "-->OK - container exists on CVP"
else
    echo "-->FAILURE - container does not exist on CVP"
fi