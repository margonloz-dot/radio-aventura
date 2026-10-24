"""Supervisor local de Radio Aventura para Windows. Sólo biblioteca estándar."""
from __future__ import annotations

import argparse
import ctypes
from ctypes import wintypes
import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import subprocess
import sys
import time
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'datos'
STOP = DATA / 'servidor.detener'
STATUS = DATA / 'servidor.json'
ADDRESS = 'http://127.0.0.1:8765'
APP_ID = json.loads((ROOT / 'curso.json').read_text(encoding='utf8'))['app_id']
CHECK_SECONDS = 5


def healthy() -> bool:
    try:
        with urlopen(ADDRESS + '/api/course', timeout=3) as response:
            return json.load(response).get('app_id') == APP_ID
    except Exception:
        return False


def exclusive_lock():
    """Windows cierra el bloqueo automáticamente si termina el supervisor."""
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD,
                                  wintypes.DWORD, wintypes.LPVOID,
                                  wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    kernel.CreateFileW.restype = wintypes.HANDLE
    handle = kernel.CreateFileW(str(DATA / 'servidor.lock'), 0xC0000000,
                                0, None, 4, 0x80, None)
    if handle == ctypes.c_void_p(-1).value:
        error = ctypes.get_last_error()
        if error == 32:  # Otro supervisor ya conserva el bloqueo.
            return kernel, None
        raise ctypes.WinError(error)
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.CloseHandle.restype = wintypes.BOOL
    return kernel, handle


def terminate(child):
    # Sólo se detiene el proceso hijo creado por este supervisor.
    if child is not None and child.poll() is None:
        child.terminate()
        try:
            child.wait(timeout=10)
        except subprocess.TimeoutExpired:
            child.kill()
            child.wait(timeout=5)


def supervise():
    import os
    DATA.mkdir(exist_ok=True)
    kernel, handle = exclusive_lock()
    if handle is None:
        return
    logger = logging.getLogger('radio-supervisor')
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler(DATA / 'servidor.log', maxBytes=256000,
                                   backupCount=2, encoding='utf8')
    handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
    logger.addHandler(handler)
    STOP.unlink(missing_ok=True)
    child = None
    failures = 0
    previous = None
    started = time.strftime('%Y-%m-%dT%H:%M:%S')
    logger.info('Supervisor iniciado; PID=%s; %s', os.getpid(), ADDRESS)
    try:
        while not STOP.exists():
            if child is not None and child.poll() is not None:
                logger.warning('El servidor terminó con código %s; se reiniciará.', child.returncode)
                child = None
            ready = healthy()
            if ready:
                failures = 0
            else:
                failures += 1
                if child is not None and failures >= 3:
                    logger.warning('El servidor no responde; reiniciando el proceso propio.')
                    terminate(child)
                    child = None
                if child is None:
                    # Python sin consola. No depende de la terminal de Codex.
                    python = Path(sys.executable).with_name('python.exe')
                    child = subprocess.Popen(
                        [str(python), str(ROOT / 'app.py'), '--no-browser', '--port', '8765'],
                        cwd=ROOT, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL, close_fds=True,
                        creationflags=subprocess.CREATE_NO_WINDOW)
                    failures = 0
                    logger.info('Servidor iniciado; PID=%s', child.pid)
            state = (ready, child.pid if child else None)
            if state != previous:
                payload = {'supervisor_pid': os.getpid(), 'server_pid': state[1],
                           'url': ADDRESS, 'healthy': ready, 'started': started,
                           'checked': time.strftime('%Y-%m-%dT%H:%M:%S')}
                temp = STATUS.with_suffix('.tmp')
                temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf8')
                temp.replace(STATUS)
                if ready:
                    logger.info('Servidor disponible: %s', ADDRESS)
                previous = state
            # La detención manual se reconoce en menos de un segundo.
            for _ in range(CHECK_SECONDS * 2):
                if STOP.exists():
                    break
                time.sleep(.5)
    finally:
        terminate(child)
        STATUS.unlink(missing_ok=True)
        logger.info('Supervisor detenido. El progreso se conserva.')
        handler.close()
        kernel.CloseHandle(handle)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stop', action='store_true', help='Detener hasta el siguiente inicio manual o de sesión.')
    args = parser.parse_args()
    if args.stop:
        DATA.mkdir(exist_ok=True)
        STOP.write_text('Detención solicitada por el usuario.\n', encoding='utf8')
        print('Se solicitó detener el servidor. Tu partida se conserva.')
    else:
        supervise()
