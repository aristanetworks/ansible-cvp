CURRENT_DIR = $(shell pwd)
DOCKER_NAME ?= ansible-cvp
DOCKER_TAG ?= latest

.PHONY: help build validate docker-image clean code-linting-ansible build-test code-import pre-commit code-validate code-import-ansible

help: ## Display help message (*: main entry points / []: part of an entry point)
	@grep -E '^[0-9a-zA-Z_-]+\.*[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

#########################################
# Ansible Collection actions		 	#
#########################################

collection-build: ## * Build arista.cvp collection locally
	ansible-galaxy collection build --force arista/cvp

collection-install: ## * Install arista.cvp collection to default location (~/.ansible/collections/ansible_collections)
	for collection in *.tar.gz; do \
		ansible-galaxy collection install $$collection ;\
	done

#########################################
# Code Validation using ansible-test 	#
#########################################
code-validate: build-test code-linting-ansible code-clean ## * Configure content to run ansible-test and execute tests except import
code-import: build-test code-import-ansible code-clean ## * Configure content to run ansible-test and execute import test


build-test: ## [part of code-validate / code-import] Configure repository to run ansible-test
	mkdir ansible_collections
	cp -r arista ansible_collections


code-linting-ansible: ## [part of code-validate / code-import] Run ansible-test sanity in venv for code sanity
	cd ansible_collections/arista/cvp/ && ansible-test sanity --venv --skip-test import


code-import-ansible: ## [part of code-validate / code-import] Run ansible-test sanity in venv for code import
	cd ansible_collections/arista/cvp/ && ansible-test sanity --venv --test import


code-clean: ## [part of code-validate / code-import] Remove ansible-test setup from local repository
	rm -rf ansible_collections

#########################################
# Docker actions					 	#
#########################################

build-docker2.7: ## * Build docker image for python 2.7
	docker build -f Dockerfile-2.7 -t $(DOCKER_NAME):$(DOCKER_TAG)-2.7 .

build-docker3: ## * Build docker image for python 3.0
	docker build -f Dockerfile-3 -t $(DOCKER_NAME):$(DOCKER_TAG) .

#########################################
# Misc Actions 							#
#########################################

lint-python: ## * Run pre-commit script for python code linting using pylint
	sh .github/pre-commit
