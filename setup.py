import ast
import configparser
import os
import shutil
import socket
import subprocess
import argparse
import filecmp

from src.packages import Package, Manager, DesktopEntry
from src.logger import Logger

parser = argparse.ArgumentParser()
parser.add_argument("--install", "-i", help="Install packages", action="store_true", default=False)
parser.add_argument("--update", "-u", help="Update packages", action="store_true", default=False)
parser.add_argument("--upgrade", "-U", help="Upgrade everything", action="store_true", default=False)
parser.add_argument("--restore", "-r", help="Restores Teknolab settings", action="store_true", default=False)
parser.add_argument("--enroll", "-e", help="Enroll device in TeknoLab", action="store_true", default=False)
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
	Package("localsend-bin"),
	Package("flatpak"),
	Package("tailscale"),
	Package("qrencode"),
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

logger = Logger()


def execute(cmd: str):
	subprocess.run(cmd, shell=True)


def install(packages: list[Package]):
	syspacks = [p.name for p in packages if p.manager == Manager.System]
	if len(syspacks) > 0:
		execute(f"yay --noconfirm --batchinstall --needed -S {' '.join(syspacks)}")

	execute("flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo")

	flatpaks = [p.name for p in packages if p.manager == Manager.Flatpak]
	if len(flatpaks) > 0:
		execute(f"flatpak install flathub {' '.join(flatpaks)} -y")


def update():
	execute("flatpak update -y")


def upgrade():
	execute("yay --noconfirm --batchinstall -Syu")
	execute("flatpak update -y")


def install_packages():
	install(packages)

	for package in packages:
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
	logger.start("Configuring shell")
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
			"" ) make help ;;
			restore|-r ) make restore;;
			install|-i ) make install ;;
			update|-u ) make update ;;
			upgrade|-U ) make upgrade ;;
			enroll|-e ) make enroll ;;
			pull|-p ) make pull ;;
			* ) make help ;;
		esac
	)
	case "$1" in
		install|-i|update|-u|upgrade|-U) source ~/.bashrc ;;
	esac
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

	logger.finish_ok("Configured shell")


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
	logger.start("Configuring gnome favourites")
	if not shutil.which("gsettings"):
		logger.finish_error("Configured gnome favourites")
		return

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
	execute(f'gsettings set org.gnome.shell favorite-apps "{favorites}"')
	logger.finish_ok("Configured gnome favourites")


def configure_background():
	logger.start("Configuring background")
	bg = "~/.mdm/res/bg.jpg"
	execute(f"gsettings set org.gnome.desktop.background picture-uri {bg} ")
	execute(f"gsettings set org.gnome.desktop.background picture-uri-dark {bg} ")
	logger.finish_ok("Configured background")


def configure_groups():
	pass
	# execute("sudo usermod -aG uucp $USER") # uucp - unix-to-unix-copy - aka serial communications group


def configure_permissions():
	microbit_udev_rules_path = "/etc/udev/rules.d/69-microbit.rules"
	desired = "./cfg/udev/69-microbit.rules"
	if not os.path.exists(microbit_udev_rules_path) or not filecmp.cmp(microbit_udev_rules_path, desired, shallow=False):
		logger.start("Configuring permissions")
		execute(f"sudo cp {desired} {microbit_udev_rules_path}")
		execute("sudo udevadm control --reload")
		execute("sudo udevadm trigger")
		logger.finish_ok("Configured permissions")


def get_wifi_mac() -> str:
	try:
		for iface in os.listdir("/sys/class/net"):
			if iface.startswith("wl"):
				with open(f"/sys/class/net/{iface}/address") as f:
					return f.read().strip()
	except Exception:
		pass
	return "unknown"


def enroll_tailscale():
	execute("sudo systemctl enable --now tailscaled")
	execute(f"sudo tailscale set --operator={os.environ.get('USER')}")

	result = subprocess.run(["tailscale", "status"], capture_output=True, text=True)
	if result.returncode == 0:
		print("This device is already enrolled in Tailscale.")
		return

	hostname = socket.gethostname()
	mac = get_wifi_mac()

	repo_root = os.path.dirname(os.path.abspath(__file__))
	conf_path = os.path.join(repo_root, "mdm.conf")
	authkey = None
	if os.path.exists(conf_path):
		conf = configparser.ConfigParser()
		conf.read(conf_path)
		authkey = conf.get("tailscale", "authkey", fallback=None)

	if authkey:
		logger.start(f"Enrolling {hostname} ({mac}) using saved auth key")
		execute(f"tailscale up --authkey={authkey} --hostname={hostname}")
		logger.finish_ok("Enrolled in Tailscale")
		return

	process = subprocess.Popen(
		["tailscale", "up", f"--hostname={hostname}"],
		stdout=subprocess.PIPE,
		stderr=subprocess.STDOUT,
		text=True,
	)

	url = None
	assert process.stdout is not None
	for line in process.stdout:
		stripped = line.strip()
		if "login.tailscale.com" in stripped:
			url = stripped
			break

	if url:
		print(f"\nDevice:   {hostname}")
		print(f"WiFi MAC: {mac}")
		print("\nScan to enroll:\n")
		subprocess.run(["qrencode", "-t", "UTF8", f"{url}?mac={mac.replace(':', '%3A')}"])
		print(f"\nOr visit: {url}\n")
		print("Waiting for authentication...")
		process.wait()
		logger.finish_ok("Enrolled in Tailscale")
	else:
		process.wait()
		logger.finish_error("Tailscale enrollment")


if args.update:
	update()
if args.upgrade:
	upgrade()
if args.install:
	install_packages()
if args.restore:
	configure_gnome_favorites()
	configure_background()
	configure_shell()
	configure_groups()
	configure_permissions()
if args.enroll:
	enroll_tailscale()
