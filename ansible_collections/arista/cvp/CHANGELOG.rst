========================
Arista.Cvp Release Notes
========================

.. contents:: Topics


v3.6.0
======

Release Summary
---------------

Release 3.6.0 - See documentation on cvp.avd.sh for details.


Minor Changes
-------------

- Feat(cv_container_v3) Add support for image bundles on containers(#550)

Bugfixes
--------

- Fix(cv_facts_v3) Handle stale and empty devices in the inventory having an image bundle of type None(#569)

v3.5.1
======

Release Summary
---------------

Release 3.5.1 - See documentation on cvp.avd.sh for details.


Bugfixes
--------

- Fix Bump update min cvprac version(#547)

v3.5.0
======

Release Summary
---------------

Release 3.5.0 - See documentation on cvp.avd.sh for details.


Minor Changes
-------------

- Feat(cv_change_control_v3) Add support for approve/execute/schedule actions(#529)
- Feat(cv_device_v3) Implement image bundle on device level(#505)
- Feat(cv_device_v3) Support device decommissioning and device removal from provisioning(#507)
- Feat(cv_facts_v3) Expose verbose option in cv_facts_v3(#535)
- Feat(dhcp_configuration) Request add support for access point provisioning(#527)

Bugfixes
--------

- Fix(cv_change_control_v3) Dict key check on CC indexing is broken(#524)
- Fix(cv_device_v3) Allow all search_by options when assigning and removing image bundles(#541)
- Fix(cv_facts_v3) Make image bundle name key usage consistent(#513)

v3.4.0
======

Release Summary
---------------

Release 3.4.0 - See documentation on cvp.avd.sh for details.


Minor Changes
-------------

- Feat (dhcp_configuration) add a name to the dhcp record (https://github.com/aristanetworks/ansible-cvp/issues/481)
- Feat Add support for change controls (https://github.com/aristanetworks/ansible-cvp/issues/464)
- Feat Add svc account token auth method for on-prem and standardize it with cvaas (https://github.com/aristanetworks/ansible-cvp/issues/458)
- Feat Facts update (https://github.com/aristanetworks/ansible-cvp/issues/469)
- Feat New module to support topology tags (https://github.com/aristanetworks/ansible-cvp/issues/459)
- Feat(cv_facts_v3)  Show assigned image bundles on devices and containers (https://github.com/aristanetworks/ansible-cvp/issues/488)
- Feat(module_utils) Raise NotImplementedError if encrypted Vault password (https://github.com/aristanetworks/ansible-cvp/issues/479)

Bugfixes
--------

- Fix Changed pytest to check for a warning (https://github.com/aristanetworks/ansible-cvp/issues/485)
- Fix(cv_container_v3) Cannot remove containers anymore (https://github.com/aristanetworks/ansible-cvp/issues/487)
- Fix(cv_device_v3) device lookup to use search_key instead of FQDN always (https://github.com/aristanetworks/ansible-cvp/issues/483)
- Fix(image_tools) Change from error to warning if image already exists (https://github.com/aristanetworks/ansible-cvp/issues/471)

New Modules
-----------

- arista.cvp.cv_change_control_v3 - Change Control management with CloudVision
- arista.cvp.cv_tag_v3 - Create/Assign/Delete/Unassign tags on CVP
