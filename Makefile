default: pull update

.PHONY: pull
pull:
	@git pull

.PHONY: update
update: pull
	@python setup.py --update --install --restore

.PHONY: install
install: pull
	@python setup.py --install --restore

.PHONY: restore
restore:
	@python setup.py --restore

.PHONY: help
help:
	@echo "usage: teknolab [install] [update] [restore]"
	@echo
	@echo "options:"
	@echo "  install, -i  Install packages"
	@echo "  update, -u   Update packages"
	@echo "  restore, -r   Restore environment"
