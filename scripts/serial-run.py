"""Upload a small shell script over UART, run it and save raw UART evidence.

Requires an already logged-in root shell and pyserial 3.5. Bounded timeout;
does not reset the board or flash firmware. Terminal echo is restored on exit.
"""
import argparse
from pathlib import Path
import re
import sys
import time
import serial
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

p = argparse.ArgumentParser()
p.add_argument('--port', required=True)
p.add_argument('--script', required=True)
p.add_argument('--output', required=True)
p.add_argument('--seconds', type=float, default=150)
a = p.parse_args()
script = Path(a.script).read_text(encoding='utf-8-sig').replace('\r\n', '\n')
if 'S31_UPLOAD_EOF' in script:
    p.error('script contains reserved heredoc delimiter')
port = serial.Serial()
port.port, port.baudrate, port.timeout = a.port, 115200, 0.2
port.dtr = port.rts = False
port.open()
output = Path(a.output)
output.parent.mkdir(parents=True, exist_ok=True)
try:
    with output.open('wb') as log:
        def read_log():
            data = port.read(4096)
            if data:
                log.write(data)
                log.flush()
                sys.stdout.write(data.decode('utf-8', errors='replace').replace('\r', ''))
                sys.stdout.flush()
            return data

        port.write(b"stty -echo\r")
        time.sleep(0.3)
        read_log()
        payload = "cat > /tmp/s31-upload.sh <<'S31_UPLOAD_EOF'\n" + script.rstrip() + '\nS31_UPLOAD_EOF\n'
        # Pace input to avoid overrunning the UART/getty input buffer.
        for line in payload.splitlines():
            for offset in range(0, len(line), 64):
                port.write(line[offset:offset + 64].encode('utf-8'))
                time.sleep(0.02)
            port.write(b'\r')
            time.sleep(0.025)
        port.write(b"sh /tmp/s31-upload.sh; rc=$?; rm -f /tmp/s31-upload.sh; stty echo; echo S31_RUN_EXIT=$rc\r")
        deadline = time.monotonic() + a.seconds
        tail = b''
        while time.monotonic() < deadline:
            tail = (tail + read_log())[-8192:]
            match = re.search(rb'S31_RUN_EXIT=(\d+)\r*\n', tail)
            if match:
                sys.exit(0 if match.group(1) == b'0' else 1)
        raise TimeoutError('UART test did not finish before the bounded timeout; inspect the log')
finally:
    port.write(b'\r stty echo\r')
    port.close()
