# ESP32-S31 Function CoreBoard: kiểm thử Linux trên board thật

**Đã chạy Linux 6.18 đến root shell, kiểm tra RAM/userspace, reboot, reset và khởi động lại sau ngắt nguồn ngày 12/10/2026.** Đây là smoke test, chưa phải kiểm chứng ổn định dài hạn hoặc toàn bộ ngoại vi.

Board Function CoreBoard-1, chip rev v0.0, flash vật lý 16 MiB; console CP210x UART 115200 8N1 (COM56). Người dùng chỉ dùng một dây ở cổng UART.

| Đã đo trên board | Kết quả |
|---|---|
| Kernel | `6.18.0-g888671b7ed45`, RISC-V 32-bit, MMU `sv32` |
| CPU | 2 hart/CPU online, `/sys/devices/system/cpu/online = 0-1` |
| RAM | MemTotal 15640 kB; MemAvailable 10392 kB đầu smoke, 9780 kB cuối smoke |
| Tệp tạm | Ghi/copy/cmp 256 KiB đạt; tmpfs mất dữ liệu sau reboot như dự kiến |
| Userspace | Hai tiến trình 10.000 vòng hoàn tất; ping loopback 3/3 |
| Lưu bền | Root OverlayFS ghi được; marker còn qua software reboot, RTS reset và ngắt/cấp nguồn |
| Ổn định ngắn | Uptime 5960.43 → 6020.53 giây, không thấy panic/reset trong cửa sổ này |
| Khởi động lại | 2 software reboot có log đầy đủ, 1 RTS reset, 1 ngắt/cấp nguồn do người dùng thực hiện đều về shell |
| Wi-Fi bổ sung | WPA2 kết nối, DHCP cấp IPv4, ping gateway 3/3; cấu hình mật khẩu cũ không khớp, đã lưu lại và test thành công |

## LED RGB từ Linux

Đã cài `rgb-led red|green|blue|white|off`; người dùng xác nhận LED đỏ. [Mã nguồn, cách dùng/build và các lỗi có điều kiện](docs/LINUX-LED.md). Dùng SPI phần cứng trên GPIO60, giữ kernel và kết nối Wi-Fi.

## Image đã test và hướng build còn bị chặn

**Image đã nạp là bản cộng đồng [GrieferPig/esp32-s31-linux](https://github.com/GrieferPig/esp32-s31-linux/releases/tag/ci-d74660b8f90c-34182145900)**, tag `ci-d74660b8f90c-34182145900`, commit `d74660b8f90c6fd0c16b54115320e748766c6df7`. Nó dùng SMP, SquashFS + JFFS2/OverlayFS và có IPv6. URL và SHA-256 nằm trong [prebuilt.lock.json](prebuilt.lock.json). SHA xác nhận asset đã tải/nạp, không chứng minh binary được tự build hoặc tái lập từ source trong phiên này.

Hướng **build cấu hình tối thiểu chính thức Espressif** được giữ trong [sources.lock.json](sources.lock.json), `configs/upstream-*` và workflow. [Actions run 38204464647](https://github.com/dangdangduong2k2/esp32-s31-linux-test/actions/runs/38204464647) không bắt đầu job do tài khoản bị khóa billing. **Chưa build kernel/firmware từ nguồn thành công trong repo này.** Chương trình userspace điều khiển LED đã được build riêng và chạy trên image có sẵn. Cấu hình chính thức có cramfs chỉ đọc, một CPU node và không bật IPv6; không dùng các đặc điểm đó mô tả image cộng đồng đã test.

## Tài liệu và bằng chứng

- [Quy trình tái lập, nạp và phục hồi](docs/PROCEDURE.md).
- [Nhật ký các bước đã thực hiện](docs/JOURNAL.md).
- [Ma trận PASS / BLOCKED / NOT TESTED](docs/RESULTS.md).
- [Lỗi đã gặp, hành vi theo cấu hình và lỗi có điều kiện](docs/ERRORS.md).
- [Danh mục log và giới hạn bằng chứng](evidence/README.md).

USB chỉ kiểm kê root hub; GPIO có thiết bị character; chưa có `/dev/i2c*` hoặc soundcard trong phiên smoke. Wi-Fi đã được test bổ sung: kết nối WPA2, DHCP và ping gateway đạt; chưa test Internet/DNS, roaming hoặc reconnect sau reboot. Ethernet, Bluetooth, audio và ngoại vi khác chưa được xác nhận hoạt động. Image cho root login qua UART không hỏi mật khẩu; đây không phải cấu hình để triển khai dịch vụ mạng công khai.

Không thể đảm bảo liệt kê mọi lỗi tồn tại. Repo phân biệt lỗi đã quan sát, điều kiện tất định của từng cấu hình và rủi ro chưa tái hiện. Flash backup riêng được giữ ngoài Git; không upload backup, mật khẩu hoặc token.
