# Ma trận kiểm thử — 12/10/2026

Các PASS Linux thuộc **image cộng đồng trong prebuilt.lock.json**, không phải image chính thức trong sources.lock.json.

| ID | Bài kiểm tra | Kết quả | Bằng chứng / giới hạn |
|---|---|---|---|
| T01 | Nhận dạng chip, flash | PASS | [Flash log](../evidence/linux-flash.log): S31 rev v0.0; backup 16 MiB ở JOURNAL |
| T02 | Backup trước thay firmware | PASS | SHA-256 trong JOURNAL; binary giữ riêng |
| T03 | UART CP210x COM56 | PASS | Login và các log UART; một cáp UART |
| T04 | Build từ nguồn chính thức | BLOCKED | [Annotation Actions](../evidence/actions-run-38204464647-annotations.json): billing, job chưa chạy |
| T05 | SHA image và nạp flash | PASS | [prebuilt.lock.json](../prebuilt.lock.json), flash log `Hash of data verified` |
| T06 | Boot đến root shell | PASS | [First boot](../evidence/linux-first-boot.log), [login](../evidence/linux-login.log), software reboot; SPL/U-Boot/Linux, kernel nhận SBI implementation Version=0x10009, SBI API v3.0; không có banner OpenSBI riêng trong log |
| T07 | CPU/RAM/MMU/MTD/mount | PASS | [Inventory](../evidence/linux-inventory.log): 2 CPU, sv32, MemTotal 15640 kB, OverlayFS rw |
| T08 | Tmpfs 256 KiB copy/cmp | PASS | [Smoke](../evidence/linux-smoke.log): checksum `3975907619`, 262144 byte cho cả hai tệp |
| T09 | Root ghi được và lưu qua boot | PASS | Smoke + [software reboot](../evidence/software-reboot.log) + [RTS](../evidence/hardware-reset.log) + [cold boot](../evidence/cold-boot-login.log): `PASS_PERSIST` |
| T10 | Hai tiến trình 10.000 vòng | PASS | Smoke: A và B hoàn tất; không phải benchmark SMP scaling |
| T11 | Ổn định 60 giây | PASS | Smoke: uptime 5960.43 → 6020.53, không thấy panic/OOM/reset trong cửa sổ quan sát |
| T12 | Software reboot 2 lần + RTS reset 1 lần | PASS | Mỗi lần root shell, 2 CPU online, persistent marker còn |
| T13 | Rút nguồn 5 giây rồi cắm UART | PASS có giới hạn | Người dùng xác nhận thao tác; cold-boot-login ghi shell uptime 11.60s và marker còn. Không thu ROM/boot log sớm của lần cắm này; không đo điện áp |
| T14 | Ethernet | NOT TESTED | Không có Ethernet trong kiểm kê smoke ban đầu; không suy ra Ethernet hỏng |
| T15 | USB thiết bị ngoài | NOT TESTED | Root hub `usb1`, `1-0:1.0` có; chưa test thiết bị ngoài |
| T16 | GPIO/I2C/audio/Bluetooth | NOT TESTED | GPIO node có; I2C node/soundcard vắng; Wi-Fi được kiểm tra riêng ở T20 |
| T17 | Loopback IPv4 | PASS | Smoke: ping 127.0.0.1, 3/3 gói, 0% loss; không chứng minh có Internet |
| T18 | Tmpfs không lưu qua reboot | PASS | Setup có marker VOLATILE; recovery sau reboot đầu báo PASS_TMP_CLEARED. Các reboot sau chỉ kiểm tra marker tiếp tục vắng |
| T19 | Dịch vụ khởi động xong | PASS | [Services settled](../evidence/services-settled.log): uptime 33.66s, rcS.status=0, rcS.done, syslog/klog/network/crond OK; chưa cấu hình mạng ngoài |
| T20 | Wi-Fi WPA2, DHCP, ping gateway | PASS sau sửa cấu hình | [Kết nối](../evidence/wifi-retry.log), [ping](../evidence/wifi-data-path.log): Connected, APPLY_RC=0, IPv4/default route, ping 3/3, 0% loss. Khóa profile cũ không khớp mật khẩu người dùng cung cấp; đã xác minh lại trước khi kết nối |

Reboot đầu đưa board về shell và giữ marker nhưng công cụ host lỗi encoding khi ghi console. Log giữ riêng; không cộng vào hai vòng có log đầy đủ.

RAM vật lý/DT là 16 MiB, khác MemTotal/MemAvailable. Flash vật lý 16 MiB, cửa sổ MTD Linux đăng ký 15360 KiB (15 MiB). Offset MTD trong dmesg tương đối với cửa sổ flash, không dùng trực tiếp làm offset esptool.

Wi-Fi được test sau smoke: MemAvailable 7884 kB lúc kết nối và ping; đây là một snapshot, không phải peak RAM. SSID, MAC và địa chỉ LAN đã được che trong bản log public. Chưa test Wi-Fi reconnect sau reboot, roaming, Internet/DNS hoặc throughput.

Chưa làm: soak nhiều giờ, ép RAM đến giới hạn, benchmark, build tái lập binary, kiểm thử bảo mật kernel và các ngoại vi còn lại. Không suy ra các mục này PASS từ việc có shell.
