# cv_task_v3

Execute or Cancel CVP Tasks.

Module added in version 3.0.0

<div class="contents" local="" depth="2">

</div>

## Synopsis

CloudVision Portal Task module to action pending tasks on CloudVision

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

</table>
</br>

## Examples:

    ---
    - name: Execute all tasks registered in cvp_configlets variable
      arista.cvp.cv_task_v3:
        tasks: "{{ cvp_configlets.taskIds }}"

    - name: Cancel a list of pending tasks
      arista.cvp.cv_task_v3:
        tasks: ['666', '667']
        state: cancelled

### Author

- Ansible Arista Team (@aristanetworks)
