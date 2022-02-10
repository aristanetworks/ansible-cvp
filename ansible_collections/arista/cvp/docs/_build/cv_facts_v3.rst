.. _cv_facts_v3:

cv_facts_v3
+++++++++++
Collect facts from Cloudvision

Module added in version 3.3.0



.. contents::
   :local:
   :depth: 2


Synopsis
--------


Returns list of devices, configlets, containers and images from CloudVision


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
    <td>[&#x27;configlets&#x27;, &#x27;containers&#x27;, &#x27;devices&#x27;, &#x27;images&#x27;]</td>
    <td><ul><li>configlets</li><li>containers</li><li>devices</li><li>images</li></ul></td>
    <td>
        <div>List of facts to retrieve from CVP.</div>
        <div>By default, cv_facts returns facts for devices/configlets/containers/tasks</div>
        <div>Using this parameter allows user to limit scope to a subset of information.</div>
    </td>
    </tr>

    <tr>
    <td>regexp_filter<br/><div style="font-size: small;"></div></td>
    <td>str</td>
    <td>no</td>
    <td>.*</td>
    <td></td>
    <td>
        <div>Regular Expression to filter configlets and devices in facts</div>
    </td>
    </tr>

    </table>
    </br>

.. _cv_facts_v3-examples-label:

Examples:
---------

::

      tasks:
      - name: '#01 - Collect devices facts from {{inventory_hostname}}'
        arista.cvp.cv_facts_v3:

      - name: '#02 - Collect devices facts from {{inventory_hostname}}'
        arista.cvp.cv_facts_v3:
          facts:
            - configlets
        register: FACTS_DEVICES

      - name: '#03 - Collect devices facts from {{inventory_hostname}}'
        arista.cvp.cv_facts_v3:
          facts:
            - devices
            - containers
        register: FACTS_DEVICES



Author
~~~~~~

* EMEA AS Team (@aristanetworks)
