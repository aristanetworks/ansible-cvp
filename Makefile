CURRENT_DIR = $(shell pwd)
DOCKER_NAME ?= ansible-cvp
DOCKER_TAG ?= latest
# ansible-test path
ANSIBLE_TEST ?= $(shell which ansible-test)
# option to run ansible-test sanity: must be either venv or docker (default is docker)
ANSIBLE_TEST_MODE ?= docker

.PHONY: help
help: ## Display help message (*: main entry points / []: part of an entry point)
	@grep -E '^[0-9a-zA-Z_-]+\.*[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

#########################################
# Ansible Collection actions		 	#
#########################################
.PHONY: collection-build
collection-build: ## Build arista.cvp collection locally
	ansible-galaxy collection build --force arista/cvp

.PHONY: collection-install
collection-install: ## Install arista.cvp collection to default location (~/.ansible/collections/ansible_collections)
	for collection in *.tar.gz; do \
		ansible-galaxy collection install $$collection ;\
	done

#########################################
# Code Validation using ansible-test 	#
#########################################

.PHONY: sanity sanity-lint sanity-import sanity-info
sanity: sanity-build sanity-info-env sanity-lint sanity-import sanity-clean ## Run ansible-test sanity validation.
sanity-info: sanity-build sanity-info-env sanity-clean ## Show information about ansible-test
sanity-lint: sanity-build code-linting-ansible sanity-clean ## Run ansible-test sanity for code sanity
sanity-import: sanity-build code-import-ansible sanity-clean ## Run ansible-test sanity for code import

.PHONY: sanity-build
sanity-build: ## Configure repository to run ansible-test
	mkdir ansible_collections
	cp -r arista ansible_collections

.PHONY: sanity-info-env
sanity-info-env:
	cd ansible_collections/arista/cvp/ ; ansible-test env

.PHONY: code-linting-ansible
code-linting-ansible:
	cd ansible_collections/arista/cvp/ ; \
	ansible-test sanity --requirements --$(ANSIBLE_TEST_MODE) --skip-test import

.PHONY: code-import-ansible
code-import-ansible:
	cd ansible_collections/arista/cvp/ ; \
	ansible-test sanity --requirements --$(ANSIBLE_TEST_MODE) --test import

.PHONY: sanity-clean
sanity-clean: ## Remove ansible-test setup from local repository
	rm -rf ansible_collections

#########################################
# Docker actions					 	#
#########################################
.PHONY: build-docker2.7
build-docker2.7: ## Build docker image for python 2.7
	docker build -f Dockerfile-2.7 -t $(DOCKER_NAME):$(DOCKER_TAG)-2.7 .

.PHONY: build-docker3
build-docker3: ## Build docker image for python 3.0
	docker build -f Dockerfile-3 -t $(DOCKER_NAME):$(DOCKER_TAG) .

#########################################
# Misc Actions 							#
#########################################

.PHONY: linting
linting: ## Run pre-commit script for python code linting using pylint
	sh .github/pre-commit

.PHONY: github-configure-ci
github-configure-ci: ## Configure CI environment to run GA (Ubuntu:latest LTS)
	sudo apt-get update
	sudo apt-get install -y gnupg2
	sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 93C4A3FD7BB9C367
	sudo echo "deb http://ppa.launchpad.net/ansible/ansible/ubuntu bionic main" | sudo tee /etc/apt/sources.list.d/ansible.list
	sudo echo "deb-src http://ppa.launchpad.net/ansible/ansible/ubuntu bionic main" | sudo tee -a /etc/apt/sources.list.d/ansible.list
	sudo apt-get update
	sudo apt-get install ansible-test
	sudo pip install --upgrade wheel
	sudo pip install -r requirements.txt

.PHONY: setup-repository
setup-repository: ## Install python requirements
	pip install --upgrade wheel
	pip install -r requirements.txt
	pip install -r requirements.dev.txt
