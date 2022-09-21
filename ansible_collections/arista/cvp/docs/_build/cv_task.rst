.. _cv_task:

cv_task
+++++++
Execute or Cancel CVP Tasks.


.. contents::
   :local:
   :depth: 2

DEPRECATED
----------

:In: version:
:Why: Updated modules released with increased functionality
:Alternative: Use :ref:`arista.cvp.cv_task_v3 <arista.cvp.cv_task_v3>` instead.



Synopsis
--------


CloudVision Portal Task module


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
    <td>executed</td>
    <td><ul><li>executed</li><li>cancelled</li></ul></td>
    <td>
        <div>action to carry out on the task executed - execute tasks cancelled - cancel tasks</div>
    </td>
    </tr>

    <tr>
    <td>tasks<br/><div style="font-size: small;"></div></td>
    <td>list</td>
    <td>yes</td>
    <td></td>
    <td></td>
    <td>
        <div>CVP taskIDs to act on</div>
    </td>
    </tr>

    <tr>
    <td>wait<br/><div style="font-size: small;"></div></td>
    <td>int</td>
    <td>no</td>
    <td>0</td>
    <td></td>
    <td>
        <div>Time to wait for tasks to transition to &#x27;Completed&#x27;</div>
    </td>
    </tr>

    </table>
    </br>

.. _cv_task-examples-label:

Examples:
---------

::

    ---
    - name: Execute all tasks registered in cvp_configlets variable
      arista.cvp.cv_task:
        tasks: "{{ cvp_configlets.data.tasks }}"

    - name: Cancel a list of pending tasks
      arista.cvp.cv_task:
        tasks: "{{ cvp_configlets.data.tasks }}"
        state: cancelled

    # Execute all pending tasks and wait for completion for 60 seconds
    # In order to get a list of all pending tasks, execute cv_facts first
    - name: Update cvp facts
      arista.cvp.cv_facts:

    - name: Execute all pending tasks and wait for completion for 60 seconds
      arista.cvp.cv_task:
        port: '{{cvp_port}}'
        tasks: "{{ tasks }}"
        wait: 60



Author
~~~~~~

* Ansible Arista Team (@aristanetworks)
