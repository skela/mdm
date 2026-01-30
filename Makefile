default: pull update

.PHONY: pull
pull:
	@git pull

.PHONY: update
update: pull
	@python setup.py --update --restore

.PHONY: upgrade
upgrade: pull
	@python setup.py --upgrade --install --restore

.PHONY: install
install: pull
	@python setup.py --install --restore

.PHONY: restore
restore: pull
	@python setup.py --restore

.PHONY: help
help:
	@echo "usage: teknolab [install] [update] [upgrade] [restore]"
	@echo
	@echo "options:"
	@echo "  restore, -r   Restore environment"
	@echo "  install, -i  Install packages"
	@echo "  update, -u   Update packages"
	@echo "  upgrade, -U   Upgrade everything"
