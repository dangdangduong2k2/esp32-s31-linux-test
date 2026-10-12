"""Bounded reboot/reset test on an already logged-in S31 UART console."""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import sys
import time
import serial
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

p = argparse.ArgumentParser()
p.add_argument('--port', required=True)
p.add_argument('--output', required=True)
p.add_argument('--mode', choices=['software', 'rts', 'login'], required=True)
p.add_argument('--cycles', type=int, default=1)
a = p.parse_args()
s = serial.Serial()
s.port, s.baudrate, s.timeout = a.port, 115200, 0.2
s.dtr = s.rts = False
s.open()
path = Path(a.output)
path.parent.mkdir(parents=True, exist_ok=True)
try:
    with path.open('wb') as log:
        def event(message):
            line = f'\n[HOST {datetime.now(timezone.utc).isoformat()}] {message}\n'
            log.write(line.encode())
            log.flush()
            print(line, end='', flush=True)

        def expect(marker, seconds=60):
            deadline, tail = time.monotonic() + seconds, b''
            while time.monotonic() < deadline:
                data = s.read(4096)
                if data:
                    log.write(data)
                    log.flush()
                    sys.stdout.write(data.decode('utf-8', errors='replace').replace('\r', ''))
                    sys.stdout.flush()
                    tail = (tail + data)[-32768:]
                    if marker in tail:
                        return tail
            raise TimeoutError(f'No {marker!r} within {seconds}s')

        for cycle in range(1, a.cycles + 1):
            event(f'BEGIN mode={a.mode} cycle={cycle}')
            if a.mode == 'software':
                s.write(b'sync; reboot\r')
            elif a.mode == 'rts':
                s.rts = True
                time.sleep(0.15)
                s.rts = False
            else:
                s.write(b'\r')
            expect(b'login:', 75)
            s.write(b'root\r')
            expect(b'~ #', 15)
            s.write(b'stty -echo\r')
            time.sleep(0.3)
            command = (
                'echo ===AFTER_BOOT===; uname -r; cat /proc/uptime; '
                'cat /sys/devices/system/cpu/online; '
                'if test "$(cat /root/.s31-persist-probe 2>/dev/null)" = S31_PERSIST_20261012; '
                'then echo PASS_PERSIST; else echo FAIL_PERSIST; fi; '
                'if test ! -e /tmp/s31-volatile-probe; then echo PASS_TMP_CLEARED; '
                'else echo FAIL_TMP_CLEARED; fi; echo S31_REBOOT_CHECK_END; stty echo\r'
            )
            s.write(command.encode())
            result = expect(b'S31_REBOOT_CHECK_END', 15)
            if b'PASS_PERSIST' not in result or b'PASS_TMP_CLEARED' not in result or b'FAIL_' in result:
                raise RuntimeError('Persistence/volatile check failed; inspect evidence')
            event(f'PASS mode={a.mode} cycle={cycle}')
finally:
    s.close()
