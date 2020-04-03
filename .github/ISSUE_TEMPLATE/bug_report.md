---
name: Issue template
about: Report an issue
title: ""
labels: Triage
assignees: ''

---

<!---
Verify first that your issue/request is not already reported on GitHub. -->

## Issue Type

<!--- What types of changes does your code introduce? Put an `x` in all the boxes that apply: -->
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] Documentation Report
- [ ] Code style update (formatting, renaming)
- [ ] Refactoring (no functional changes)
- [ ] Other (please describe):


## Summary

<!--- Explain the problem briefly -->

## Role or Module Name

<!--- Insert, BELOW THIS COMMENT, the name of the module, plugin, task or feature
-->

__Module name:__ `module name`

`arista.cvp` collection and Python libraries version

<!--- Paste, BELOW THIS COMMENT, verbatim output from "ansible --version" and  "pip freeze" between quotes below Also provide the version of arista.avd collection-->

```shell
# Ansible version
$ ansible --version

# list of python packages if required.
$ pip freeze

```

## OS / Environment

__Cloudvision version__

<!-- Define which CVP version is your target -->

__EOS Version__

<!-- Define which version of EOS and which platform you are using -->

__OS running Ansible__

<!-- Define which OS and version you use to run ansible -->


## Steps to reproduce
<!--- For bugs, show exactly how to reproduce the problem, using a minimal test-case.
For new features, show how the feature would be used. -->

<!--- Paste example playbooks or commands between quotes below -->
```yaml
---
```

<!--- You can also paste gist.github.com links for larger files -->

### Expected results

<!--- What did you expect to happen when running the steps above? -->

```shell
$
```

### Actual results
<!--- What actually happened? If possible run with extra verbosity (-vvvv) -->

<!--- Paste verbatim command output between quotes below -->
```shell
$
```
