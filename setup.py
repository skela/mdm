import ast
import os
import shutil
import subprocess


def execute(cmd: str):
	os.system(cmd)


def install(name: str):
	execute(f"yay --noconfirm --batchinstall --needed -S {name}")


def update_all():
	execute("yay --noconfirm")


def install_packages():
	packages = [
		"ghostty",
		"neovim",
		"fish",
		"krita",
		"inkscape",
		"gimp",
		"gemini-cli",
		"cura-bin",
		"blender",
		"visual-studio-code-bin",
		"google-chrome",
		"flatpak",
	]

	for package in packages:
		install(package)

	install_flatpaks()
	install_vinegar_launcher()


def install_flatpaks():
	flat_paks = [
		"org.vinegarhq.Vinegar",  # roblox-studio - https://github.com/Nightro-Fx/Flatpak-Vinegar-Guide
	]

	execute("flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo")
	for package in flat_paks:
		execute(f"flatpak install flathub {package} -y")


def install_vinegar_launcher():
	applications_dir = os.path.expanduser("~/.local/share/applications")
	os.makedirs(applications_dir, exist_ok=True)
	icons_dir = os.path.expanduser("~/.icons")
	os.makedirs(icons_dir, exist_ok=True)
	repo_root = os.path.dirname(os.path.abspath(__file__))
	icon_src = os.path.join(repo_root, "res", "roblox.svg")
	icon_name = "roblox-vinegar"
	icon_dst = os.path.join(icons_dir, f"{icon_name}.svg")
	shutil.copy(icon_src, icon_dst)
	desktop_path = os.path.join(applications_dir, f"{icon_name}.desktop")
	desktop_entry = """[Desktop Entry]
Name=Roblox Studio
Comment=Launch Roblox Studio via Vinegar Flatpak
Exec=flatpak run org.vinegarhq.Vinegar
Terminal=false
Type=Application
Icon=roblox-studio
Categories=Game;Education;
StartupNotify=true
X-Flatpak=org.vinegarhq.Vinegar
"""
	with open(desktop_path, "w", encoding="utf-8") as desktop_file:
		desktop_file.write(desktop_entry)


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
	roblox = find_desktop_entry(["roblox-vinegar.desktop"])
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


update_all()
install_packages()
configure_gnome_favorites()
configure_background()
