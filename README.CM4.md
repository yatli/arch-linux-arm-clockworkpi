# Additional bootstrap steps for CM4

## If using a pre-built rootfs, skip to "Prepare the SD Card".

** Inject these steps after main procedure step 1

```bash
pacman -D --asexplicit binutils diffutils linux-firmware linux-firmware-whence mkinitcpio
pacman -R linux-aarch64 uboot-raspberrypi
```

Copy the built kernel (kernel8.img etc.) to /boot
Copy modules to /lib/modules/
Copy config.txt and cmdline.txt to /boot

Copy mkinitcpio.conf to /etc/
Copy linux.preset to /etc/mkinitcpio.d/
mkinitcpio -P

Install dnsmasq, copy dns.conf to /etc/NetworkManager/conf.d/
Install pre-built packages:
audio-clockworkpi-cm4-0.1-1-aarch64.pkg.tar.xz
bluetooth-clockworkpi-cm4-0.1-1-aarch64.pkg.tar.xz
uconsole-4g-clockworkpi-cm4-1.0-1-aarch64.pkg.tar.xz
wiringpi-clockworkpi-cm4-bin-0.1-1-aarch64.pkg.tar.xz

Install bluez (TODO: this should be a dependency of bluetooth-clockworkpi-cm4)

systemctl enable bluetooth
systemctl disable systemd-networkd
systemctl disable systemd-resolved

** Now, return to main procedure step 2

locale.gen: enable both C and en_US

** Inject step 5

Note: our mkinitcpio.conf disabled udev and systemd, so LABEL=... will not work

```
# Static information about the filesystems.
# See fstab(5) for details.

# <file system> <dir> <type> <options> <dump> <pass>
proc                  /proc   proc  defaults        0   0
PARTUUID=617a2abd-01  /boot   vfat  defaults,flush  0   2
PARTUUID=617a2abd-02  /       ext4  defaults,noatime  0   1
```

** Inject step 6,7,8...

systemctl enable systemd-timesyncd
hwclock --hctosys

echo 'uConsole' > /etc/hostname

Root password: root

/etc/sudoer: 

```
alarm ALL=(ALL:ALL) NOPASSWD: ALL
```

## Prepare the SD Card

Do not delete the Raspbian partitions. Instead, remove all the files from the partitions.
The first partition should be FAT32
The second partition should be EXT4

TODO figure out the partitioning details:
https://github.com/raspberrypi/rpi-imager/blob/d825c22fb9b2bbb33859d8f4befd314264cae8b3/src/driveformatthread.cpp#L159

** Continue to step 6 in main procedure, minus the SWAP part.

!!! Update /etc/fstab and /boot/cmdline.txt for PART-UUID!