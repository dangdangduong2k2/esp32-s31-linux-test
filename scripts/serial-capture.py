"""Capture a bounded UART session, optionally reset and send a command.

Python 3 + pyserial 3.5. Output is raw UTF-8-decoded UART text, no invented timestamps.
"""
import argparse
import pathlib
import sys
import time
import serial
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

p = argparse.ArgumentParser()
p.add_argument('--port', required=True)
p.add_argument('--output', required=True)
p.add_argument('--seconds', type=float, default=30)
p.add_argument('--reset', action='store_true')
p.add_argument('--send')
args = p.parse_args()
s = serial.Serial()
s.port = args.port
s.baudrate = 115200
s.timeout = 0.2
s.dtr = False
s.rts = False
s.open()
path = pathlib.Path(args.output)
path.parent.mkdir(parents=True, exist_ok=True)
try:
    with path.open('w', encoding='utf-8', newline='') as log:
        if args.reset:
            s.rts = True
            time.sleep(0.15)
            s.rts = False
        if args.send is not None:
            s.write((args.send + '\r').encode())
        deadline = time.monotonic() + args.seconds
        while time.monotonic() < deadline:
            text = s.read(4096).decode('utf-8', errors='replace')
            if text:
                log.write(text)
                log.flush()
                sys.stdout.write(text)
                sys.stdout.flush()
finally:
    s.close()
