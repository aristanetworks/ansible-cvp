# Ansible CVP Collection testing

## Configure Pytest

### Test requirements

- Cloudvision server with some devices
- Pytest install as per [collection dev requirements](../ansible_collections/arista/cvp/requirements-dev.txt)

### Configuration file

Configure a configuration file under __tests/unit__ to set your Cloudvision information:

- Username
- Password
- Server

```python
#!/usr/bin/python
# coding: utf-8 -*-

username = "< Your CV username >"
password = "< Your CV password >"
server = "< your CV server IP >"
```

A command alias is available in Makefile under __tests__:

```bash
$ make config.py
Generate config.py for Cloudvision auth
---
Update unit/config.py with your credentials
```

## Run tests

A [Makefile](Makefile) is available to provide commands:

- `test`: Run pytest to execute all tests with `generic` and `api` flags.
- `test-all`: Run pytest to execute all tags.
- `repor`: Run pytest to execute all tests with `generic` and `api` flags + HTML reports (pytest + codecoverage).
- `report-all`: Run pytest to execute all tags + HTML reports (pytest + codecoverage).
