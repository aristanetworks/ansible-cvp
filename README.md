# CVP_Ansible_Modules
Pre Release Work in progress Anisble modules for CVP

**cv_configlet**

 - add, delete, and show configlets.

Configlets can be created, deleted then added to containers or devices.
Any Tasks that are generated as a result will be returned.
Need to add the option to check (CVP verify) the configuration contained in the configlet

**cv_container**
 - add, delete, and show containers

Containers can be created or deleted

**CvpRac**

To use these modules you will need cvprac.
Official version can be found here: [Arista Networks cvprac](https://github.com/aristanetworks/cvprac)
CVPRACV2 in this repository is a tweaked version with additional functionality that has been requested in the official version. See README in CVPRACV2 folder.

Other CVP Ansible modules can be found here: [Arista EOS+ Ansible Modules](https://github.com/arista-eosplus/ansible-cloudvision)
