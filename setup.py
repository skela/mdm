import ast
import os
import shutil
import subprocess
import argparse

from src.packages import Package, Manager, DesktopEntry

parser = argparse.ArgumentParser()
parser.add_argument("--install", "-i", help="Install packages", action="store_true", default=False)
parser.add_argument("--update", "-u", help="Update packages", action="store_true", default=False)
parser.add_argument("--restore", "-r", help="Restores Teknolab settings", action="store_true", default=False)
args = parser.parse_args()

packages: list[Package] = [
	Package("ghostty"),
	Package("neovim"),
	Package("fish"),
	Package("krita"),
	Package("inkscape"),
	Package("gimp"),
	Package("gemini-cli"),
	Package("cura-bin"),
	Package("blender"),
	Package("visual-studio-code-bin"),
	Package("google-chrome"),
	Package("microblocks"),
	Package(
		"org.vinegarhq.Sober",
		manager=Manager.Flatpak,
		desktop_entry=DesktopEntry(
			name="Roblox",
			comment="Launch Roblox via Sober",
			icon="roblox",
			startup_notify=True,
			required=True,
			categories=["Game"],
		),
	),  # roblox
	Package(
		"org.vinegarhq.Vinegar",
		manager=Manager.Flatpak,
		desktop_entry=DesktopEntry(
			name="Roblox Studio",
			comment="Launch Roblox Studio via Vinegar",
			icon="roblox-studio",
			startup_notify=True,
			required=True,
			categories=["Game", "Education"],
		),
	),  # roblox-studio - https://github.com/Nightro-Fx/Flatpak-Vinegar-Guide
]


def execute(cmd: str):
	os.system(cmd)


def install(package: Package):
	match package.manager:
		case Manager.System:
			execute(f"yay --noconfirm --batchinstall --needed -S {package.name}")
		case Manager.Flatpak:
			execute(f"flatpak install flathub {package.name} -y")


def update_all():
	execute("yay --noconfirm")


def prepare_flatpak():
	install(Package("flatpak"))
	execute("flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo")


def install_packages():
	prepare_flatpak()

	for package in packages:
		install(package)
		post_install(package)


def post_install(package: Package):
	if not package.desktop_entry.required:
		return

	applications_dir = os.path.expanduser("~/.local/share/applications")
	os.makedirs(applications_dir, exist_ok=True)
	icons_dir = os.path.expanduser("~/.icons")
	os.makedirs(icons_dir, exist_ok=True)

	entry = package.desktop_entry

	match package.manager:
		case Manager.System:
			desktop_path = os.path.join(applications_dir, f"{package.name}.desktop")
			desktop_entry = f"""[Desktop Entry]
Name={entry.name}
Comment={entry.comment}
Exec={package.name}
Terminal={entry.terminal}
Type={entry.type}
Icon={entry.icon}
Categories={";".join(entry.categories)};
StartupNotify={entry.startup_notify}
		"""
			with open(desktop_path, "w", encoding="utf-8") as desktop_file:
				desktop_file.write(desktop_entry)
		case Manager.Flatpak:
			desktop_path = os.path.join(applications_dir, f"{package.name}.desktop")
			desktop_entry = f"""[Desktop Entry]
Name={entry.name}
Comment={entry.comment}
Exec=flatpak run {package.name}
Terminal={entry.terminal}
Type={entry.type}
Icon={entry.icon}
Categories={";".join(entry.categories)};
StartupNotify={entry.startup_notify}
X-Flatpak={package.name}
		"""
			with open(desktop_path, "w", encoding="utf-8") as desktop_file:
				desktop_file.write(desktop_entry)

	repo_root = os.path.dirname(os.path.abspath(__file__))
	icon_src = os.path.join(repo_root, "res", f"{entry.icon}.svg")
	if os.path.exists(icon_src):
		icon_dst = os.path.join(icons_dir, f"{entry.icon}.svg")
		shutil.copy(icon_src, icon_dst)


def configure_shell():
	home = os.path.expanduser("~")
	bashrc_path = os.path.join(home, ".bashrc")
	if not os.path.exists(bashrc_path):
		with open(bashrc_path, "w", encoding="utf-8"):
			pass

	repo_root = os.path.dirname(os.path.abspath(__file__))
	snippet = f"""
# Teknolab command helper
teknolab() {{
	(
		cd "{repo_root}" || return 1
		case "$1" in
			\"\" ) make help ;;
			install ) make install ;;
			update ) make update ;;
			* ) make help ;;
		esac
	)
}}
"""
	start_marker = "# Teknolab command helper"
	with open(bashrc_path, "r", encoding="utf-8") as bashrc:
		content = bashrc.read()

	if snippet.strip() in content:
		return

	cleaned = content
	if start_marker in content:
		lines = content.splitlines()
		trimmed = []
		skipping = False
		for line in lines:
			if not skipping and line.strip() == start_marker:
				skipping = True
				continue
			if skipping:
				if line.strip() == "}":
					skipping = False
				continue
			trimmed.append(line)
		cleaned = "\n".join(trimmed).rstrip("\n")

	with open(bashrc_path, "w", encoding="utf-8") as bashrc:
		if cleaned:
			bashrc.write(cleaned)
			bashrc.write("\n")
		bashrc.write(snippet.lstrip("\n"))


DESKTOP_DIRS = [
	"/usr/share/applications",
	os.path.expanduser("~/.local/share/applications"),
]


def find_desktop_entry(candidates: list[str]) -> str:
	for candidate in candidates:
		for directory in DESKTOP_DIRS:
			if os.path.exists(os.path.join(directory, candidate)):
				return candidate
	return candidates[0]


def configure_gnome_favorites():
	raw = subprocess.check_output(
		["gsettings", "get", "org.gnome.shell", "favorite-apps"],
		text=True,
	).strip()
	current = ast.literal_eval(raw)
	ghostty = find_desktop_entry(["com.mitchellh.ghostty.desktop", "ghostty.desktop"])
	vscode = find_desktop_entry(["visual-studio-code.desktop", "code.desktop"])
	blender = find_desktop_entry(["blender.desktop"])
	roblox_studio = find_desktop_entry(["org.vinegarhq.Vinegar.desktop"])
	roblox = find_desktop_entry(["org.vinegarhq.Sober.desktop"])
	nautilus = "org.gnome.Nautilus.desktop"
	chrome = "google-chrome.desktop"
	current = [app for app in current if app not in {
		"firefox.desktop",
		"firefox-developer-edition.desktop",
		"org.gnome.Console.desktop",
	}]
	ordered = [
		nautilus,
		chrome,
		ghostty,
		vscode,
		blender,
		roblox_studio,
		roblox,
	]
	excluded = set(ordered)
	current = [app for app in current if app not in excluded]
	favorites = ordered + current
	execute(f"gsettings set org.gnome.shell favorite-apps \"{favorites}\"")


def configure_background():
	bg = "~/.mdm/res/bg.jpg"
	execute(f"gsettings set org.gnome.desktop.background picture-uri {bg} ")
	execute(f"gsettings set org.gnome.desktop.background picture-uri-dark {bg} ")


if args.update:
	update_all()
if args.install:
	install_packages()
if args.restore:
	configure_gnome_favorites()
	configure_background()
	configure_shell()
