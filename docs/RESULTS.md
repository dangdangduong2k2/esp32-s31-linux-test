# Ma trận kiểm thử

Ngày 12/10/2026. Trạng thái khởi tạo trước khi build/nạp Linux; sẽ cập nhật theo log thật.

| Test | Tiêu chí | Trạng thái | Bằng chứng |
|---|---|---|---|
| T01 | Nhận đúng chip ESP32-S31, flash 16 MiB | PASS (bài LED) | esptool, backup 16 MiB |
| T02 | Sao lưu trước thay firmware | PASS | SHA-256 trong JOURNAL |
| T03 | UART Windows nhận đúng CP210x | PASS | COM56, driver OK |
| T04 | Build image Linux thành công, có SHA/config | NOT TESTED | Chờ Actions |
| T05 | Nạp image, hash khớp | NOT TESTED | Chờ build |
| T06 | Boot đủ SPL/OpenSBI/U-Boot/Linux/root shell | NOT TESTED | Chờ UART log |
| T07 | Xác nhận uname/CPU/memory/MTD | NOT TESTED | Chờ shell |
| T08 | Ghi/đọc/so sánh tmpfs 256 KiB | NOT TESTED | s31-smoke |
| T09 | Root cramfs từ chối ghi đúng thiết kế | NOT TESTED | s31-smoke |
| T10 | Hai tiến trình chạy 10.000 vòng | NOT TESTED | s31-smoke |
| T11 | Uptime tăng, không panic/reset trong 60 giây | NOT TESTED | Chờ test |
| T12 | Reboot/reset lặp lại | NOT TESTED | Chờ test |
| T13 | Cold boot sau ngắt/cấp nguồn | NOT TESTED | Cần thao tác vật lý |
| T14 | Ethernet link, DHCP, ping | NOT TESTED | Cần cáp mạng/mạng thử |
| T15 | USB host chức năng | NOT TESTED | Cần thiết bị USB |
| T16 | GPIO/I2C/audio/Wi-Fi/BT chức năng | NOT TESTED | Ngoài smoke test, cần bài riêng |

Không dùng trạng thái PASS của T01 để suy ra PASS Linux; không coi việc flash thành công là boot thành công.
