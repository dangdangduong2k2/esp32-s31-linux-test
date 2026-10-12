"""UART terminal with explicit Windows ANSI support, including Windows 11.

Requires pyserial. Ctrl+] exits. Does not record commands or credentials.
All miniterm options remain available; defaults are COM56/115200, RTS/DTR=0.
"""
import ctypes
from ctypes import wintypes
import os
import sys


def enable_windows_ansi():
    if os.name != 'nt':
        return None, []
    api = ctypes.WinDLL('kernel32', use_last_error=True)
    api.GetStdHandle.argtypes = [wintypes.DWORD]
    api.GetStdHandle.restype = wintypes.HANDLE
    api.GetConsoleMode.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
    api.GetConsoleMode.restype = wintypes.BOOL
    api.SetConsoleMode.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    api.SetConsoleMode.restype = wintypes.BOOL
    saved = []
    for stream_id in (-11, -12):
        handle = api.GetStdHandle(wintypes.DWORD(stream_id))
        old = wintypes.DWORD()
        if not api.GetConsoleMode(handle, ctypes.byref(old)):
            if stream_id == -11:
                raise RuntimeError('Open this script in an interactive Windows console, without output redirection.')
            continue
        if not api.SetConsoleMode(handle, old.value | 0x0004):
            raise ctypes.WinError(ctypes.get_last_error())
        saved.append((handle, old.value))
    return api, saved


def main():
    api, saved = enable_windows_ansi()
    try:
        if sys.argv[1:] == ['--check-console']:
            for handle, _ in saved:
                mode = wintypes.DWORD()
                assert api.GetConsoleMode(handle, ctypes.byref(mode))
                assert mode.value & 0x0004
            print('\x1b[32mANSI console mode enabled; no serial port opened.\x1b[0m')
            return
        from serial.tools import miniterm
        miniterm.main(default_port='COM56', default_baudrate=115200,
                      default_rts=0, default_dtr=0)
    finally:
        for handle, old in saved:
            api.SetConsoleMode(handle, old)


if __name__ == '__main__':
    main()
