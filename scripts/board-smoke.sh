#!/bin/sh
# Bounded tests for a 16 MiB board. No raw flash writes or deliberate OOM.
echo '=== S31_SMOKE_BEGIN ==='
uname -a
cat /proc/version
cat /proc/cpuinfo
cat /proc/meminfo
cat /proc/cmdline
cat /proc/mounts
cat /proc/mtd
cat /proc/uptime
ls -l /dev/ttyS0 /dev/gpiochip* /dev/i2c* 2>&1
echo '=== TEMP_FILE_CHECK ==='
probe=$(mktemp /tmp/s31-smoke.XXXXXX) || exit 1
trap 'rm -f "$probe" "$probe.copy"' EXIT
dd if=/dev/zero of="$probe" bs=1024 count=256
cp "$probe" "$probe.copy"
if cmp "$probe" "$probe.copy"; then echo 'PASS temp file 256 KiB'; else echo 'FAIL temp file'; fi
cksum "$probe" "$probe.copy"
echo '=== EXPECTED_READ_ONLY_ROOT ==='
if touch /.s31-linux-write-probe; then
    rm -f /.s31-linux-write-probe
    echo 'UNEXPECTED writable root; review image/config'
else
    echo 'EXPECTED read-only root rejection'
fi
echo '=== CPU_AND_PROCESS_CHECK ==='
(i=0; while [ "$i" -lt 10000 ]; do i=$((i+1)); done; echo "PASS worker A iterations=$i") &
pid_a=$!
(i=0; while [ "$i" -lt 10000 ]; do i=$((i+1)); done; echo "PASS worker B iterations=$i") &
pid_b=$!
wait "$pid_a"; wait "$pid_b"
echo '=== NETWORK_INVENTORY ==='
cat /proc/net/dev
ip addr 2>&1
ip route 2>&1
for p in /sys/class/net/*; do echo "$p"; cat "$p/operstate" "$p/carrier" 2>&1; done
echo '=== USB_INVENTORY ==='
ls /sys/bus/usb/devices 2>&1
echo '=== DMESG ==='
dmesg
echo '=== S31_SMOKE_END ==='
