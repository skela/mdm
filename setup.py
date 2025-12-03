import os


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

bg = "~/.mdm/res/bg.jpg"
execute(f"gsettings set org.gnome.desktop.background picture-uri {bg} ")
execute(f"gsettings set org.gnome.desktop.background picture-uri-dark {bg} ")
