# Evidence — 12/10/2026

| Log | Nội dung |
|---|---|
| actions-run-38204464647-annotations.json | GitHub chặn job do billing trước khi thực thi |
| linux-erase.log / linux-flash.log | Cài mới community image; hash nạp verified |
| linux-first-boot.log | Reset sau nạp đến login |
| uart-resume.log / linux-login.log | Console và root shell |
| linux-inventory.log | CPU/RAM/MMU/mount/MTD |
| linux-smoke.log | Tệp tạm, 2 workers, loopback, 60s, dmesg |
| persistence-setup.log | Tạo marker riêng và sync |
| software-reboot-host-encoding-error.log | Reboot đầu, capture ngắt do host encoding; không phải log boot đầy đủ |
| software-reboot-recovery.log | Login sau lần lỗi capture: marker bền còn, marker volatile mất |
| software-reboot.log | 2 reboot có log đầy đủ |
| hardware-reset.log | 1 reset qua RTS có log |
| services-after-reboot.log | Dịch vụ chưa xong khi shell đã có |
| services-settled.log | rcS hoàn tất với status 0 |
| cold-boot-login.log | Login sau người dùng rút/cắm nguồn; không có boot log sớm |
| final-state.log | Trạng thái cuối và xóa marker thử nghiệm |
| wifi-initial-failure.txt | Trích log do người dùng gửi: kết nối WPA2 timeout reason=15 |
| wifi-credential-check.json | Kết quả boolean đối chiếu trước/sau sửa; không chứa password/PSK |
| wifi-retry.log | WPA2 Connected, DHCP và default route; nhận dạng mạng đã che |
| wifi-data-path.log | Ping gateway 3/3 và snapshot RAM sau kết nối |

Log UART giữ CR/ANSI và có thể có vài byte không giải mã được lúc reset. serial-run/reboot ghi bytes; serial-capture giải mã UTF-8 với replacement. Dòng [HOST ...] là thời gian UTC máy tính; giờ kernel là uptime, không phải ngày giờ lịch đã đồng bộ. Ngày thao tác ở Asia/Ho_Chi_Minh là 12/10/2026.

SHA256SUMS bảo vệ tính toàn vẹn các log trong phiên bản này, không chứng nhận firmware là an toàn hay tự build. Firmware SHA nằm ở prebuilt.lock.json. MAC thiết bị trong log flash được thay bằng [REDACTED]; log Wi-Fi thay SSID và địa chỉ LAN bằng nhãn. Bản gốc riêng không commit. Không kèm binary backup, password/PSK, token hoặc tài khoản máy tính.

Source đối chiếu behavior: [community inittab tại commit đã chọn](https://github.com/GrieferPig/esp32-s31-linux/blob/d74660b8f90c6fd0c16b54115320e748766c6df7/buildroot-external/board/esp32-s31/overlay/etc/inittab), [layout](../configs/tested-community-layout.cfg). Source mô tả không thay thế kết quả thực nghiệm.
