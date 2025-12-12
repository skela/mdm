default: pull setup

.PHONY: pull
pull:
	@git pull

.PHONY: setup
setup:
	@python setup.py --update --install --restore

.PHONY: update
update: pull
	@python setup.py --update --restore

.PHONY: install
install: pull
	@python setup.py --install --restore

.PHONY: help
help: help
	@python setup.py --help
