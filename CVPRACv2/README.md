# CVPRAC Version 2

Copy of original CvpRac distribution - https://github.com/aristanetworks/cvprac

cvp_client now imports cvp_apiV2 instead of the original cvp_api

**cvp_apiV2**

Contains additional functions to apply and remove Configlets to containers and a fix for check the parent of a Container.
These were logged as Issues:

85 cvp_api fails to identify top level container - https://github.com/aristanetworks/cvprac/issues/85

88 Additional Container Modules  - https://github.com/aristanetworks/cvprac/issues/88

90 Factory Reset Device and Move to Undefined Container - https://github.com/aristanetworks/cvprac/issues/90

91 Get Device Reconcile Config - https://github.com/aristanetworks/cvprac/issues/91

Any additional functionality will be added to this version and raised as Issues in the original CvpRac distribution.

**cvprac_ContainerTest.py**

Test script to used in the development of CvpRacV2 to confirm behaviour of functions used in with the ansible modules to manipulate containers

**cvprac_DeviceTest.py**

Test script to used in the development of CvpRacV2 to confirm behaviour of functions used in with the ansible modules to manipulate devices

**test.sh**

shell script to execute cvprac_test.py and pass command line arguments to it, me being lazy during testing.
