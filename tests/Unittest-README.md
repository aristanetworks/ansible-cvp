<!--
  ~ Copyright (c) 2023-2024 Arista Networks, Inc.
  ~ Use of this source code is governed by the Apache License 2.0
  ~ that can be found in the LICENSE file.
  -->

# Ansible CVP Unit testing

## Unit test structure

The structure of unit tests are described below

- **`tests/unit`**: Contains all unittests
  - Filename start with `test_` followed by the name of the file it's testing.
    - For example: Unittests for `ansible_collection/arista/cvp/plugins/module_utils/device_tools.py` will be under `tests/unit/test_cv_device_tools.py`
  - `tests/unit/conftest.py`: This is a special python script that defines all the fixtures available for use while testing `ansible-cvp` modules
- **`tests/lib`**: Contains library functions
  - **`tests/lib/mockMagic.py`**: Contains mock cvprac functions
    - Note: the name and signature of the mock functions matches original cvprac functions
- **`tests/data`**: Contains faked datasets for use by the mocked cvprac functions

## Write unittests

### General guidelines

- Create your unittest file under `tests/unit` following the naming convention mentioned in the [above section](#unit-test-structure).
- If the file is already present, add your unittests in the file.
- Each function in the **file-under-test** (example: `ansible_collection/arista/cvp/plugins/module_utils/device_tools.py`) should be placed in a class of its own with the class name starting with `Test` followed by the function's name.

```python
class TestValidateConfig():
    """
    Contains unit tests for validate_config()
    """
...
```

- Add tags to run cases selectively.

```python
@pytest.mark.api
@pytest.mark.configlet
```

> Tags must be defined in [pytest.ini](./pytest.ini) file.
> Tags can be added at `class` or `test` level.

```python
@pytest.mark.api
class TestFoo(..):
  ...

class TestBar(...):
  @pytest.mark.configlet
  def test_bar_scenario1(...):
    ...
```

- Place the test suite within this class.

```python
class TestValidateConfig():
    """
    Contains unit tests for validate_config()
    """
    def test_validate_config_warning(...):
      pass
    def test_validate_config_error(...):
      pass
    ....
```

### Fixtures

Fixtures are used to prepare the context for the tests. It can include environment (*`CVP` configured with some topology*) as well as content (*`CVP` configured with some configlet*). Some important fixures are described below. For more information, please refer to the [conftest](./unit/conftest.py) file.

- `apply_mock()`: Factory function to return a method to apply mocker.patch() on paths
- `mock_cvpClient()`: mock cvprac classes and objects

For more info on pytest fixtures refer to the official [pytest documentation](https://docs.pytest.org/en/7.1.x/how-to/fixtures.html)

#### How to use Fixtures

A test function can request a fixture by declaring them as arguments in the function definition.
For example:

```python
def test_foo(apply_mock):
  mock_foo = apply_mock("path.to.original.foo")
  ...
```

### Setup and Teardown functions

Setup and Teardown functions are used to set up and clear up state for testing. They are executed before and after every test in a test suite.

#### How to write setup and teardown function

Setup/Teardown functions can be written as a fixture and called at the beginning and end of each test.

```python
@pytest.fixture
def setup(fixture1, fixture2):
  # use fixture1 and fixture2
  ...
  m1 = fixture1(...)
  m2 = fixture2(...)
  ...
  return m1, m2

def test_foo(setup, ...):
  mock1, mock2 = setup
  ...
```

### Parameterizing the tests

Pytest allows you to easily parameterize tests, in which case they will be called multiple times, each time with a different set of inputs.

Use the decorator `@pytest.mark.parameterize` to parametrize arguments for a test function.

```python
@pytest.mark.parametrize("arg1, arg2",
        [pytest.param(
            input1, input2,
            id="scenario1"
        ),
        pytest.param(
            input3, input4,
            id="scenario2"
        ),
        pytest.param(
            input5, input6,
            id="scenario3"
        ),
        ])
    def test_foo(self, fixture1, arg1, arg2):
      ...
```

## Run tests

### With initial Pytest CLI

```bash
# Configlet Unit testing
pytest -rA --cov-report term:skip-covered -v --cov-report term:skip-covered \
 --html=report.html --self-contained-html --cov-report=html --color yes \
 --cov=ansible_collections.arista.cvp.plugins.module_utils -m 'generic or api'\
 unit/<test-file-name>.py
```

### Makefile usage

```bash
# Configlet Unit testing
make test TESTS=unit/test_configlet_input.py

# Run all tests related to configlets with logging in CLI set to INFO
make test TAG='configlet' CLI_LOGGING=INFO

# Run all tests related to configlets with logging in CLI set to INFO and pytest.log set to WARNING
make test TAG='configlet' CLI_LOGGING=INFO PYTEST_LOGGING=WARNING
```

### Custom Makefile options

- `TESTS`: Which tests to run. (By default `.`)
- `TAG`: Which tag to run. (By default `generic or api`)
- `CLI_LOGGING`: Log verbosity print out to your console
- `PYTEST_LOGGING`: Log level used to report in pytest.log

## Tests Results

Results are printed to your screen and also saved in reports:

- `report.html`: Pytest result with logging
- `htmlcov/index.html`: Coverage report

> More information on pytest, can be found at the official [pytest documentation](https://docs.pytest.org/).
