# CVP_Ansible_Modules
Pre Release Work in progress Anisble modules for CVP

**cv_configlet**

 - add, delete, and show configlets.

Configlets can be created, deleted then added to containers or devices. - also in cv_devices as required to move devices between containers
Any Tasks that are generated as a result will be returned.
Need to add the option to check (CVP verify) the configuration contained in the configlet

**cv_container**
 - add, delete, and show containers

Containers can be created or deleted

**cv_device**
 - add, delete, and show devices

Devices can be deployed from the undefined container to a provisioned container or moved from one container to another using the add functionality and specifiying the target container. Configlets and Images can be added to devices using add and specifying the current parent container.
Devices can be Removed from CVP using the delete option and specifying "CVP" as the container, equivalent to the REMOVE GUI option.
Devices can be reset and moved to the undefined container using the delete option and specifying "RESET" as the container.
Configlets and Images can be removed from a device using the delete option and specifiying the configs to be removed and the current parent container as the container.
show option provide device data and current config.

**CvpRac**

To use these modules you will need cvprac.
The official version can be found here: [Arista Networks cvprac](https://github.com/aristanetworks/cvprac)
CVPRACV2 in this repository is a tweaked version with additional functionality that has been requested in the official version. See README in CVPRACV2 folder.

Other CVP Ansible modules can be found here: [Arista EOS+ Ansible Modules](https://github.com/arista-eosplus/ansible-cloudvision)
