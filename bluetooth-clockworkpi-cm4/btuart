#!/bin/sh
# /usr/bin/btuart
# Based on https://github.com/RPi-Distro/pi-bluetooth/blob/master/usr/bin/btuart

HCIATTACH=/usr/bin/btattach
if grep -q "Pi 4" /proc/device-tree/model; then
  BDADDR=
else
  SERIAL=`cat /proc/device-tree/serial-number | cut -c9-`
  B1=`echo $SERIAL | cut -c3-4`
  B2=`echo $SERIAL | cut -c5-6`
  B3=`echo $SERIAL | cut -c7-8`
  BDADDR=`printf b8:27:eb:%02x:%02x:%02x $((0x$B1 ^ 0xaa)) $((0x$B2 ^ 0xaa)) $((0x$B3 ^ 0xaa))`
fi

uart0="`cat /proc/device-tree/aliases/uart0`"
serial1="`cat /proc/device-tree/aliases/serial1`"

if [ "$uart0" = "$serial1" ] ; then
	uart0_pins="`wc -c /proc/device-tree/soc/gpio@7e200000/uart0_pins/brcm\,pins | cut -f 1 -d ' '`"
	if [ "$uart0_pins" = "16" ] ; then
		$HCIATTACH -B /dev/serial1 -P bcm -S 3000000
	else
		$HCIATTACH -B /dev/serial1 -P bcm -S 921600 --noflowctl
	fi
else
	$HCIATTACH -B /dev/serial1 -P bcm -S 460800 --noflowctl
fi