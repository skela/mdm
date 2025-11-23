import os


def execute(cmd: str):
	os.system(cmd)


def install(name: str):
	execute(f"yay --batchinstall --needed -S {name}")


execute("yay")

packages = [
	"ghostty",
	"krita",
	"inkscape",
	"gimp",
	"gemini-cli",
	"cura-bin",
	"blender",
	"visual-studio-code-bin",
]

for package in packages:
	install(package)
