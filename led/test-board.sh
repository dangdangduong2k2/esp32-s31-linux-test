#!/bin/sh
# Run after installing; briefly cycles colors, finishes red. No Wi-Fi secrets.
set -eu
echo LED_CHECK_BEGIN
uname -r
rgb-led --self-test
for args in '256 0 0' '-1 0 0' 'red extra' 'unknown'; do
    if /usr/libexec/s31-rgb-led $args; then
        echo 'FAIL: invalid argument accepted'
        exit 1
    else
        rc=$?
        [ "$rc" -eq 2 ] || exit 1
    fi
done
echo PASS_INVALID_ARGUMENTS
for color in off green blue white red; do
    rgb-led "$color"
    sleep 1
done
rgb-led 64 0 0
echo PASS_COLOR_TRANSFERS
s31-overlay remove rgb-led --volatile
if [ -e /dev/spidev2.0 ]; then
    echo 'FAIL: device remains after removing overlay'
    exit 1
fi
rgb-led red
echo PASS_OVERLAY_REAPPLY
s31-overlay status
gpioinfo -c gpiochip0 60
for stat in errors timedout transfers; do
    file="/sys/class/spi_master/spi2/statistics/$stat"
    if [ -f "$file" ]; then
        printf 'SPI_%s=' "$stat"
        cat "$file"
    fi
done
if [ -e /sys/class/net/wlan0/carrier ]; then
    printf 'WIFI_CARRIER='
    cat /sys/class/net/wlan0/carrier
fi
echo LED_CHECK_END
