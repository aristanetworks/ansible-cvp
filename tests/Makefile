CURRENT_DIR = $(shell pwd)
TESTS ?= .
TAG ?= generic or api
TEST_OPT = -rA --cov-report term:skip-covered
REPORT = -v --cov-report term:skip-covered --html=report.html --self-contained-html --cov-report=html --color yes
COVERAGE = --cov=ansible_collections.arista.cvp.plugins.module_utils
LOGGING ?= INFO

.PHONY: test
test:  ## Run Pytest in verbose mode with CLI report only for all tests. By default only unit and system, but can be changed by declaring  TEST_PATH variable and its value
	pytest $(TEST_OPT) $(REPORT) $(COVERAGE) --log-cli-level=$(LOGGING) -m '$(TAG)' $(TESTS)
