#!/bin/sh
taskID="all"
action="show"
runScript="yes"
helptext="Actions:\n s - show\n a - add\n d - delete\n\nOperators\n l - taskID = all\n i - taskID = 2268"
while getopts 'hsadli:p'  OPTION
do
case "${OPTION}"
in
h) runScript="no";;
s) action='show';;
a) action='add';;
d) action='delete';;
l) taskID="all";;
i) taskID="$OPTARG";;
p) runScript="no";;
esac
done
echo 'CVPrac - Test Script..\n'
if [ $runScript == "yes" ]
then
  ./cvprac_TaskTest.py --username cvpadmin --password atsira --host 10.83.30.100 --taskID $taskID --action $action
  echo 'CVPrac - Test Script Option: '$action
  echo 'Completed'
else
  echo $helptext
  echo "\nDefaults"
  echo " taskID  - " $taskID
fi
