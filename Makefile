default: update configure

.PHONY: update
update:
	@git pull

.PHONY: configure
configure:
	@python configure.py

