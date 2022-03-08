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
# Python version to use in testing.
ANSIBLE_TEST_PYTHON ?= 3.6
# Root path for MKDOCS content
WEBDOC_BUILD = ansible_collections/arista/cvp/docs/_build
COMPOSE_FILE ?= development/docker-compose.yml
MUFFET_TIMEOUT ?= 60

.PHONY: help
help: ## Display help message (*: main entry points / []: part of an entry point)
	@grep -E '^[0-9a-zA-Z_-]+\.*[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

#########################################
# Ansible Collection actions		 	#
#########################################
.PHONY: collection-build
collection-build: ## Build arista.cvp collection locally
	rm -rf ansible_collections/arista/cvp/molecule/ ; \
	ansible-galaxy collection build --force ansible_collections/arista/cvp ; \
	git checkout ansible_collections/arista/cvp/molecule/

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
	ansible-test sanity -v --requirements --$(ANSIBLE_TEST_MODE) --skip-test yamllint --python $(ANSIBLE_TEST_PYTHON); \
	rm -rf tests/output/

.PHONY: sanity-import
sanity-import: ## Run ansible-test sanity for code import
	cd ansible_collections/arista/cvp/ ; \
	ansible-test sanity --requirements --$(ANSIBLE_TEST_MODE) --python $(ANSIBLE_TEST_PYTHON) --test import ; \
	rm -rf tests/output/

.PHONY: galaxy-importer
galaxy-importer:  ## Run galaxy importer tests
	rm -f *.tar.gz && \
	ansible-galaxy collection build --force ansible_collections/arista/cvp && \
	python -m galaxy_importer.main *.tar.gz

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
	find . -name 'cv_*_v3.rst' -exec pandoc {} --from rst --to gfm -o ../modules/{}.md \;)
	cp $(CURRENT_DIR)/contributing.md $(WEBDOC_BUILD)/.. ;\

.PHONY: check-cvp-404
check-cvp-404: ## Check local 404 links for AVD documentation
	docker run --rm --network container:webdoc_cvp raviqqe/muffet:1.5.7 http://127.0.0.1:8001 -e ".*fonts.googleapis.com.*" -e ".*fonts.gstatic.com.*" -e ".*edit.*" -f --limit-redirections=3 --timeout=${MUFFET_TIMEOUT}

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
github-configure-ci: github-configure-ci-python3 github-configure-ci-ansible ## Configure CI environment to run GA (Ubuntu:latest LTS)

.PHONY: github-configure-ci-ansible
github-configure-ci-ansible: ## Install Ansible Test 2.9 on GA (Ubuntu:latest LTS)
	sudo apt-get update
	sudo apt-get install -y gnupg2
	sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 93C4A3FD7BB9C367
	sudo echo "deb http://ppa.launchpad.net/ansible/ansible-2.9/ubuntu bionic main" | sudo tee /etc/apt/sources.list.d/ansible.list
	sudo echo "deb-src http://ppa.launchpad.net/ansible/ansible-2.9/ubuntu bionic main" | sudo tee -a /etc/apt/sources.list.d/ansible.list
	sudo apt-get update
	sudo DEBIAN_FRONTEND=noninteractive apt-get install -q -y ansible-test

.PHONY: github-configure-ci-python3
github-configure-ci-python3: ## Configure Python3 environment to run GA (Ubuntu:latest LTS)
	sudo apt-get update
	sudo apt-get upgrade -y
	sudo apt-get install -y python3 python3-pip git python3-setuptools
	sudo update-alternatives --install /usr/bin/python python /usr/bin/python3 10

.PHONY: install-requirements
install-requirements: ## Install python requirements for generic purpose
	pip3 install --upgrade wheel pip
	pip3 install -r ansible_collections/arista/cvp/requirements.txt
	pip3 install -r ansible_collections/arista/cvp/requirements-dev.txt

.PHONY: install-docker
install-docker: ## Install docker
	sudo apt install -q -y apt-transport-https ca-certificates curl software-properties-common
	curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
	sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable"
	sudo apt update
	sudo apt install -q -y docker-ce
