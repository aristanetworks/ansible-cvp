
MOLECULE ?= cv_configlet_loose
ANSIBLE_OPTIONS ?=

.PHONY: help
help: ## Display help message
	@grep -E '^[0-9a-zA-Z_-]+\.*[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

###############################################################################
# 			docker containers target									      #
###############################################################################

.PHONY: run
run: ## Execute molecule TEST sequence. By default eos_cli_config_gen. Can be set with MOLECULE=
	cd .. && \
	molecule test --scenario-name $(MOLECULE) -- $(ANSIBLE_OPTIONS)

.PHONY: converge
converge: ## Execute molecule CONVERGE sequence. By default eos_cli_config_gen. Can be set with MOLECULE=
	cd .. && \
	molecule converge --scenario-name $(MOLECULE) -- $(ANSIBLE_OPTIONS)

.PHONY: refresh-facts
refresh-facts: ## Run all molecule scenarios
	@for MOLECULE_SCENARIO in * ; do \
        if [ -d "$$MOLECULE_SCENARIO" ]; then\
        echo "Run scenrario for "$$MOLECULE_SCENARIO && \
		cd .. ; \
		molecule converge --scenario-name $$MOLECULE_SCENARIO -- $(ANSIBLE_OPTIONS) ; \
		cd ./molecule ; \
        fi \
    done

.PHONY: commit-facts
commit-facts: ## Commit updated facts for CI
	git status --short
	git add .
	git commit --no-verify -m 'ci(molecule): Update artifacts' ./

.PHONY: test-git-status
test-git-status: ## Run post molecule script to check git status
	sh ../../../../.github/git-repo-state-monitor.sh

.PHONY: sync-facts
sync-facts: refresh-facts commit-facts ## Refresh and commit CI artifacts

.PHONY: cleanup
destroy: ## destroy all molecule scenarios
	@for MOLECULE_SCENARIO in * ; do \
        if [ -d "$$MOLECULE_SCENARIO" ]; then\
        echo "Run scenrario for "$$MOLECULE_SCENARIO && \
		cd .. ; \
		molecule cleanup --scenario-name $$MOLECULE_SCENARIO -- $(ANSIBLE_OPTIONS) ; \
		cd ./molecule ; \
        fi \
    done

.PHONY: test-molecule-v3
test-molecule-v3:## Run V3 molecule scenarios
	@while read -r MOLECULE_SCENARIO; do \
        if [ -d "$$MOLECULE_SCENARIO" ]; then\
            echo "Run scenario for "$$MOLECULE_SCENARIO && \
            cd .. ; \
            molecule converge --scenario-name $$MOLECULE_SCENARIO -- $(ANSIBLE_OPTIONS); \
            cd ./molecule ; \
        fi \
    done <MOLECULE_SCENARIOS.txt
