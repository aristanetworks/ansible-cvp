#!/bin/sh
container="None"
device="None"
image="None"
action="show"
runScript="yes"
helptext="Actions:\n s - show\n a - add\n d - delete\n\nOperators\n w - container = CTL1_Prod\n x - device - CTL1-EXT-PRDSW-001\n y - device = Wrong_One\n z - container - Wrong_One"
while getopts 'sadhijkwxypz'  OPTION
do
case "${OPTION}"
in
s) action='show';;
a) action='add';;
d) action='delete';;
h) image="Wrong_One";;
i) image="EOS-4.18.5M+TerminAttr-1.4.1";;
j) image="EOS-4.20.11M+Terminattr-1.5.5-1";;
k) container='Testing';;
w) container='CTL1_Prod';;
x) device='CTL1-PRD-GLEAF-001';;
y) device='Wrong_One';;
z) container='Wrong_One';;
p) runScript="no";;
esac
done
echo 'CVPrac - Test Script..\n'
if [ $runScript == "yes" ]
then
  ./cvprac_ImageTest.py --username cvpadmin --password atsira --host 10.83.30.100 --container $container --device $device --image $image --action $action
  echo 'CVPrac - Test Script Option: '$action
  echo 'Completed'
else
  echo $helptext
  echo "\nDefaults"
  echo " Container  - " $container
  echo " Device     - " $device
  echo " Action     - " $action
fi
