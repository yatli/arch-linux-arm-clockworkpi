#!/bin/bash

set -e

cd src/rkbin-master
tools/mkimage -n rk3399 -T rksd -d bin/rk33/rk3399_ddr_800MHz_v1.27.bin idbloader.img
cat bin/rk33/rk3399_miniloader_v1.26.bin >> idbloader.img
tools/loaderimage --pack --uboot ../u-boot-2022.04/u-boot-dtb.bin uboot.img 0x00200000
tools/trust_merger RKTRUST/RK3399TRUST.ini
cd ../..
