CURRENT_DIR = $(shell pwd)
TAG ?= -m 'generic, api'
TEST_PATH ?= unit
TEST_OPT = -v --cov-report term:skip-covered
REPORT = -v --cov-report term:skip-covered --html=report.html --self-contained-html --cov-report=html --color yes
COVERAGE = --cov=ansible_collections.arista.cvp.plugins.module_utils.container_tools --cov=ansible_collections.arista.cvp.plugins.module_utils.configlet_tools --cov=ansible_collections.arista.cvp.plugins.module_utils.generic_tools  --cov=ansible_collections.arista.cvp.plugins.module_utils.device_tools  --cov=ansible_collections.arista.cvp.plugins.module_utils.response  --cov=ansible_collections.arista.cvp.plugins.module_utils.schema_v3

AUTH_CONFIG_FILE = $(TEST_PATH)/config.py

define AUTH_CONFIG
#!/usr/bin/python
# coding: utf-8 -*-

username = "ansible"
password = "ansible"
server = "cv-server-ip"
endef
export AUTH_CONFIG

.PHONY: ci-test
ci-test:  ## Run Pytest with only local tests and no API interactions
	cp unit/pytest.ini .
	pytest -v --cov-report term:skip-covered -m 'generic'
	rm pytest.ini

.PHONY: ci-report
ci-report:  ## Run Pytest with reporting for CI
	cp unit/pytest.ini .
	pytest $(REPORT) $(COVERAGE) -m 'generic' $(TEST_PATH)
	rm pytest.ini

.PHONY: test
test:  ## Run Pytest in verbose mode with CLI report only for basic tests
	pytest $(TEST_OPT) $(COVERAGE) $(TAG) $(TEST_PATH)

.PHONY: test-all
test-all:  ## Run Pytest in verbose mode with CLI report only for all tests
	pytest $(TEST_OPT) $(COVERAGE) $(TEST_PATH)

.PHONY: report
report:  ## Run Pytest and generate HTML report + code coverage
	pytest $(REPORT) $(COVERAGE) $(TAG) $(TEST_PATH)

.PHONY: report-all
report-all:  ## Run Pytest and generate HTML report + code coverage
	pytest $(REPORT) $(COVERAGE) $(TEST_PATH)

.PHONY: report-api
report-api:  ## Run Pytest and generate HTML report + code coverage
	pytest $(REPORT) $(COVERAGE) -m 'generic,api' $(TEST_PATH)

.PHONY: report-builder
report-builder:  ## Run Pytest and generate HTML report + code coverage
	pytest $(REPORT) $(COVERAGE) -m 'builder' $(TEST_PATH)

.PHONY: config.py
config.py:  ## Generate Auth Configuration file
	@echo "Generate config.py for Cloudvision auth"
	@echo "$$AUTH_CONFIG" > $(AUTH_CONFIG_FILE)
	@echo "---"
	@echo "Update unit/config.py with your credentials"
