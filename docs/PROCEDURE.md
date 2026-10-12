# Quy trình tái lập

## 1. Chuẩn bị, UART và backup

Cáp data ở cổng **UART**, console **115200 8N1**. Một cáp đủ cho nạp và console; chỉ một chương trình mở COM tại một thời điểm. Phiên này COM56, máy khác có thể khác.

Đặt project, venv, downloads và log trên D:. Các lệnh giả sử đang ở repo, `python` thuộc venv trên D có `pyserial==3.5`, `esptool==5.5.0`:

```powershell
$env:TEMP='D:\Codex\Temp'
$env:TMP=$env:TEMP
$env:PYTHONUTF8='1'
python -m serial.tools.list_ports -v
python -m esptool --chip esp32s31 --port COM56 chip-id
python -m esptool --chip esp32s31 --port COM56 flash-id
python -m esptool --chip esp32s31 --port COM56 get-security-info
python -m esptool --chip esp32s31 --port COM56 --baud 460800 read-flash 0 ALL original-flash.bin
Get-FileHash original-flash.bin -Algorithm SHA256
```

Giữ backup riêng, không commit. Board lần này chưa bật secure boot/flash encryption; không ghi eFuse. Backup đã làm trước bài LED, không đọc Linux đã nạp rồi gọi đó là firmware gốc.

## 2. Chọn profile firmware

### A. Image cộng đồng đã test

Đọc [prebuilt.lock.json](../prebuilt.lock.json), tải đúng asset và kiểm tra SHA:

```powershell
$imageLock=Get-Content prebuilt.lock.json -Raw | ConvertFrom-Json
Invoke-WebRequest -Uri $imageLock.url -OutFile s31_full_flash.bin
if ((Get-FileHash s31_full_flash.bin -Algorithm SHA256).Hash.ToLowerInvariant() -ne $imageLock.sha256) { throw 'SHA256 mismatch' }
```

Tag `ci-d74660b8f90c-34182145900`, 14,880,768 byte. Đây là release cộng đồng, không phải binary repo này tự build. [Layout thực tế](../configs/tested-community-layout.cfg) khác layout chính thức.

Lệnh **cài mới** đã dùng trong phiên này, sau khi có backup:

```powershell
python -m esptool --chip esp32s31 --port COM56 --baud 460800 erase-flash
python -m esptool --chip esp32s31 --port COM56 --baud 460800 write-flash --flash-mode dio --flash-freq 80m --flash-size 16MB 0x0 s31_full_flash.bin
```

Erase và ghi image gộp có thể làm mất persistent data. Không dùng lại quy trình cài mới như update giữ dữ liệu; update cần image thành phần và layout upstream tương ứng. Chờ `Hash of data verified`. Nếu auto-reset không vào download: giữ BOOT, nhấn-thả RESET, thả BOOT rồi thử lại.

### B. Build nguồn chính thức — chưa thành công trong phiên này

Workflow `Build ESP32-S31 Linux` chạy thủ công qua Actions; job bị chặn billing trước khi thực thi. Không có compile log/artifact thành công. Sau khi xử lý billing có thể chạy lại; hoặc build trên Linux/WSL có filesystem Linux và backing volume đủ chỗ trên D:

```sh
bash scripts/build.sh
```

Cài host dependencies theo workflow. Script dùng Buildroot 2025.02, commit trong sources.lock.json, thêm s31-smoke, dùng BSP checkout riêng. Không dùng GCC bare-metal ESP-IDF làm toolchain Linux musl. Kết quả dự kiến là profile cramfs tối thiểu; không ngầm đồng nhất với image cộng đồng. Workflow/build script chưa được xác nhận end-to-end.

## 3. Boot và shell

Để người dùng nhập lệnh tương tác, mở console sau (đóng chương trình UART khác trước):

```powershell
python scripts/console.py COM56 115200 --raw --eol CR --rts 0 --dtr 0
```

Wrapper bật ANSI trên Windows 11 để menu không in thẳng mã điều khiển. Ctrl+] thoát về host; Ctrl+C gửi ngắt đến chương trình đang chạy trên board. Nhấn Enter, đăng nhập root nếu cần. Có thể dùng `esp32-config` và chọn Wireless LAN, hoặc dùng giao diện dòng lệnh dưới đây để tránh phụ thuộc menu:

