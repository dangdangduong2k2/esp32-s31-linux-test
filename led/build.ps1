param(
    [Parameter(Mandatory=$true)][string]$Compiler,
    [Parameter(Mandatory=$true)][string]$Python,
    [string]$OutDir = "$PSScriptRoot/../.work/led"
)
$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force $OutDir | Out-Null
$OutDir = (Resolve-Path -LiteralPath $OutDir).Path
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:TEMP = $OutDir
$env:TMP = $OutDir
& $Python "$PSScriptRoot/build-overlay.py" --out $OutDir
if ($LASTEXITCODE -ne 0) { throw 'Overlay build failed' }
& $Compiler -march=rv32imac -mabi=ilp32 -mcmodel=medany -msmall-data-limit=0 `
    -Os -Wall -Wextra -Werror -fno-builtin -fno-stack-protector `
    -nostdlib -nostartfiles -static '-Wl,--no-relax,-e,_start,--build-id=none,-z,max-page-size=4096' `
    "$PSScriptRoot/rgb-led.c" -o "$OutDir/rgb-led.elf"
if ($LASTEXITCODE -ne 0) { throw 'RV32 Linux ELF build failed' }
Write-Output "Built $OutDir/rgb-led.elf and esp32s31-overlay-rgb-led.dtbo"
