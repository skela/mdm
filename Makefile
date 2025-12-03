default: update setup

.PHONY: update
update:
	@git pull

.PHONY: setup
setup:
	@python setup.py

