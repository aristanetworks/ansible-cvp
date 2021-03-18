.. _cv_device_v3:

cv_device_v3
++++++++++++
Manage Provisioning topology.

Module added in version 3.0.0



.. contents::
   :local:
   :depth: 2


Synopsis
--------


CloudVision Portal Configlet configuration requires a dictionary of containers with their parent, to create and delete containers on CVP side.
Returns number of created and/or deleted containers


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
    <td>devices<br/><div style="font-size: small;"></div></td>
    <td>list</td>
    <td>yes</td>
    <td></td>
    <td></td>
    <td>
        <div>List of devices with their container and configlets information</div>
    </td>
    </tr>

    <tr>
    <td>state<br/><div style="font-size: small;"></div></td>
    <td>str</td>
    <td>no</td>
    <td>present</td>
    <td><ul><li>present</li><li>absent</li></ul></td>
    <td>
        <div>Set if ansible should build or remove devices on CLoudvision</div>
    </td>
    </tr>

    </table>
    </br>

.. _cv_device_v3-examples-label:

Examples:
---------

::

    ---
    - name: Device Management in Cloudvision
      hosts: cv_server
      connection: local
      gather_facts: false
      collections:
        - arista.avd
        - arista.cvp
      vars:
        CVP_DEVICES:
          - fqdn: CV-ANSIBLE-EOS01
            parentContainerName: ANSIBLE
            configlets:
                - 'CV-EOS-ANSIBLE01'
      tasks:
        - name: "Configure devices on {{inventory_hostname}}"
          arista.cvp.cv_device_v3:
            devices: '{{CVP_DEVICES}}'
            state: present



Author
~~~~~~

* EMEA AS Team (@aristanetworks)
