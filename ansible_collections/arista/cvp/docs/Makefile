.PHONY: build_modules
build_modules: ## Build modules documentation
	python ansible2rst.py
	find . -name 'cv_*.rst' -exec pandoc {} --from rst --to gfm -o module_docs/{}.md \;

