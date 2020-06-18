# cv\_task

Execute or Cancel CVP Tasks.

Module added in version 2.9

<div class="contents" data-local="" data-depth="2">

</div>

## Synopsis

C l o u d V i s o n

P o r t a l

T a s k

m o d u l e

## Module-specific Options

The following options may be specified for this module:

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

## Examples:

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

### Author

  - EMEA AS Team (@aristanetworks)

### Status

This module is flagged as **preview** which means that it is not
guaranteed to have a backwards compatible interface.
