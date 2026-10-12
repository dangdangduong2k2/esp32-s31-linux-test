#!/bin/sh
# SPDX-License-Identifier: MIT
# Persistent command; the hardware overlay is applied only for this boot.
set -eu
BIN=/usr/libexec/s31-rgb-led
case "${1:-}" in
    --self-test) exec "$BIN" "$@" ;;
    -h|--help|'')
        echo 'rgb-led red|green|blue|white|off'
        echo 'rgb-led R G B   (each 0..255)'
        exit 0 ;;
esac
case "$(uname -r)" in
    6.18.0-g888671b7ed45) ;;
    *) echo 'rgb-led: this overlay is validated only on kernel 6.18.0-g888671b7ed45' >&2; exit 1 ;;
esac
if ! s31-overlay status | grep -q '^active: rgb-led .*gpios=1000000000000000$'; then
    s31-overlay apply rgb-led --volatile
fi
if [ ! -c /dev/spidev2.0 ]; then
    echo 'rgb-led: /dev/spidev2.0 is missing; inspect dmesg and s31-overlay status' >&2
    exit 1
fi
exec "$BIN" "$@"
