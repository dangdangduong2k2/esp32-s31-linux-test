#!/usr/bin/env bash
set -euo pipefail
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
REPO=$(cd "$(dirname "$0")/.." && pwd)
WORK_ROOT=${WORK_ROOT:-$REPO/.work}
mkdir -p "$WORK_ROOT" "$REPO/dist"
exec > >(tee "$REPO/dist/build.log") 2>&1
set -x
date -u
uname -a
df -h "$WORK_ROOT"
free -h
python3 "$REPO/scripts/prepare.py" "$WORK_ROOT"
python3 -m venv "$WORK_ROOT/venv"
"$WORK_ROOT/venv/bin/pip" install 'esptool==5.5.0'
export ESP_ESPTOOL="$WORK_ROOT/venv/bin/esptool"
export ESP_BSP_DIR="$WORK_ROOT/bsp"
make -C "$WORK_ROOT/buildroot" O="$WORK_ROOT/output" BR2_EXTERNAL="$WORK_ROOT/external" s31_test_defconfig
make -C "$WORK_ROOT/buildroot" O="$WORK_ROOT/output" -j"${JOBS:-2}"
cp "$WORK_ROOT/output/images/s31_full_flash.bin" "$REPO/dist/"
cp "$WORK_ROOT/output/.config" "$REPO/dist/buildroot.config"
cp "$WORK_ROOT/output/build/linux-custom/.config" "$REPO/dist/linux.config"
cp "$REPO/sources.lock.json" "$REPO/dist/"
"$WORK_ROOT/venv/bin/pip" freeze > "$REPO/dist/python-packages.txt"
find "$WORK_ROOT/output/images" -maxdepth 1 -type f -printf '%f %s bytes\n' > "$REPO/dist/image-sizes.txt"
(cd "$REPO/dist"; sha256sum s31_full_flash.bin > SHA256SUMS)
date -u
