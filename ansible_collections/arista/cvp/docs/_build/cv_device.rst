.. _cv_device:

cv_device
+++++++++
Provision, Reset, or Update CloudVision Portal Devices.


.. contents::
   :local:
   :depth: 2

DEPRECATED
----------

:In: version:
:Why: Updated modules released with increased functionality
:Alternative: Use :ref:`arista.cvp.cv_device_v3 <arista.cvp.cv_device_v3>` instead.



Synopsis
--------


CloudVision Portal Device compares the list of Devices
in devices against cvp-facts then adds, resets, or updates them as appropriate.
If a device is in cvp_facts but not in devices it will be reset to factory defaults in ZTP mode
If a device is in devices but not in cvp_facts it will be provisioned
If a device is in both devices and cvp_facts its configlets and imageBundles will be compared
and updated with the version in devices if the two are different.
Warning - reset means devices will be erased and will run full ZTP process. Use this function with caution !


.. _module-specific-options-label:

Module-specific Options
-----------------------
The following options may be specified for this module:

.. raw:: html

    <table border=1 cellpadding=4>

    <tr>
    <th class="head">parameter</th>
    <th class="head">type</th>
    <th class="head">required</th>
    <th class="head">default</th>
    <th class="head">choices</th>
    <th class="head">comments</th>
    </tr>

    <tr>
    <td>configlet_mode<br/><div style="font-size: small;"></div></td>
    <td>str</td>
    <td>no</td>
    <td>override</td>
    <td><ul><li>override</li><li>merge</li><li>delete</li></ul></td>
    <td>
        <div>If override, Add listed configlets and remove all unlisted ones.</div>
        <div>If merge, Add listed configlets to device and do not touch already configured configlets.</div>
    </td>
    </tr>

    <tr>
    <td>cvp_facts<br/><div style="font-size: small;"></div></td>
    <td>dict</td>
    <td>yes</td>
    <td></td>
    <td></td>
    <td>
        <div>Facts from CVP collected by cv_facts module</div>
    </td>
    </tr>

    <tr>
    <td>device_filter<br/><div style="font-size: small;"></div></td>
    <td>list</td>
    <td>no</td>
    <td>[&#x27;all&#x27;]</td>
    <td></td>
    <td>
        <div>Filter to apply intended mode on a set of configlet. If not used, then module only uses ADD mode. device_filter list devices that can be modified or deleted based on configlets entries.</div>
    </td>
    </tr>

    <tr>
    <td>devices<br/><div style="font-size: small;"></div></td>
    <td>dict</td>
    <td>yes</td>
    <td></td>
    <td></td>
    <td>
        <div>Yaml dictionary to describe intended devices configuration from CVP stand point.</div>
    </td>
    </tr>

    <tr>
    <td>options<br/><div style="font-size: small;"></div></td>
    <td>dict</td>
    <td>no</td>
    <td></td>
    <td></td>
    <td>
        <div>Implements the ability to create a sub-argument_spec, where the sub</div>
        <div>options of the top level argument are also validated using</div>
        <div>the attributes discussed in this section.</div>
    </td>
    </tr>

    <tr>
    <td>state<br/><div style="font-size: small;"></div></td>
    <td>str</td>
    <td>no</td>
    <td>present</td>
    <td><ul><li>present</li><li>absent</li></ul></td>
    <td>
        <div>If absent, devices will be removed from CVP and moved back to undefined.</div>
        <div>If present, devices will be configured or updated.</div>
    </td>
    </tr>

    </table>
    </br>

.. _cv_device-examples-label:

Examples:
---------

::

    ---
    - name: Test cv_device
      hosts: cvp
      connection: local
      gather_facts: no
      collections:
        - arista.cvp
      vars:
        configlet_list:
          cv_device_test01: "alias a{{ 999 | random }} show version"
          cv_device_test02: "alias a{{ 999 | random }} show version"
        # Device inventory for provision activity: bind configlet
        devices_inventory:
          veos01:
            name: veos01
            configlets:
              - cv_device_test01
              - SYS_TelemetryBuilderV2_172.23.0.2_1
              - veos01-basic-configuration
              - SYS_TelemetryBuilderV2
      tasks:
          # Collect CVP Facts as init process
        - name: "Gather CVP facts from {{inventory_hostname}}"
          cv_facts:
          register: cvp_facts
          tags:
            - always

        - name: "Configure devices on {{inventory_hostname}}"
          tags:
            - provision
          cv_device:
            devices: "{{devices_inventory}}"
            cvp_facts: '{{cvp_facts.ansible_facts}}'
            device_filter: ['veos']
          register: cvp_device

        - name: "Add configlet to device on {{inventory_hostname}}"
          tags:
            - provision
          cv_device:
            devices: "{{devices_inventory}}"
            cvp_facts: '{{cvp_facts.ansible_facts}}'
            configlet_mode: merge
            device_filter: ['veos']
          register: cvp_device



Author
~~~~~~

* Ansible Arista Team (@aristanetworks)
