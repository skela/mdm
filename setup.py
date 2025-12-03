import ast
import os
import subprocess


def execute(cmd: str):
	os.system(cmd)


def install(name: str):
	execute(f"yay --noconfirm --batchinstall --needed -S {name}")


execute("yay --noconfirm")

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
]

for package in packages:
	install(package)


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
	ghostty_desktop = find_desktop_entry(
		["com.mitchellh.ghostty.desktop", "ghostty.desktop"]
	)
	vscode_desktop = find_desktop_entry(
		["visual-studio-code.desktop", "code.desktop"]
	)
	blender_desktop = find_desktop_entry(["blender.desktop"])
	current = [
		app
		for app in current
		if app
		not in {
			"firefox.desktop",
			"firefox-developer-edition.desktop",
			"org.gnome.Console.desktop",
		}
	]
	ordered = [
		"org.gnome.Nautilus.desktop",
		"google-chrome.desktop",
		ghostty_desktop,
		vscode_desktop,
		blender_desktop,
	]
	excluded = set(ordered)
	current = [app for app in current if app not in excluded]
	favorites = ordered + current
	execute(f"gsettings set org.gnome.shell favorite-apps \"{favorites}\"")


def configure_background():
	bg = "~/.mdm/res/bg.jpg"
	execute(f"gsettings set org.gnome.desktop.background picture-uri {bg} ")
	execute(f"gsettings set org.gnome.desktop.background picture-uri-dark {bg} ")


configure_gnome_favorites()
configure_background()
