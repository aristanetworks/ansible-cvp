# Ansible CVP Collection testing

## Available tests

- __Unit__: test with no CV interaction to test component: `tests/unit`
  - Tests with no API requirements
  - Tests objects & function with no abstraction
  - Unit Testing test each part of the program and shows that the individual parts are correct
  - Should be run at anytime by developers or CI

- __System__: test to run module backend component and which requires CV connection: `tests/system`
  - Testing based on Cloudvision API
  - Validate full integration with module inputs
  - Close to ansible module execution
  - Can be run as soon as you have access to test environment.

- __Lib__: to provides a safe place for fixtures, parametrizes, mook data: `tests/lib`
  - Provides helpers for unit and system
  - Store all tests data
  - Only available for pytest

### Test requirements

- Cloudvision server with some devices
- Pytest install as per [collection dev requirements](../ansible_collections/arista/cvp/requirements-dev.txt):
  - `pytest`
  - `pytest-cov`
  - `pytest-html`
  - `pytest-metadata`
  - `pytest-dependency`

```bash
pip install -r ../ansible_collections/arista/cvp/requirements-dev.txt
```

### Configuration file

Credentials are loaded from ENV variable from your shell:

```bash
# User token generated from Cloudvision instance
export ARISTA_AVD_CV_TOKEN='your-token-from-your-cv-instance'

# Cloudvision address
# Note: port is set to tcp/443
export ARISTA_AVD_CV_SERVER='lab.cv.io'

# Option to provision or not Cloudvision
# If set to False, fixture will not provision Cloudvision. By default set to True
export ARISTA_AVD_CV_PROVISION=False
```

## Run tests

### With initial Pytest CLI

```bash
# Configlet Unit testing
pytest -rA --cov-report term:skip-covered -v --cov-report term:skip-covered \
	--html=report.html --self-contained-html --cov-report=html --color yes \
	--cov=ansible_collections.arista.cvp.plugins.module_utils -m 'generic or api'\
	unit/test_configlet_input.py

# Configlet system testing
pytest -rA --cov-report term:skip-covered -v --cov-report term:skip-covered \
	--html=report.html --self-contained-html --cov-report=html --color yes \
	--cov=ansible_collections.arista.cvp.plugins.module_utils -m 'generic or api'\
	 system/test_cv_configlet.py

# Configlet system testing with only WARNING print in pytest.log
$ PYTEST_LOG_LEVEL=WARNING pytest -rA --cov-report term:skip-covered -v --cov-report term:skip-covered \
	--html=report.html --self-contained-html --cov-report=html --color yes \
	--cov=ansible_collections.arista.cvp.plugins.module_utils -m 'generic or api'\
	 system/test_cv_configlet.py
```

### Makefile usage

```bash
# Configlet Unit testing
$ make test TESTS=unit/test_configlet_input.py

# Configlet system testing
$ make test TESTS=system/test_cv_configlet.py

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


## Create test cases

### Generic build

- Add tags to run cases selectively

```python
@pytest.mark.api
@pytest.mark.configlet
```

> Tags must be defined in [pytest.ini](./pytest.ini) file

- Define fixture to configure your test case

```python
@pytest.mark.usefixtures("CvContainerTools_Manager")
```

- Add parametrize markers to pass data to tests

```python
@pytest.mark.parametrize("test_configlet", SYSTEM_CONFIGLETS_TESTS, ids=['system-configlet-tests01', 'system-configlet-tests02', 'system-configlet-tests03', 'system-configlet-tests04'])
@pytest.mark.parametrize("check_mode", [True, False], ids=['check_mode_on', 'check_mode_off'])
```

- Add conditiion to execute tests (Optional)

```python
@pytest.mark.skipif(user_token == 'unset_token', reason="Token is not set correctly")
```

- Add log before and after each API call to measure execution time

```python
logger = setup_custom_logger(name='configlet_unit')
def test_configlet_data_from_cv(self, test_configlet, check_mode):
    logger.info('Start to get configlet data from CV {}'.format(time_log()))
    cv_data = self.cv_configlet.get_configlet_data_cv(configlet_name=test_configlet['name'])
    logger.info('Got CV result')
```

### Parametrize options

Parametrize marker provides:

- Generate a list of value to test
- Can use a constant or a function
- Each entry from the list is passed to the test
- List of parametrize available in lib/parametrize.py

```python
# Using a CONSTANT element
@pytest.mark.parametrize("test_configlet", SYSTEM_CONFIGLETS_TESTS, ids=['system-configlet-tests01', 'system-configlet-tests02', 'system-configlet-tests03', 'system-configlet-tests04'])

# Using a list
@pytest.mark.parametrize("check_mode", [True, False], ids=['check_mode_on', 'check_mode_off'])

# Using a function
@pytest.mark.parametrize("configlet_inventory", generate_flat_data(type='configlet', mode='valid'))
```

### Unit test definition

Data are all available in [`lib.json_data.mook_data`](./lib/json_data.py)

- Dictionary based on `[ mode ][ type ]`.
- Easy to extend dataset used in tests.
  - Add your own entries
  - Automatically added to test with parametrize

```python
from .static_content import CONFIGLET_CONTENT

#######################################
# Configlet Examples
#######################################

mook_data["valid"]["configlet"] = [
        {"configlet_device01": "alias sib show version"},
        {"configlet-device01": "alias sib show version"},
        {"configlet-device_01": CONFIGLET_CONTENT},
]

mook_data["invalid"]["configlet"] = [
        {"configlet_device01": 100},
        {"configlet_device02": True},
        {"configlet_device02": False},
        {"configlet-device_01": "alias sib show version", 'version': 1},
]
```

Import parametrize in test cases

```python
# Import parametrize function
from lib.parametrize import generate_flat_data

class Test_ConfigletInput():

    @pytest.mark.parametrize("configlet_inventory", generate_flat_data(type='configlet', mode='valid'))
    def test_print_inventory_data(self, configlet_inventory):
        logger.debug('Inventory has {} configlets'.format(len(configlet_inventory)))
        logger.debug('Inventory is: {}'.format(to_nice_json(data=configlet_inventory)))
```

### System test definition

Data have to be representative and valid from CV.

- Should be defined under `lib/cvaas_<type>.py`
- Input data would be representative of ansible user's input.
- All tests entry should have expected result `_expected` suffix
- A parametrize function could be used (optional)
- Easy to extend dataset used in tests.
- Add your own entries
- Automatically added to test with parametrize

Example data for configlets:

```python
SYSTEM_CONFIGLETS_TESTS = [
    {
        'name': 'system-configlet-tests01',
        'config': CONFIGLET_CONTENT,
        'config_expected': CONFIGLET_CONTENT,
        'is_present_expected': True,
        'is_valid_expected': True
    },
    {
        'name': 'system-configlet-tests02',
        'config': 'alias sib show ip interfaces',
        'config_expected': 'alias sib show ip interfaces brief',
        'is_present_expected': True,
        'is_valid_expected': True
    },
    {
        'name': 'system-configlet-tests03',
        'config': 'alias sib2 show ip interfaces brief',
        'config_expected': 'alias sib2 show ip interfaces brief',
        'is_present_expected': False,
        'is_valid_expected': True
    },
    {
        'name': 'system-configlet-tests04',
        'config': CONFIGLET_CONTENT,
        'config_expected': CONFIGLET_CONTENT,
        'is_present_expected': False,
        'is_valid_expected': True
    }

]
```