```sh
esp32-config wifi configure
esp32-config wifi enable
esp32-config wifi status
ip -4 addr show wlan0
ip route
```

Lệnh configure hỏi SSID, passphrase 8–63 ký tự và nhập lại passphrase; nhập riêng trực tiếp qua UART, không đưa mật khẩu/profile Wi-Fi vào log Git. Enable có thể mất khoảng 35 giây hoặc lâu hơn khi chuẩn bị radio. Cần Connected và địa chỉ IP để xác nhận; các lệnh này được đối chiếu source của image, chưa có kết quả test kết nối Wi-Fi trong phiên smoke ban đầu.

Các lệnh dưới đây dành cho tự động capture/reset, không chạy cùng lúc terminal tương tác:

```powershell
python scripts/serial-capture.py --port COM56 --reset --seconds 40 --output evidence/boot.log
python scripts/serial-capture.py --port COM56 --send root --seconds 5 --output evidence/login.log
```

Image đã test cho username `root` không cần password trên UART. Đọc uname, /proc/cpuinfo, /proc/meminfo, /proc/mounts, /proc/mtd. Không suy ra Linux hỗ trợ phần cứng chỉ từ thông số board.

Image chạy rcS ở nền để getty lên sớm. Shell xuất hiện chưa đồng nghĩa mọi dịch vụ đã xong. Kiểm tra /run/rcS.done, /run/rcS.status, /run/rcS.log; phiên này ở uptime 33.66s đã có status 0. Log ghi không có USB swap và Wi-Fi disabled.

## 4. Smoke, reboot, lưu bền

Khi đã ở root shell:

```powershell
python scripts/serial-run.py --port COM56 --script scripts/board-smoke.sh --seconds 150 --output evidence/linux-smoke.log
```

Script upload qua UART rồi chạy: kiểm kê, tmpfs 256 KiB copy/cmp/checksum, root write probe có xóa, 2 worker 10.000 vòng, loopback, mạng/USB, chờ 60 giây và dmesg. Đọc từng kết quả trong log; exit 0 không tự thay cho đánh giá mọi mục kiểm kê.

Tạo marker riêng ở root shell (vài byte filesystem, không ghi raw MTD):

```sh
if test ! -e /root/.s31-persist-probe; then
  echo S31_PERSIST_20261012 > /root/.s31-persist-probe
  echo VOLATILE > /tmp/s31-volatile-probe
  sync
else
  echo PROBE_EXISTS_ABORT
fi
```

Nếu PROBE_EXISTS_ABORT, kiểm tra marker cũ trước. Trên host:

```powershell
python scripts/serial-reboot.py --port COM56 --mode software --cycles 2 --output evidence/software-reboot.log
python scripts/serial-reboot.py --port COM56 --mode rts --output evidence/hardware-reset.log
```

Reboot test kiểm tra về shell sớm; vòng kế tiếp có thể bắt đầu khi rcS còn chạy. Shutdown FAIL lúc đó cần đối chiếu trạng thái dịch vụ, không đánh đồng kernel không boot.

Cold boot: sync, đóng serial, rút nguồn ít nhất 5 giây rồi cắm UART lại:

```powershell
python scripts/serial-reboot.py --port COM56 --mode login --output evidence/cold-boot-login.log
```

Mode login chỉ xác nhận shell/marker sau thao tác vật lý, không tự ngắt nguồn. Kết thúc xóa đúng marker đã tạo và sync; không xóa dữ liệu khác.

## 5. Ngoại vi và phục hồi

Ethernet/Wi-Fi cần cấu hình và mạng thử, USB cần thiết bị, GPIO/I2C/audio cần dây và sơ đồ chân. Phiên này chỉ kiểm kê; chưa test các chức năng đó. Không bật ngẫu nhiên GPIO.

Muốn phục hồi dùng đúng backup riêng:

```powershell
python -m esptool --chip esp32s31 --port COM56 --baud 460800 write-flash 0x0 original-flash.bin
```

Đây chỉ là hướng dẫn; kết thúc phiên vẫn để Linux trên board.

## 6. Git

Commit scripts, docs, lock/config, log và SHA manifest. Không commit binary, venv, tài khoản Codex/GitHub hoặc backup. Chưa làm ghi NOT TESTED, build bị chặn ghi BLOCKED; không đổi thành PASS để hoàn tất bảng.
