.. _cv_facts:

cv_facts
++++++++
Collect facts from CloudVision Portal.

Module added in version 2.9



.. contents::
   :local:
   :depth: 2


Synopsis
--------


Returns list of devices, configlets, containers and images


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
    <td>facts<br/><div style="font-size: small;"></div></td>
    <td>list</td>
    <td>no</td>
    <td>[&#x27;all&#x27;]</td>
    <td><ul><li>all</li><li>devices</li><li>containers</li><li>configlets</li><li>tasks</li></ul></td>
    <td>
        <div>List of facts to retrieve from CVP.</div>
        <div>By default, cv_facts returns facts for devices/configlets/containers/tasks</div>
        <div>Using this parameter allows user to limit scope to a subet of information.</div>
    </td>
    </tr>

    <tr>
    <td>gather_subset<br/><div style="font-size: small;"></div></td>
    <td>list</td>
    <td>no</td>
    <td>[&#x27;default&#x27;]</td>
    <td><ul><li>default</li><li>config</li><li>tasks_pending</li><li>tasks_failed</li><li>tasks_all</li></ul></td>
    <td>
        <div>When supplied, this argument will restrict the facts collected</div>
        <div>to a given subset.  Possible values for this argument include</div>
        <div>all, hardware, config, and interfaces.  Can specify a list of</div>
        <div>values to include a larger subset.  Values can also be used</div>
        <div>with an initial <code><a class="reference internal" href="#!"><span class="std std-ref">!</span></a></code> to specify that a specific subset should</div>
        <div>not be collected.</div>
    </td>
    </tr>

    </table>
    </br>

.. _cv_facts-examples-label:

Examples:
---------

::
    
    ---
      tasks:
        - name: '#01 - Collect devices facts from {{inventory_hostname}}'
          cv_facts:
            facts:
              devices
          register: FACTS_DEVICES

        - name: '#02 - Collect devices facts (with config) from {{inventory_hostname}}'
          cv_facts:
            gather_subset:
              config
            facts:
              devices
          register: FACTS_DEVICES_CONFIG

        - name: '#03 - Collect confilgets facts from {{inventory_hostname}}'
          cv_facts:
            facts:
              configlets
          register: FACTS_CONFIGLETS

        - name: '#04 - Collect containers facts from {{inventory_hostname}}'
          cv_facts:
            facts:
              containers
          register: FACTS_CONTAINERS

        - name: '#10 - Collect ALL facts from {{inventory_hostname}}'
          cv_facts:
          register: FACTS



Author
~~~~~~

* EMEA AS Team (@aristanetworks)




Status
~~~~~~

This module is flagged as **preview** which means that it is not guaranteed to have a backwards compatible interface.


