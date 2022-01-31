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
    <td>apply_mode<br/><div style="font-size: small;"></div></td>
    <td>str</td>
    <td>no</td>
    <td>loose</td>
    <td><ul><li>loose</li><li>strict</li></ul></td>
    <td>
        <div>Set how configlets are attached/detached on device. If set to strict all configlets not listed in your vars are detached.</div>
    </td>
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
    <td>search_key<br/><div style="font-size: small;"></div></td>
    <td>str</td>
    <td>no</td>
    <td>hostname</td>
    <td><ul><li>fqdn</li><li>hostname</li><li>serialNumber</li></ul></td>
    <td>
        <div>Key name to use to look for device in Cloudvision.</div>
    </td>
    </tr>

    <tr>
    <td>state<br/><div style="font-size: small;"></div></td>
    <td>str</td>
    <td>no</td>
    <td>present</td>
    <td><ul><li>present</li><li>factory_reset</li></ul></td>
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

    # task in loose mode using fqdn (default)
    - name: Device Management in Cloudvision
      hosts: cv_server
      connection: local
      gather_facts: false
      collections:
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
            search_key: fqdn

    # task in loose mode using serial
    - name: Device Management in Cloudvision
      hosts: cv_server
      connection: local
      gather_facts: false
      collections:
        - arista.cvp
      vars:
        CVP_DEVICES:
          - serialNumber: xxxxxxxxxxxx
            parentContainerName: ANSIBLE
            configlets:
                - 'CV-EOS-ANSIBLE01'
      tasks:
        - name: "Configure devices on {{inventory_hostname}}"
          arista.cvp.cv_device_v3:
            devices: '{{CVP_DEVICES}}'
            state: present
            search_key: serialNumber

    # task in strict mode
    - name: Device Management in Cloudvision
      hosts: cv_server
      connection: local
      gather_facts: false
      collections:
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
            apply_mode: strict



Author
~~~~~~

* EMEA AS Team (@aristanetworks)
