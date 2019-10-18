#!/bin/sh
configlet="CTL1-EXT-PRDSW-001_base-sw-backup","CTL1-EXT-PRDSW-001_nw","CTL1-EXT-PRDSW-001_gw","CTL1-EXT-PRDSW-001_ep"
container="CTL1_Prod"
device="CTL1-EXT-PRDSW-001"
action="show"
runScript="yes"
helptext="Actions:\n s - show\n a - add\n d - delete\n\nOperators\n w - container = CVP\n x - configlet = Test_Configlet\n y - container = CTL_DC1_GLEAF"
while getopts 'sadwxyp'  OPTION
do
case "${OPTION}"
in
s) action='show';;
a) action='add';;
d) action='delete';;
w) container='CVP';;
x) configlet='Test_Configlet';;
y) container='CTL_DC1_GLEAF';;
p) runScript="no";;
esac
done
echo 'CVPrac - Test Script..\n'
if [ $runScript == "yes" ]
then
  ./cvprac_DeviceTest.py --username cvpadmin --password atsira --host 10.83.30.100 --container $container --device $device --configlet $configlet --action $action
  echo 'CVPrac - Test Script Option: '$action
  echo 'Completed'
else
  echo $helptext
  echo "\nDefaults"
  echo " Configlets - " $configlet
  echo " Container  - " $container
  echo " Device     - " $device
  echo " Action     - " $action
fi
