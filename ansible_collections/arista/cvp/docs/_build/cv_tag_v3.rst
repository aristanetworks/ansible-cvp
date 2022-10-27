.. _cv_tag_v3:

cv_tag_v3
+++++++++
Create/Assign/Delete/Unassign tags on CVP

Module added in version 3.4.0



.. contents::
   :local:
   :depth: 2


Synopsis
--------


CloudVision Portal Tag module to Create/Assign/Delete/Unassign tags on CloudVision


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
    <td>auto_create<br/><div style="font-size: small;"></div></td>
    <td>bool</td>
    <td>no</td>
    <td>True</td>
    <td><ul><li>yes</li><li>no</li></ul></td>
    <td>
        <div>auto_create tags before assigning</div>
    </td>
    </tr>

    <tr>
    <td>mode<br/><div style="font-size: small;"></div></td>
    <td>str</td>
    <td>no</td>
    <td></td>
    <td><ul><li>create</li><li>delete</li><li>assign</li><li>unassign</li></ul></td>
    <td>
        <div>action to carry out on the tags create - create tags delete - delete tags assign - assign existing tags to device unassign - unassign existing tags from device</div>
    </td>
    </tr>

    <tr>
    <td>tags<br/><div style="font-size: small;"></div></td>
    <td>list</td>
    <td>yes</td>
    <td></td>
    <td></td>
    <td>
        <div>CVP tags</div>
    </td>
    </tr>

    </table>
    </br>

.. _cv_tag_v3-examples-label:

Examples:
---------

::

    # Create and assign device and interface tags to multiple devices and interfaces
    - name: cv_tag_v3 example1
      hosts: cv_server
      connection: local
      gather_facts: no
      vars:
        CVP_TAGS:
          - device: leaf1
            device_tags:
              - name: tag1
                value: value1
              - name: tag2
                value: value2
              - name: tag3
                value: value3
            interface_tags:
              - interface: Ethernet1
                tags:
                  - name: tag1i
                    value: value1i
                  - name: tag2i
                    value: value2i
              - interface: Ethernet2
                tags:
                  - name: tag1i
                    value: value1i
                  - name: tag2i
                    value: value2i
          - device: spine1
            device_tags:
              - name: DC
                value: Dublin
              - name: rack
                value: rackA
              - name: pod
                value: podA
            interface_tags:
              - interface: Ethernet3
                tags:
                  - name: tag3i
                    value: value3i
                  - name: tag4i
                    value: value4i
              - interface: Ethernet4
                tags:
                  - name: tag5i
                    value: value6i
                  - name: tag6i
                    value: value6i
      tasks:
        - name: "create tags"
          arista.cvp.cv_tag_v3:
            tags: "{{CVP_TAGS}}"
            mode: assign
            auto_create: true

    # Delete device and interface tags
    - name: cv_tag_v3 example2
      hosts: cv_server
      connection: local
      gather_facts: no
      vars:
        CVP_TAGS:
          - device: leaf1
            device_tags:
              - name: tag1
                value: value1
            interface_tags:
              - interface: Ethernet1
                tags:
                  - name: tag1i
                    value: value1i
      tasks:
        - name: "create tags"
          arista.cvp.cv_tag_v3:
            tags: "{{CVP_TAGS}}"
            mode: delete

    # Create device and interface tags (without assigning to the devices)
    - name: cv_tag_v3 example3
      hosts: cv_server
      connection: local
      gather_facts: no
      vars:
        CVP_TAGS:
          - device: leaf1
            device_tags:
              - name: tag1
                value: value1
            interface_tags:
              - interface: Ethernet1
                tags:
                  - name: tag1i
                    value: value1i
      tasks:
        - name: "create tags"
          arista.cvp.cv_tag_v3:
            tags: "{{CVP_TAGS}}"
            mode: create

    # Assign device and interface tags
    - name: cv_tag_v3 example4
      hosts: cv_server
      connection: local
      gather_facts: no
      vars:
        CVP_TAGS:
          - device: leaf1
            device_tags:
              - name: tag1
                value: value1
            interface_tags:
              - interface: Ethernet1
                tags:
                  - name: tag1i
                    value: value1i
      tasks:
        - name: "create tags"
          arista.cvp.cv_tag_v3:
            tags: "{{CVP_TAGS}}"
            mode: assign

    # Unassign device and interface tags
    - name: cv_tag_v3 example5
      hosts: cv_server
      connection: local
      gather_facts: no
      vars:
        CVP_TAGS:
          - device: leaf1
            device_tags:
              - name: tag1
                value: value1
            interface_tags:
              - interface: Ethernet1
                tags:
                  - name: tag1i
                    value: value1i
      tasks:
        - name: "create tags"
          arista.cvp.cv_tag_v3:
            tags: "{{CVP_TAGS}}"
            mode: assign



Author
~~~~~~

* Ansible Arista Team (@aristanetworks)



Full Schema
~~~~~~~~~~~
Get full schema docs `here <../../schema/cv_tag_v3/>`_.
