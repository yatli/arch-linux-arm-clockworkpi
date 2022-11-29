#!/bin/bash

set -e

makepkg -e -f
sudo pacman -U uboot-clockworkpi-a06-2022.04-3-aarch64.pkg.tar.xz
sudo dd if=/boot/u-boot.itb of=/dev/mmcblk1 seek=16384 conv=notrunc,fsync 
sudo dd if=/boot/idbloader.img of=/dev/mmcblk1 seek=64 conv=notrunc,fsync 
sudo reboot
