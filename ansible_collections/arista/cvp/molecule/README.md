# CVP Unit test

This section provides a list of Ansible Cloudvision scenario executed during Continuous Integration to validate CVP integration.

## Ansible molecule

Molecule provides support for testing with multiple instances, operating systems and distributions, virtualization providers, test frameworks and testing scenarios. Molecule encourages an approach that results in consistently developed roles that are well-written, easily understood and maintained.

## Scenario

Current molecule implementation provides following scenario:

- dhcp_configuration

## Manual execution

To manually run molecule testing, follow commands:

```shell
# Install development requirements
$ pip install -r development/requirements-dev.txt

# Move to AVD collection
$ ansible-avd/ansible_collections/arista/cvp

# Run molecule for a given test
$ molecule test -s <scenario-name>

# Run molecule for all test
$ molecule test --all
```

## Continuous Integration

These scenario are all included in github actions and executed on `push` and `pull_request` when a file under `roles` and/or `molecule` is updated.

```yaml
name: Ansible Molecule
on:
  push:
  pull_request:
    paths:
      - 'ansible_collections/arista/cvp/roles/**'
      - 'ansible_collections/arista/cvp/molecules/**'
      - 'requirements.txt'
jobs:
  molecule:
    runs-on: ubuntu-latest
    env:
      PY_COLORS: 1 # allows molecule colors to be passed to GitHub Actions
      ANSIBLE_FORCE_COLOR: 1 # allows ansible colors to be passed to GitHub Actions
    strategy:
      fail-fast: true
      matrix:
        avd_scenario:
          - dhcp_configuration
    steps:
      - name: Checkout repository
        uses: actions/checkout@v2

      - name: Run molecule action
        uses: inetsix/molecule-collection-actions@master
        with:
          molecule_parentdir: 'ansible_collections/arista/cvp'
          molecule_command: 'test'
          molecule_args: '-s ${{ matrix.avd_scenario }}'
          pip_file: 'requirements.txt'
```