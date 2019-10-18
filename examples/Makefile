build:
		@echo "-----------------------------------------------------------"
		@echo "| Build and install arista.cvp collection to local folder |"
		@echo "-----------------------------------------------------------"
		ansible-galaxy collection build --force ../arista/cvp
		for collection in *.tar.gz; do \
			ansible-galaxy collection install $$collection -p collections/ ;\
		done
clean:
		@echo "-----------------------------------------------------------"
		@echo "| Cleanup local folder                                    |"
		@echo "-----------------------------------------------------------"
		rm -rf collections/
		rm -f *.tar.gz