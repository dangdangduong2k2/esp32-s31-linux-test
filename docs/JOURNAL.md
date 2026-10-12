# Nhật ký thực hiện — 12/10/2026 (Asia/Ho_Chi_Minh)

Các mục dưới đây ghi theo thứ tự thực hiện. Lệnh chuẩn để tái lập ở PROCEDURE; log máy ở evidence hoặc Actions artifact. Không coi các bước dự kiến là đã thực hiện.

1. Người dùng xác nhận bài LED đỏ chỉ nhằm kiểm tra board còn hoạt động và yêu cầu test Linux, ghi lại bước/lỗi để đưa lên GitHub.
2. Đọc hướng dẫn chính thức `espressif/esp-buildroot-external`: Buildroot 2025.02; S31 NOR; Developer Preview; console 115200; boot SPL/OpenSBI/U-Boot/Linux.
3. Kiểm tra Windows: có Git, GitHub CLI và WSL2 Ubuntu-24.04. GitHub CLI xác nhận tài khoản `dangdangduong2k2`.
4. Kiểm tra dung lượng: C còn 4.44 GB, D còn 2.71 GB (giá trị thập phân tại thời điểm kiểm tra). WSL hiển thị 927 GiB khả dụng logic trong VHDX nhưng backing volume C không có dung lượng đó. Chưa chạy build Linux tại máy.
5. WSL: có gcc/make/git/python3 và các công cụ build thường dùng; `sudo -n true` thất bại vì cần mật khẩu. Không đổi mật khẩu/cấu hình sudo.
6. Clone external tree và BSP chính thức; ghi commit. Đọc layout NOR: SPL 0x2000, FIT 0x100000, DTB 0x300000, kernel 0x500000, rootfs 0xC00000.
7. Tải kernel config/DTS qua raw.githubusercontent.com bị HTTP 429. Dùng GitHub Contents API đã xác thực để đọc cùng file thành công. Không thay nguồn kernel.
8. Một lệnh in HTML bằng Python Windows vấp UnicodeEncodeError/cp1252; đặt PYTHONUTF8=1 khắc phục phần hiển thị.
9. Xác nhận config dùng `console=ttyS0` và cramfs `ro`; gửi hướng dẫn chuyển cáp sang UART.
10. Người dùng chọn build bằng GitHub Actions và repo public; chỉ có một cáp nên chuyển cáp từ USB Serial/JTAG sang UART.
11. Windows nhận CP210x `COM56`, trạng thái driver OK. COM55 biến mất đúng với việc rút cáp khỏi USB Serial/JTAG.
12. Chuẩn bị repository local, source lock, build workflow, script smoke, tài liệu lỗi và ma trận kiểm thử. Chưa nạp Linux tại mục này.
13. Tạo repo public dangdangduong2k2/esp32-s31-linux-test và chạy workflow. Run 38204464647 bị GitHub chặn trước job vì account billing lock; giữ annotation JSON. Không có Linux build từ nguồn thành công.
14. Tìm community release GrieferPig tag ci-d74660b8f90c-34182145900, source commit d74660b8f90c6fd0c16b54115320e748766c6df7. Tải s31_full_flash.bin 14,880,768 byte; SHA-256 f9a86a8e902257f7ef680a4555badc602d81da82fa02d6110711b46c6c1f7c2c. Đây là fallback khác profile chính thức.
15. Kiểm tra backup và trạng thái bảo mật chip, không thay eFuse. Erase toàn flash cho cài mới, nạp combined image offset 0 với DIO/80m/16MB, baud 460800. esptool xác minh hash, ghi mất 197.2s; log ở evidence/linux-erase.log và linux-flash.log.
16. Capture boot thấy SPL/U-Boot/Linux 6.18 và login. Người dùng yêu cầu chuyển mọi dữ liệu Codex sang D; tạm ngắt phần test để chuẩn bị migration. Migration chưa hoàn tất tại lúc tiếp tục; mọi dữ liệu S31 mới được lưu ở D, repo hoạt động tách khỏi bản stage để không bị sync migration ghi đè.
17. Tiếp tục COM56, đăng nhập root không password; kiểm kê uname/cpuinfo/meminfo/mount/MTD. Xác nhận sv32, 2 CPU, MemTotal 15640 kB, OverlayFS rw. Sửa tài liệu để không áp đặc điểm official cramfs lên community image.
18. Upload và chạy board-smoke.sh: 256 KiB zero-filled file copy/cmp/checksum đạt, root write probe tạo/xóa được, 2 worker 10.000 vòng đạt, loopback 3/3; quan sát 60.10 giây uptime không panic/reset. Kiểm kê chỉ có lo, USB root hub, gpiochip0; I2C node và soundcard vắng.
19. Tạo marker root persistent và /tmp volatile, sync. Reboot đầu host capture bị UnicodeEncodeError cp1252; board vẫn về shell, marker root còn và /tmp mất. Sửa stdout UTF-8 cả 3 script và giữ log lần lỗi.
20. Chạy lại 2 software reboot có log đầy đủ và 1 reset RTS: cả 3 lần shell hoạt động, CPU online 0-1, PASS_PERSIST. Một số shutdown dịch vụ FAIL khi reboot nhanh; đọc source inittab thấy rcS chạy nền. Đọc log ở uptime 33.66s có rcS.status=0, rcS.done, các dịch vụ OK; Wi-Fi disabled, không USB swap.
21. Sync rồi yêu cầu người dùng rút dây 5 giây và cắm lại UART; người dùng xác nhận đã làm. Đăng nhập lại được ở uptime 11.60s, marker root còn. Không capture được ROM/kernel sớm của lần cấp nguồn đó; ghi giới hạn bằng chứng trong RESULTS.
22. Đọc trạng thái cuối sau cold boot: uptime 392.84s, rcS.status=0, CPU online 0-1, MemAvailable 10356 kB, SwapTotal=0. Kiểm tra đúng nội dung marker trước khi xóa marker do bài test tạo; sync, để Linux và root shell chạy trên board.
23. Giữ nguyên các boot warning trong ERRORS; phân biệt lỗi đã gặp, giới hạn profile và rủi ro chỉ xảy ra theo điều kiện. Chưa test ngoại vi/mạng ngoài hoặc soak dài hạn. Chuẩn bị commit/push script, docs, log, checksum; không kèm firmware backup. MAC được che trong bản log public, log gốc giữ riêng.
24. Sau khi người dùng mở console và menu cấu hình, ảnh cho thấy mã ANSI in thẳng trong Windows PowerShell. Đối chiếu miniterm.py 3.5: điều kiện tự bật ANSI chỉ xét Windows 10; host thực tế Windows 11 (10.0.22631). Thêm scripts/console.py, kiểm tra console mode thành công bằng --check-console trong PTY, không mở COM56 đang dành cho người dùng. Thêm hướng dẫn Wi-Fi CLI dựa trên source; chưa đánh dấu kết nối Wi-Fi PASS.

## Tham chiếu bài kiểm tra LED trước Linux

- Chip ESP32-S31 revision v0.0, flash 16 MiB; nạp qua COM55 thành công.
- Sao lưu 16,777,216 byte trước khi nạp LED; SHA-256 `fd8b53fde3ba788ed8c4e6178f91a64a346a0072072400897dc2b4a704da47ee`.
- ESP-IDF có sẵn v6.0 chưa có target S31 trong checkout; tải bản master có S31 và bộ công cụ phù hợp.
- Đã gặp đường dẫn Git quá dài trong submodule mbedTLS; sửa bằng `git -c core.longpaths=true ... submodule update`.
- Build ban đầu chạy trước khi pip xong gây thiếu module; lần sau thiếu constraints v6.2 và ESP_IDF_VERSION, đã bổ sung.
- Trình biên dịch báo khởi tạo `{0}` cho struct rỗng của RMT; sửa `{}` đúng API.
- esptool xác nhận hash sau nạp; log RMT thành công và người dùng xác nhận board sống. Các lỗi này thuộc bài ESP-IDF trước đó, không quy thành lỗi Linux.
