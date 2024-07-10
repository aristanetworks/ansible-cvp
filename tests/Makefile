CURRENT_DIR = $(shell pwd)
TESTS ?= .
TAG ?= generic or api
TEST_OPT = -rA -q --cov-report term:skip-covered
REPORT = -v --cov-report term:skip-covered --html=report.html --self-contained-html --cov-report=html --color yes
COVERAGE = --cov=ansible_collections.arista.cvp.plugins.module_utils
CLI_LOGGING ?= INFO
PYTEST_LOGGING ?= DEBUG

.PHONY: unit-tests
unit-tests:  ## Run python unit tests in verbose mode with CLI report only for all tests
	export PYTEST_LOG_LEVEL=$(PYTEST_LOGGING) && pytest ./unit $(TEST_OPT) $(REPORT) $(COVERAGE) --log-cli-level=$(CLI_LOGGING) -m '$(TAG)' $(TESTS)

.PHONY: system-tests
system-tests:  ## Run python system tests in verbose mode with CLI report only for all tests
	export PYTEST_LOG_LEVEL=$(PYTEST_LOGGING) && pytest ./system $(TEST_OPT) $(REPORT) $(COVERAGE) --log-cli-level=$(CLI_LOGGING) -m '$(TAG)' $(TESTS)
