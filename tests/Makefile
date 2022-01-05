CURRENT_DIR = $(shell pwd)
TESTS ?= .
TAG ?= generic or api
TEST_OPT = -rA -q --cov-report term:skip-covered
REPORT = -v --cov-report term:skip-covered --html=report.html --self-contained-html --cov-report=html --color yes
COVERAGE = --cov=ansible_collections.arista.cvp.plugins.module_utils
CLI_LOGGING ?= INFO
PYTEST_LOGGING ?= DEBUG

.PHONY: test
test:  ## Run Pytest in verbose mode with CLI report only for all tests. By default only unit and system, but can be changed by declaring  TEST_PATH variable and its value
	PYTEST_LOG_LEVEL=$(PYTEST_LOGGING) pytest $(TEST_OPT) $(REPORT) $(COVERAGE) --log-cli-level=$(CLI_LOGGING) -m '$(TAG)' $(TESTS)
