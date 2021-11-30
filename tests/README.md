# Ansible CVP Collection testing

## Availabale tests

- __Unit__: test with no CV interaction to test component: `tests/unit`
- __System__: test to run module backend component and which requires CV connection: `tests/system`
- __Lib__: to provides a safe place for fixtures, parametrizes, mook data: `tests/lib`

### Test requirements

- Cloudvision server with some devices
- Pytest install as per [collection dev requirements](../ansible_collections/arista/cvp/requirements-dev.txt):
  - pytest
  - pytest-cov
  - pytest-html
  - pytest-metadata
  - pytest-dependency

```bash
pip install -r ../ansible_collections/arista/cvp/requirements-dev.txt
```

### Configuration file

Credentials are loaded from ENV variable from your shell:

```bash
# User token generated from Cloudvision instance
export ARISTA_AVD_CV_TOKEN='your-token-from-your-cv-instance'

# Cloudvision address
export ARISTA_AVD_CV_SERVER='lab.cv.io'
```

## Run tests

A [Makefile](Makefile) is available to provide commands:

```bash
make test
```

It supports some options:

- `TESTS`: select path for tests to run. It can be a folder or a python file. By default runs `unit` and `system` test cases

```bash
make test TESTS=system/
```

- `TAG`: Select pytest tag to run. By defaul, run `api` and `generic`


## Tests Results

Results are print to your screen and also saved in reports:

- `report.html`: Pytest result with logging
- `htmlcov/index.html`: Coverage report
