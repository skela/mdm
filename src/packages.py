from enum import Enum
from typing import Optional


class Manager(Enum):
	System = 1
	Flatpak = 2


class DesktopEntry(object):

	def __init__(
		self,
		name: str,
		comment: str,
		icon: str,
		terminal: bool = False,
		type: str = "Application",
		startup_notify: bool = False,
		required: bool = False,
		categories: list[str] = [],
	):
		self.name = name
		self.comment = comment
		self.terminal = terminal
		self.type = type
		self.startup_notify = startup_notify

		self.required = required
		self.categories = categories


class Package(object):

	def __init__(
		self,
		name: str,
		version: Optional[str] = None,
		manager: Manager = Manager.System,
		desktop_entry: DesktopEntry = DesktopEntry(
			name="",
			comment="",
			icon="",
		),
	):
		self.name = name
		self.manager = manager
		self.version = version
		self.desktop_entry = desktop_entry
