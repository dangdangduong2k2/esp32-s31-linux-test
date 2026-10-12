import json
import pathlib
import subprocess
import sys

repo = pathlib.Path(__file__).resolve().parents[1]
work = pathlib.Path(sys.argv[1]).resolve()
lock = json.loads((repo / 'sources.lock.json').read_text())
for name in ('buildroot', 'external', 'bsp'):
    path = work / name
    spec = lock[name]
    if not path.exists():
        subprocess.run(['git', 'init', str(path)], check=True)
        subprocess.run(['git', '-C', str(path), 'remote', 'add', 'origin', spec['url']], check=True)
        subprocess.run(['git', '-C', str(path), 'fetch', '--depth=1', 'origin', spec['commit']], check=True)
        subprocess.run(['git', '-C', str(path), 'checkout', '--detach', 'FETCH_HEAD'], check=True)
    actual = subprocess.check_output(['git', '-C', str(path), 'rev-parse', 'HEAD'], text=True).strip()
    if actual != spec['commit']:
        raise SystemExit(f'{name}: revision differs from lock file')

config = (work / 'external/configs/espressif_esp32s31_function_core_board_nor_defconfig').read_text()
# Download exact source archives instead of fetching Linux's large Git history.
for name, prefix in [('linux', 'BR2_LINUX_KERNEL'), ('uboot', 'BR2_TARGET_UBOOT'), ('opensbi', 'BR2_TARGET_OPENSBI')]:
    spec = lock[name]
    config = '\n'.join(line for line in config.splitlines() if not line.startswith((prefix + '_CUSTOM_GIT=', prefix + '_CUSTOM_REPO_')))
    archive = spec['url'].removesuffix('.git') + '/archive/' + spec['commit'] + '.tar.gz'
    config += f'\n{prefix}_CUSTOM_TARBALL=y\n{prefix}_CUSTOM_TARBALL_LOCATION="{archive}"\n'
# Packaging scripts are supplied by our pinned BSP checkout through ESP_BSP_DIR.
config = config.replace('BR2_PACKAGE_HOST_ESP_LINUX_BSP=y', '# BR2_PACKAGE_HOST_ESP_LINUX_BSP is not set')
(work / 'external/configs/s31_test_defconfig').write_text(config)
overlay = work / 'external/board/espressif/esp32s31/rootfs_overlay/usr/bin'
overlay.mkdir(parents=True, exist_ok=True)
target = overlay / 's31-smoke'
target.write_bytes((repo / 'scripts/board-smoke.sh').read_bytes())
target.chmod(0o755)
