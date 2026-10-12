"""Create a UART-uploadable installer, with hashes verified on the board."""
import argparse
import base64
import hashlib
from pathlib import Path

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--build-dir', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
files = [
    (a.build_dir / 'rgb-led.elf', 'rgb-led', '/usr/libexec/s31-rgb-led', '755'),
    (a.build_dir / 'esp32s31-overlay-rgb-led.dtbo', 'rgb-led.dtbo',
     '/usr/lib/s31-overlays/esp32s31-overlay-rgb-led.dtbo', '644'),
    (Path(__file__).with_name('rgb-led.sh'), 'rgb-led.sh', '/usr/bin/rgb-led', '755'),
]
lines = ['#!/bin/sh', 'set -eu', 'echo LED_INSTALL_BEGIN',
         'stage=$(mktemp -d /tmp/rgb-led-install.XXXXXX)',
         "trap 'rm -rf \"$stage\"' EXIT HUP INT TERM"]
for src, temp, dest, mode in files:
    data = src.read_bytes()
    if src.suffix == '.sh':
        data = data.replace(b'\r\n', b'\n')
    lines += [f'base64 -d > "$stage/{temp}" <<\'LED_DATA_EOF\'',
              base64.encodebytes(data).decode().strip(), 'LED_DATA_EOF',
              f'echo "{hashlib.sha256(data).hexdigest()}  $stage/{temp}" | sha256sum -c -']
lines += ['chmod 755 "$stage/rgb-led"', '"$stage/rgb-led" --self-test',
          'mkdir -p /usr/libexec /usr/lib/s31-overlays']
for src, temp, dest, mode in files:
    lines += [f'cp "$stage/{temp}" {dest}.new', f'chmod {mode} {dest}.new',
              f'mv {dest}.new {dest}']
lines += ['sync', 'rgb-led red', 'echo LED_INSTALL_END']
a.output.write_text('\n'.join(lines) + '\n', encoding='ascii', newline='\n')
