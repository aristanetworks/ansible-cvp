# CVPRAC Version 2

Copy of original CvpRac distribution - https://github.com/aristanetworks/cvprac

cvp_client now imports cvp_apiV2 instead of the original cvp_apiV2

**cvp_apiV2**

Contains additional functions to apply and remove Configlets to containers and a fix for check the parent of a Container.
These were logged as Issues:
85 cvp_api fails to identify top level container - https://github.com/aristanetworks/cvprac/issues/85
88 Additional Container Modules  - https://github.com/aristanetworks/cvprac/issues/88

Any additional functionality will be added to this version and raised as Issues in the original CvpRac distribution.

**cvprac_test.py**

Test script to used in the development of CvpRacV2 to confirm behaviour of functions used in with the ansible modules

**test.sh**

shell script to execute cvprac_test.py and pass command line arguments to it, me being lazy during testing.
