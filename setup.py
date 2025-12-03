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


def configure_gnome_favorites():
	raw = subprocess.check_output(
		["gsettings", "get", "org.gnome.shell", "favorite-apps"],
		text=True,
	).strip()
	favorites = ast.literal_eval(raw)
	favorites = [app for app in favorites if app != "firefox.desktop"]
	if "google-chrome.desktop" not in favorites:
		favorites.append("google-chrome.desktop")
	execute(f"gsettings set org.gnome.shell favorite-apps \"{favorites}\"")


def configure_background():
	bg = "~/.mdm/res/bg.jpg"
	execute(f"gsettings set org.gnome.desktop.background picture-uri {bg} ")
	execute(f"gsettings set org.gnome.desktop.background picture-uri-dark {bg} ")


configure_gnome_favorites()
configure_background()
