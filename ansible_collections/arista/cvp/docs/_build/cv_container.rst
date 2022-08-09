.. _cv_container:

cv_container
++++++++++++
Manage Provisioning topology.


.. contents::
   :local:
   :depth: 2

DEPRECATED
----------

:In: version:
:Why: Updated modules released with increased functionality
:Alternative: Use :ref:`arista.cvp.cv_container_v3 <arista.cvp.cv_container_v3>` instead.



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
    <td>configlet_filter<br/><div style="font-size: small;"></div></td>
    <td>list</td>
    <td>no</td>
    <td>[&#x27;none&#x27;]</td>
    <td></td>
    <td>
        <div>Filter to apply intended set of configlet on containers. If not used, then module only uses ADD mode. configlet_filter list configlets that can be modified or deleted based on configlets entries.</div>
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
    <td>mode<br/><div style="font-size: small;"></div></td>
    <td>str</td>
    <td>no</td>
    <td>merge</td>
    <td><ul><li>merge</li><li>override</li><li>delete</li></ul></td>
    <td>
        <div>Allow to save topology or not</div>
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
    <td>topology<br/><div style="font-size: small;"></div></td>
    <td>dict</td>
    <td>yes</td>
    <td></td>
    <td></td>
    <td>
        <div>Yaml dictionary to describe intended containers</div>
    </td>
    </tr>

    </table>
    </br>

.. _cv_container-examples-label:

Examples:
---------

::

    - name: Create container topology on CVP
      hosts: cvp
      connection: local
      gather_facts: no
      vars:
        verbose: False
        containers:
            Fabric:
                parent_container: Tenant
            Spines:
                parent_container: Fabric
                configlets:
                    - container_configlet
                images:
                    - 4.22.0F
                devices:
                    - veos01
      tasks:
        - name: "Gather CVP facts {{inventory_hostname}}"
          cv_facts:
          register: cvp_facts
        - name: "Build Container topology on {{inventory_hostname}}"
          cv_container:
            cvp_facts: "{{cvp_facts.ansible_facts}}"
            topology: "{{containers}}"
            mode: merge
          register: CVP_CONTAINERS_RESULT



Author
~~~~~~

* Ansible Arista Team (@aristanetworks)
