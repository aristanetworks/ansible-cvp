# cv\_facts\_v1

Collect facts from CloudVision Portal.

Module added in version 2.9

<div class="contents" data-local="" data-depth="2">

</div>

## Synopsis

Returns the list of devices, configlets, containers and images

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
<td>gather_subset<br/><div style="font-size: small;"></div></td>
<td>list</td>
<td>no</td>
<td>[&#x27;default&#x27;]</td>
<td><ul><li>default</li><li>config</li></ul></td>
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

## Examples:

    ---
        # Collect CVP Facts as init process
    - name: "Gather CVP facts from {{inventory_hostname}}"
      arista.cvp.cv_facts_v1:
      register: cvp_facts

### Author

  - EMEA AS Team (@aristanetworks)

### Status

This module is flagged as **preview** which means that it is not
guaranteed to have a backwards compatible interface.
