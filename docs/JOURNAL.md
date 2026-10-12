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

## Tham chiếu bài kiểm tra LED trước Linux

- Chip ESP32-S31 revision v0.0, flash 16 MiB; nạp qua COM55 thành công.
- Sao lưu 16,777,216 byte trước khi nạp LED; SHA-256 `fd8b53fde3ba788ed8c4e6178f91a64a346a0072072400897dc2b4a704da47ee`.
- ESP-IDF có sẵn v6.0 chưa có target S31 trong checkout; tải bản master có S31 và bộ công cụ phù hợp.
- Đã gặp đường dẫn Git quá dài trong submodule mbedTLS; sửa bằng `git -c core.longpaths=true ... submodule update`.
- Build ban đầu chạy trước khi pip xong gây thiếu module; lần sau thiếu constraints v6.2 và ESP_IDF_VERSION, đã bổ sung.
- Trình biên dịch báo khởi tạo `{0}` cho struct rỗng của RMT; sửa `{}` đúng API.
- esptool xác nhận hash sau nạp; log RMT thành công và người dùng xác nhận board sống. Các lỗi này thuộc bài ESP-IDF trước đó, không quy thành lỗi Linux.
