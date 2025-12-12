default: pull setup

.PHONY: pull
pull:
	@git pull

.PHONY: setup
setup:
	@python setup.py --update --install --restore

.PHONY: install
install: pull
	@python setup.py --install --restore

