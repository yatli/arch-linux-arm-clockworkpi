# Arch Linux ARM for the ClockworkPi DevTerm A06

Maintainer: Yatao Li

Original Author: Cole Smith

License: LGPL-2.1

# Introduction

This document will walk you through installing [Arch Linux ARM](https://archlinuxarm.org/) on the DevTerm A06.

We will create a root file system based on the **rock64** architecture (rk3328). This will include patching our
bootloader and kernel with the patches provided by ClockworkPi. Technically, the DevTerm A06's architecture is based on
the rk3399.

## Caution
If you are running advanced filesystems on your host (for example `zfs`), don’t try to prepare the image on that host. 
`mkinitcpio` in chroot doesn’t like that, and may cause damage to your host filesystem. Please use a virtual machine, or use a prebuilt image instead.

## Quickstart

Pre-built root filesystem(s) are provided in the **Releases** tab. Skip to the **Prepare the SD Card** section if using
a pre-built image.

**NOTE:** Please note the following defaults for the release filesystem:

* Root password: `root`
* Timezone: `US/Eastern`
* Locale: `en_US UTF8`
* Hostname: `devterm`

# Setup

This guide **assumes you are already using Arch Linux**. Some package names or procedures may differ depending on your
distribution.

In order to build the root filesystem, we will set up the following:

1. `aarch64` chroot environment + necessary configuration
2. `arm-none-eabi-gcc` build tools from ARM
3. Linux kernel
4. U-Boot bootloader
5. Additional packages for the A06

## Setting up Chroot Environment

We will start by creating an ARM chroot environment to build our root filesystem using
[this guide](https://nerdstuff.org/posts/2020/2020-003_simplest_way_to_create_an_arm_chroot/).

1. Install the required packages

```
$ yay -S base-devel qemu-user-static qemu-user-binfmt arch-install-scripts
# systemctl restart systemd-binfmt.service
```

2. Verify that an `aarch64` executable exists in

```
$ ls /proc/sys/fs/binfmt_misc
```

3. Download the base root FS to use. We will use the `aarch64` tarball from Arch Linux ARM

```
$ wget http://os.archlinuxarm.org/os/ArchLinuxARM-aarch64-latest.tar.gz
```

4. Create the mount point and extract the files as root (not via sudo)

```
$ sudo su
# mkdir root 

# bsdtar -xpf ArchLinuxARM-aarch64-latest.tar.gz -C root
# mount --bind root root
```

**NOTE**: It's very important that this `root` folder is owned by **root**. Otherwise, you will
get `unsafe path transition`
errors in the final build.

5. Chroot into the newly created environment

```
# arch-chroot root
```

6. Inside the chroot, populate and init the pacman keyring

```
# pacman-key --init
# pacman-key --populate archlinuxarm
```

7. Finally, update the packages

```
# pacman -Syu
```

## Configuring The Root Filesystem

We will start with lightly configuring our system before compiling the packages.

For this section, **all commands will be run inside the chroot**.

1. Install some useful tools

```
# pacman -S base-devel git vim wget ranger sudo man networkmanager
```

2. Enable `networkmanager` and `dhcpcd` for networking on first boot

```
# systemctl enable NetworkManager dhcpcd
```

3. Set the Locale by editing `/etc/locale.gen` and uncommenting your required locales.
4. Run

```
# locale-gen
```

5. Reference partitions in `/etc/fstab`

```
# echo 'LABEL=ROOT_ARCH    /    f2fs    defaults,noatime    0    0' >> /etc/fstab
# echo 'LABEL=BOOT_ARCH    /boot    ext4    defaults    0    0' >> /etc/fstab
```

6. Set the time using `timedatectl`. To list supported timezones: `timedatectl list-timezones`

```
# timedatectl set-timezone "US/Eastern"
# timedatectl set-ntp true
```

**NOTE**: This may affect the timezone of your system outside the chroot, if so, you may reset
your host system timezone after finishing the root tarball. 


7. Set the system clock

```
# hwclock --systohc
```

8. Set the hostname to whatever you like

```
# echo 'devterm' > /etc/hostname
```

9. Add the following to `/etc/X11/xorg.conf.d/10-monitor.conf`

```
Section "Monitor"
        Identifier "DSI-1"
        Option "Rotate" "right"
EndSection
```

10. Assign the root password

```
# passwd
```

### Switch to the `alarm` user

1. We can avoid working with the root account by granting `alarm`, the default Arch Linux ARM user, `sudo` privileges.

```
# EDITOR=/usr/bin/vim visudo
```

2. And add the corresponding line for `alarm` after the one for `root`

```
alarm ALL=(ALL) ALL
```

3. Switch to the `alarm` user

```
# su alarm

$ cd
```

**NOTE**: The default password for the **alarm** user is **alarm**

## Acquiring GCC Build Tools

U-Boot depends on the `arm-none-eabi-gcc` executable to be built, and since this program is not available in the Arch
Linux ARM repositories, we will download it directly from
[ARM's website](https://developer.arm.com/tools-and-software/open-source-software/developer-tools/gnu-toolchain/gnu-a/downloads)
.

1. Download the binaries

```
$ wget https://developer.arm.com/-/media/Files/downloads/gnu-a/10.3-2021.07/binrel/gcc-arm-10.3-2021.07-aarch64-arm-none-eabi.tar.xz
```

2. Extract the binaries to another directory

```
$ mkdir gcc 
$ tar -xJf gcc-arm-10.3-2021.07-aarch64-arm-none-eabi.tar.xz -C gcc
```

3. Add the toolchain to your `PATH`

```
$ cd gcc/gcc-arm-10.3-2021.07-aarch64-arm-none-eabi/bin
$ export PATH=$PATH:$(pwd)
$ cd
```

## Compiling The Packages

This repository contains pre-configured and patched Arch Linux packages for the DevTerm A06. The Linux kernel and U-Boot
are based off the **rock64** variants, already available in Arch Linux ARM, with patches provided by ClockWorkPi.

You can find these patches from
ClockworkPi [here](https://github.com/clockworkpi/DevTerm/tree/main/Code/patch/armbian_build_a06/patch).

### Download This Repository

1. Inside the `alarm` home folder of your `aarch64` chroot environment, clone this repository

```
$ git clone https://github.com/yatli/arch-linux-arm-clockworkpi-a06.git
$ cd arch-linux-arm-clockworkpi-a06
```

### Compiling The Linux Kernel

1. Build the package. **This can take a long time!!** Especially since we are emulating an `aarch64`
   architecture. The package build tool `makepkg`, supports a flag called `MAKEFLAGS`. Below, we will append
   `MAKEFLAGS="-j$(nproc)"` to the `makepkg` command to instruct the compiler to use one worker for each core.

```
$ cd linux-clockworkpi-a06 
$ MAKEFLAGS="-j$(nproc)" makepkg -si 
$ cd ..
```

### Compiling U-Boot

1. Build the rkbin helper, which allows us to run rockchip-supplied, x64-only, image packing tool for uboot.

```
$ cd rkbin-aarch64-hack
$ MAKEFLAGS="-j$(nproc)" makepkg -si 
$ cd ..
```

2. Build the package, similar to above.

```
$ cd uboot-clockworkpi-a06 
$ MAKEFLAGS="-j$(nproc)" makepkg -si 
$ cd ..
```

**NOTE: DO NOT INSTALL THE BOOTLOADER TO THE DISK WHEN ASKED AFTER THIS STEP.** We will do this ourselves when we
prepare the SD card.


**Note:** Since we are going to use a separate boot partition, edit the file `/boot/extlinux/extlinux.conf`.
Original:
```
LABEL Arch ARM
KERNEL /boot/Image
FDT /boot/dtbs/rockchip/rk3399-clockworkpi-a06.dtb
APPEND initrd=/boot/initramfs-linux.img console=ttyS2,1500000 root=LABEL=ROOT_ARCH rw rootwait audit=0
```
Updated:
```
LABEL Arch ARM
KERNEL /Image
FDT /dtbs/rockchip/rk3399-clockworkpi-a06.dtb
APPEND initrd=/initramfs-linux.img console=ttyS2,1500000 root=LABEL=ROOT_ARCH rw rootwait audit=0
```

### Compiling Additional Packages

For each additional package directory in this repository

```
$ cd <package directory> 
$ MAKEFLAGS="-j$(nproc)" makepkg -si 
$ cd ..
```

### Clean up the build dependencies
```
# pacman -Rs base-devel git vim wget ranger rkbin-aarch64-hack xmlto docbook-xsl inetutils bc dtc
# rm /var/cache/pacman/pkg/*.pkg.tar.xz*
# rm /home/alarm/gcc*
```

### Exit the chroot

1. Exit `alarm`

```
$ exit
```

2. Exit `root`

```
# exit
```

### Unmount The Root Filesystem

```
 # umount root
```

# Tar The Root Filesystem

We are now ready to package up the root filesystem into a compressed tarball.
Optionally, we can save the built packages.

```
 # cd root
 # mv home/alarm/arch-linux-arm-clockworkpi-a06 ../
 # tar cpJf ../arch-linux-clockworkpi-a06-root-fs.tar.xz .
 # cd ..
```

Change ownership of the tarball and exit the `root` account

```
 # chown <user>:<user> arch-linux-clockworkpi-a06-root-fs.tar.xz
 # exit
```

**You now have a root filesystem tarball to bootstrap the SD card!**

## Prepare the SD Card

We will now put our prepared filesystem onto the SD card. We will follow
[Arch Linux ARM's guide for the rock64](https://archlinuxarm.org/platforms/armv8/rockchip/rock64) (except that we use f2fs for root, instead of ext4),
but use our tarball in place of theirs.

1. Zero the beginning of the SD card

```
# dd if=/dev/zero of=/dev/sdX bs=1M count=32
```

2. Start fdisk to partition the SD card

```
# fdisk /dev/sdX
```

3. Inside fdisk,

    1. Type **o**. This will clear out any partitions on the drive
    2. Type **p** to list partitions. There should be no partitions left
    3. Type **n**, then **p** for primary, **1** for the first partition on the drive, **32768** for the first sector, then **+2G** for the last sector (boot partition, 2GB)
	4. Type **p** and note the end sector number for the partition freshly created.
    5. Type **n**, then **p**, **2** for the second partition, **use number from step 4 and add 2** as first sector, then **+4G** for the last sector (swap partition, 4GB)
	6. Again, type **p** and note the end sector number for the partition freshly created.
    7. Type **n**, then **p**, **3** for the third partition, **use number from step 6 and add 2** as first sector, then leave default for the last sector (root partition, takes all available space)
    8. Write the partition table and exit by typing **w**

4. Create the **ext4** filesystem **without a Journal** for boot, and **f2fs** filesystem for root

```
# mkfs.ext4 -L BOOT_ARCH -O ^has_journal /dev/sdX1
# mkswap /dev/sdX2
# mkfs.f2fs -l ROOT_ARCH -O extra_attr,inode_checksum,sb_checksum /dev/sdX3
```

**IMPORTANT** The `mkswap` command will return the swap partition's UUID, which will be needed later. Please write it down.

**NOTE:** Disabling the journal is helpful for simple flash devices like SD Cards to reduce successive writes.
In rare cases, your filesystem may become corrupted, which may arise as a boot loop.
Running `fsck -y /dev/sdX1` on an external system can fix this issue.

5. Mount the filesystem

```
# mount /dev/sdX3 /mnt
# mkdir -p /mnt/boot
# mount /dev/sdX1 /mnt/boot
```

6. Install the root filesystem (as root not via sudo)

```
# sudo su
# bsdtar -xpf arch-linux-clockworkpi-a06-root-fs.tar.xz -C /mnt
# echo 'UUID="<SWAP PARTITION UUID HERE>" none  swap  sw  0 0' >> /mnt/etc/fstab
# exit
```

7. Install the bootloader to the SD card

```
# cd /mnt/boot
# dd if=idbloader.img of=/dev/sdX seek=64 conv=notrunc,fsync
# dd if=uboot.img of=/dev/sdX seek=16384 conv=notrunc,fsync
# dd if=trust.img of=/dev/sdX seek=24576 conv=notrunc,fsync
```

8. Unmount and eject the SD card

```
# cd
# umount /mnt/boot
# umount /mnt
# sync
```

## Done!

The SD card is now ready to be booted by the DevTerm! Good luck!

## Next Steps

You will want to set up Wi-Fi on first boot. Use the command `nmtui`.

Check out the [post-install suggestions](https://wiki.archlinux.org/title/General_recommendations) from Arch Linux for
further configuration.

## Troubleshooting

If you run into issues where you see no screen output or the DevTerm will not boot, please check the debugging output
via UART:

1. Connect a micro-USB cable to the UART port on the *inside* of your DevTerm, near where the printer ribbon cable is
   connected
2. Connect the other end to your Linux system, you should now see a new device: `/dev/ttyUSB0`
3. Monitor the connection with `sudo stty -F /dev/ttyUSB0 1500000 && sudo cat /dev/ttyUSB0`
4. Power on your DevTerm and monitor for errors

# Acknowledgements

Very special thanks to **Max Fierke (@maxfierke)** from the CPI Discord, and the Manjaro team for their help in
debugging and kernel patching. The Linux kernel and u-boot ports in this repository uses their carefully designed
patches, and modified PKGBUILDs. This Arch Linux port would not be possible without their hard work, and I make no
claims or credit to it.

[Manjaro DevTerm A06 Linux Kernel](https://gitlab.manjaro.org/manjaro-arm/packages/core/linux-clockworkpi-a06)

[Manjaro DevTerm A06 U-Boot](https://gitlab.manjaro.org/manjaro-arm/packages/core/uboot-clockworkpi-a06)

