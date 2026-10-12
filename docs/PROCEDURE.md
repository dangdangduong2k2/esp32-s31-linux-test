# Quy trình test

## 1. Chuẩn bị và nhận diện

1. Dùng cáp USB có dữ liệu, nối cổng Type-C UART để xem console Linux. Nếu có hai dây có thể giữ thêm USB Serial/JTAG cho nạp. Không nhầm USB Type-A host với cổng console.
2. Trên Windows tìm COM bằng `python -m serial.tools.list_ports -v`. Lần test này: USB Serial/JTAG ban đầu COM55; sau chuyển dây, CP210x UART là COM56.
3. Đóng mọi serial monitor đang chiếm cổng. Đọc chip và flash:

```powershell
python -m esptool --port COM56 chip-id
python -m esptool --port COM56 flash-id
```

4. Trước khi thay firmware, đọc toàn flash 16 MiB và tính SHA-256. Phiên này đã có bản sao từ trước test LED. Giữ riêng, không commit bản sao lên GitHub vì có thể chứa dữ liệu thiết bị.

```powershell
python -m esptool --chip esp32s31 --port COM56 --baud 460800 read-flash 0 ALL original-flash.bin
Get-FileHash original-flash.bin -Algorithm SHA256
```

## 2. Build có thể tái lập

1. Mở Actions, chạy `Build ESP32-S31 Linux` bằng workflow_dispatch.
2. Script khóa Buildroot và các nguồn trong `sources.lock.json`; lấy archive theo commit cho kernel/OpenSBI/U-Boot để tránh tải lịch sử Git lớn.
3. Giữ defconfig chính thức, thêm `/usr/bin/s31-smoke` vào rootfs. Dùng BSP checkout đã khóa qua `ESP_BSP_DIR` thay vì package kéo nhánh động.
4. Tải artifact thành công, kiểm tra `SHA256SUMS`. Giữ run ID, commit repo, build log và config.
5. Kết quả: SPL + OpenSBI/U-Boot FIT + DTB + XIP kernel + cramfs được gộp vào `s31_full_flash.bin`.

## 3. Nạp

Image gộp nạp tại **0x0**. BSP quy định header SPL **DIO, 80 MHz, 16 MiB**; không tự đổi thành thông số của bài LED.

```powershell
python -m esptool --chip esp32s31 --port COM56 --baud 460800 write-flash 0x0 s31_full_flash.bin
```

Chờ `Hash of data verified`. Nếu auto-reset không vào download: giữ BOOT, nhấn-thả RESET, thả BOOT rồi nạp lại. Không ghi eFuse và không cần erase toàn chip trước khi nạp image này.

## 4. Kiểm thử thực tế

1. Ghi log UART **115200, 8N1**, từ reset đến shell. Xác nhận từng tầng SPL, OpenSBI, U-Boot, kernel và userspace.
2. Chạy `uname -a`, `/proc/cpuinfo`, `/proc/meminfo`, `/proc/mtd`, `/proc/mounts`, `/proc/cmdline`.
3. Chạy `s31-smoke`: tệp tmpfs 256 KiB, so sánh bản sao, hai tiến trình tính vòng lặp 10.000 bước, đọc danh sách mạng/USB và dmesg. Không suy ra SMP chỉ từ việc chạy hai tiến trình.
4. Kiểm tra ghi root bị từ chối đúng như cramfs chỉ đọc; ghi `/tmp` phải thành công.
5. Chờ tối thiểu 60 giây ở shell; kiểm tra uptime tăng và không tự reset/panic. Đây chỉ là smoke test, không phải chứng nhận ổn định dài hạn.
6. Thử reboot phần mềm và reset phần cứng nhiều lần; phân biệt reboot với cold boot. Cold boot cần ngắt rồi cấp nguồn thật.
7. Chỉ test Ethernet khi có dây/link: xem interface, carrier, DHCP, ping gateway. Không có cáp thì đánh dấu NOT TESTED/BLOCKED, không gọi driver lỗi.
8. USB/GPIO/I2C chỉ kiểm kê mặc định; kiểm thử chức năng cần thiết bị và sơ đồ chân cụ thể. Không bật ngẫu nhiên GPIO hay ghi thanh ghi ngoại vi.

## 5. Phục hồi

Vào ROM download rồi ghi lại **đúng bản sao của board này**:

```powershell
python -m esptool --chip esp32s31 --port COM56 --baud 460800 write-flash 0x0 original-flash.bin
```

Xác nhận SHA/hash và reset. Đây là hướng dẫn phục hồi; không tự phục hồi nếu vẫn đang dùng Linux để test.

## 6. Đưa kết quả lên Git

Commit hướng dẫn, script, source lock, config và log đã rà soát. Giữ riêng flash backup, khóa, token, mật khẩu và dữ liệu thiết bị. Binaries build để trong Actions artifact; ghi SHA-256 vào báo cáo. Mọi PASS phải trỏ đến log thực tế, mọi bước chưa chạy phải ghi rõ.
