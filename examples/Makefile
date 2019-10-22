### Environment management

setup:
	@echo "-> Install repository requirements."
	pip install -r ../requirements.txt

install:
	@echo "-> Build and install arista.cvp collection to ${PWD}/collections"
	ansible-galaxy collection build --force ../arista/cvp
	for collection in *.tar.gz; do \
		ansible-galaxy collection install $$collection -p collections/ ;\
	done

clean:
	@echo "-> Cleanup local folder:"
	rm -rf collections/
	rm -f *.tar.gz

build: setup install
rebuild: clean install

### CVP Tests management

facts-foster:
	@echo '-> Running test cases against foster version'
	@echo ''
	@echo '## ---------------------------------------- ##'
	@echo ''
	ansible-playbook playbook.facts.demo.yaml --limit cvp_foster

facts-grant:
	@echo '-> Running test cases against foster version'
	@echo ''
	@echo '## ---------------------------------------- ##'
	@echo ''
	ansible-playbook playbook.facts.demo.yaml --limit cvp_grant