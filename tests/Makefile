CURRENT_DIR = $(shell pwd)
# TAG ?= -m 'generic, api'
TAG ?=
TEST_PATH ?= unit
TEST_OPT = -v --cov-report term:skip-covered
REPORT = -v --cov-report term:skip-covered --html=report.html --self-contained-html --cov-report=html --color yes
COVERAGE = --cov=ansible_collections.arista.cvp.plugins.module_utils.container_tools --cov=ansible_collections.arista.cvp.plugins.module_utils.configlet_tools --cov=ansible_collections.arista.cvp.plugins.module_utils.generic_tools  --cov=ansible_collections.arista.cvp.plugins.module_utils.device_tools  --cov=ansible_collections.arista.cvp.plugins.module_utils.response  --cov=ansible_collections.arista.cvp.plugins.module_utils.schema_v3

AUTH_CONFIG_FILE = lib/config.py

define AUTH_CONFIG
#!/usr/bin/python
# coding: utf-8 -*-

username = "< username >"
password = "< password >"
server = "< cloudvision ip >"
endef
export AUTH_CONFIG


.PHONY: ci
ci:  ## Run Pytest with reporting for CI: No API interaction
	pytest $(REPORT) $(COVERAGE) -m 'generic' $(TEST_PATH)

.PHONY: test
test:  ## Run Pytest in verbose mode with CLI report only for all tests. By default only unit, but chan be changed with TEST_PATH
	pytest $(TEST_OPT) $(REPORT) $(COVERAGE) $(TAG) $(TEST_PATH)

.PHONY: test-api
test-api:  ## Run Pytest and generate HTML report + code coverage for generic and api test cases.
	pytest $(REPORT) $(COVERAGE) -m 'generic,api'

.PHONY: config.py
config.py:  ## Generate Auth Configuration file. Please edit result to set your credentials
	@echo "Generate config.py for Cloudvision auth"
	@echo "$$AUTH_CONFIG" > $(AUTH_CONFIG_FILE)
	@echo "---"
	@echo "Update lib/config.py with your credentials"
