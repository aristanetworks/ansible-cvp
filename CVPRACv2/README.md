# CVPRAC Version 2

Copy of original CvpRac distribution - https://github.com/aristanetworks/cvprac

**To Install**

Install the official version of CvpRac then copy the cvp_apiV2 library to the CvpRac directory.

Amend the cvp_client to import cvp_apiV2 instead of the original cvp_api as follows:

#from cvprac.cvp_api import CvpApi

#Import Updated CvpApi until cvprac is updated

from cvprac.cvp_apiV2 import CvpApi

**cvp_apiV2**

Contains additional functions to apply and remove Configlets to containers and a fix for check the parent of a Container.
These were logged as Issues:

85 cvp_api fails to identify top level container - https://github.com/aristanetworks/cvprac/issues/85

88 Additional Container Modules  - https://github.com/aristanetworks/cvprac/issues/88

90 Factory Reset Device and Move to Undefined Container - https://github.com/aristanetworks/cvprac/issues/90

91 Get Device Reconcile Config - https://github.com/aristanetworks/cvprac/issues/91

94 Get additional Device info using getNetElementInfoById - https://github.com/aristanetworks/cvprac/issues/94

96 No return for the method "execute_task" - https://github.com/aristanetworks/cvprac/issues/96

98 Add return option to - def cancel_task(self, task_id): - https://github.com/aristanetworks/cvprac/issues/98

Any additional functionality will be added to this version and raised as Issues in the original CvpRac distribution.

**cvprac_ContainerTest.py**

Test script used in the development of CvpRacV2 to confirm behaviour of functions used with the ansible modules to manipulate containers

**cvprac_DeviceTest.py**

Test script used in the development of CvpRacV2 to confirm behaviour of functions used with the ansible modules to manipulate devices

**cvprac_ImageTest.py**

Test script used in the development of CvpRacV2 to confirm behaviour of functions used with the ansible modules to manipulate images

**cvprac_TaskTest.py**

Test script used in the development of CvpRacV2 to confirm behaviour of functions used with the ansible modules to manipulate tasks

**test_container.sh**

shell script to execute cvprac_ContainerTest.py and pass command line arguments to it, me being lazy during testing.

**test_device.sh**

shell script to execute cvprac_Devicetest.py and pass command line arguments to it, me being lazy during testing.

**test_image.sh**

shell script to execute cvprac_Imagetest.py and pass command line arguments to it, me being lazy during testing.

**test_task.sh**

shell script to execute cvprac_TaskTest.py and pass command line arguments to it, me being lazy during testing.
