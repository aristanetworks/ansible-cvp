CURRENT_DIR = $(shell pwd)
DOCKER_NAME ?= ansible-cvp
DOCKER_TAG ?= latest

.PHONY: build validate docker-image clean code-linting-ansible build-test code-import pre-commit code-validate code-import-ansible

#########################################
# Ansible Collection actions		 	#
#########################################

collection-build:
	ansible-galaxy collection build --force arista/cvp

collection-install:
	for collection in *.tar.gz; do \
		ansible-galaxy collection install $$collection ;\
	done

#########################################
# Code Validation using ansible-test 	#
#########################################
code-validate: build-test code-linting-ansible code-clean
code-import: build-test code-import-ansible code-clean

build-test:
	mkdir ansible_collections
	cp -r arista ansible_collections

code-linting-ansible:
	cd ansible_collections/arista/cvp/ && ansible-test sanity --venv --skip-test import

code-import-ansible:
	cd ansible_collections/arista/cvp/ && ansible-test sanity --venv --test import

code-clean:
	rm -rf ansible_collections

#########################################
# Docker actions					 	#
#########################################

docker-image2.7:
	docker build -f Dockerfile-2.7 -t $(DOCKER_NAME):$(DOCKER_TAG)-2.7 .

docker-image3:
	docker build -f Dockerfile-3 -t $(DOCKER_NAME):$(DOCKER_TAG) .

#########################################
# Misc Actions 							#
#########################################

lint-python:
	sh .github/pre-commit