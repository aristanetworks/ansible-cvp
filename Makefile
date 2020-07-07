CURRENT_DIR = $(shell pwd)
CONTAINER_NAME = avdteam/base
DOCKER_TAG = centos-7
CONTAINER = $(CONTAINER_NAME):$(DOCKER_TAG)
HOME_DIR = $(shell pwd)
HOME_DIR_DOCKER = '/home/docker'
# ansible-test path
ANSIBLE_TEST ?= $(shell which ansible-test)
# option to run ansible-test sanity: must be either venv or docker (default is docker)
ANSIBLE_TEST_MODE ?= docker
# Root path for MKDOCS content
WEBDOC_BUILD = ansible_collections/arista/cvp/docs/_build

.PHONY: help
help: ## Display help message (*: main entry points / []: part of an entry point)
	@grep -E '^[0-9a-zA-Z_-]+\.*[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

#########################################
# Ansible Collection actions		 	#
#########################################
.PHONY: collection-build
collection-build: ## Build arista.cvp collection locally
	ansible-galaxy collection build --force ansible_collections/arista/cvp

.PHONY: collection-install
collection-install: ## Install arista.cvp collection to default location (~/.ansible/collections/ansible_collections)
	for collection in *.tar.gz; do \
		ansible-galaxy collection install $$collection ;\
	done

#########################################
# Code Validation using ansible-test 	#
#########################################

.PHONY: sanity
sanity: sanity-info sanity-lint sanity-import ## Run ansible-test sanity validation.

.PHONY: sanity-info
sanity-info: ## Show information about ansible-test
	cd ansible_collections/arista/cvp/ ; ansible-test env

.PHONY: sanity-lint
sanity-lint: ## Run ansible-test sanity for code sanity
	cd ansible_collections/arista/cvp/ ; \
	ansible-test sanity --requirements --$(ANSIBLE_TEST_MODE) --skip-test import ; \
	rm -rf tests/output/

.PHONY: sanity-import
sanity-import: ## Run ansible-test sanity for code import
	cd ansible_collections/arista/cvp/ ; \
	ansible-test sanity --requirements --$(ANSIBLE_TEST_MODE) --test import ; \
	rm -rf tests/output/


#########################################
# Docker actions					 	#
#########################################
.PHONY: run-docker
run-docker: ## Connect to docker container
	docker run --rm -it \
		-v $(HOME)/.ssh:$(HOME_DIR_DOCKER)/.ssh \
		-v $(HOME)/.gitconfig:$(HOME_DIR_DOCKER)/.gitconfig \
		-v $(HOME_DIR)/:/projects \
		-v /etc/hosts:/etc/hosts $(CONTAINER)

.PHONY: build-docker
build-docker: ## [DEPRECATED] visit https://github.com/arista-netdevops-community/docker-avd-base to build image
	#docker build --no-cache -t $(CONTAINER) .
	echo ''; echo 'Deprecated command -- visit https://github.com/arista-netdevops-community/docker-avd-base to build image'; echo ''

.PHONY: build-docker3
build-docker3: ## [DEPRECATED] visit https://github.com/arista-netdevops-community/docker-avd-base to build image
	#docker build --no-cache -t $(CONTAINER) .
	echo ''; echo 'Deprecated command -- visit https://github.com/arista-netdevops-community/docker-avd-base to build image'; echo ''


#########################################
# Documentation actions					#
#########################################
.PHONY: webdoc
webdoc: ## Build documentation to publish static content
	( cd $(WEBDOC_BUILD) ; \
	python ansible2rst.py ; \
	find . -name 'cv_*.rst' -exec pandoc {} --from rst --to gfm -o ../modules/{}.md \;)
	cp $(CURRENT_DIR)/contributing.md $(WEBDOC_BUILD)/.. ;\
	cd $(CURRENT_DIR)
	mkdocs build -f mkdocs.yml


#########################################
# Misc Actions 							#
#########################################

.PHONY: linting
linting: ## Run pre-commit script for python code linting using pylint
	sh .github/pre-commit

.PHONY: pre-commit
pre-commit: ## Execute pre-commit validation for staged files
	pre-commit run

.PHONY: pre-commit-all
pre-commit-all: ## Execute pre-commit validation for all files
	pre-commit run --all-files

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

.PHONY: install-requirements
install-requirements: ## Install python requirements
	pip install --upgrade wheel
	pip install -r requirements.txt
	pip install -r development/requirements-dev.txt