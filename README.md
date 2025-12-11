# Setup of TeknoLab Computers

## Preparing a new computer

Follow these steps to install the OS on a fresh machine.

### Create the installer USB

- Download the latest EndeavourOS ISO from the [official site](https://endeavouros.com/).
- Flash the ISO to a USB drive (e.g. with BalenaEtcher or another USB imaging tool).
- Reboot and enter the BIOS/UEFI; disable Secure Boot if it blocks booting the USB.
- Boot from the live USB and start the EndeavourOS installer.

### Installation (EndeavourOS)

- Launch the installer: on the live desktop, open the EndeavourOS installer (Calamares) from the desktop shortcut or application menu.
- When prompted for installation mode, choose Online (preferred) instead of Offline.
- Location: set language to English (UK); leave the region as detected.
- Keyboard: choose Norwegian layout (usually the default in Norway).
- Desktop: select Gnome.
- Packages: leave defaults and click Next.
- Partitions: choose Erase disk; for Swap select `Swap (no Hibernate)`.
- Users: for a machine named Ziggy, fill in:
  - What is your name? `Ziggy`
  - What name do you want to use to login? `teknolab`
  - What is the name of this computer? `ziggy`
  - Enter a secure password, tick “log in automatically without asking for the password”, and tick “use the same password for the administrator account”.
- Summary/Install: review and start the installation; reboot when finished and remove the USB.

## Post-installation setup

- Open a terminal
- `git clone https://github.com/skela/mdm .mdm`
- `cd .mdm`
- `python setup.py`
