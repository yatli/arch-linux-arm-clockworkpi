#!/bin/bash
# example script of how to install this package on DevTerm
set -e

# scp yatao-rtx:~/home_devterm/arch-linux-arm-clockworkpi-a06/uboot-clockworkpi-a06/uboot-clockworkpi-a06-2022.04-3-aarch64.pkg.tar.xz ./
sudo pacman -U uboot-clockworkpi-a06-2022.04-3-aarch64.pkg.tar.xz
sudo dd if=/boot/idbloader.img of=/dev/mmcblk2 seek=64 conv=notrunc,fsync
sudo dd if=/boot/uboot.img of=/dev/mmcblk2 seek=16384 conv=notrunc,fsync
sudo dd if=/boot/trust.img of=/dev/mmcblk2 seek=24576 conv=notrunc,fsync
sudo reboot
