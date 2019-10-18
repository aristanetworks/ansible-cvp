#!/bin/sh
container="None"
device="None"
action="show"
while getopts 'sadcewx'  OPTION
do
case "${OPTION}"
in
s) action="show";;
a) action="add";;
d) action="delete";;
c) container="Testing";;
e) container="Testing2";;
w) device="CTL1-EXT-PRDSW-001";;
x) device="CTL1-PRD-SLEAF-006";;
esac
done
echo 'CVPrac - Test Script..'
./cvprac_ContianerTest.py --username cvpadmin --password atsira --host 10.83.30.100 --container $container --device $device --data ./vars/lab_data.yml --template Test.j2 --action $action
echo 'CVPrac - Test Script Option: '$action
echo 'Completed'
