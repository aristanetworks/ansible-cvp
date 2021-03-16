CURRENT_DIR = $(shell pwd)
TAG ?= 'not delete and not create'
TEST ?= unit
REPORT = --html=report.html --self-contained-html --cov=ansible_collections.arista.cvp.plugins.module_utils.container_tools --cov=ansible_collections.arista.cvp.plugins.module_utils.configlet_tools --cov=ansible_collections.arista.cvp.plugins.module_utils.generic_tools  --cov=ansible_collections.arista.cvp.plugins.module_utils.device_tools  --cov=ansible_collections.arista.cvp.plugins.module_utils.response  --cov=ansible_collections.arista.cvp.plugins.module_utils.schema --cov-report=html --color yes

.PHONY: test
test:  ## Run Pytest in verbose mode with CLI report only
	pytest -v -m $(TAG) $(TEST)

.PHONY: report
report:  ## Run Pytest and generate HTML report + code coverage
	pytest $(REPORT) -m $(TAG) $(TEST)
