# ESP32-S31 Function CoreBoard: Linux bring-up

Thử nghiệm trên board thật, có lệnh tái lập, nguồn được khóa commit và log kết quả. Tài liệu tiếng Việt.

**Trạng thái hiện tại: đang chuẩn bị build; chưa xác nhận Linux khởi động trên board này.**

Board: ESP32-S31-Function-CoreBoard-1, chip revision v0.0, NOR flash 16 MiB. LED đỏ đã chạy bằng ESP-IDF, xác nhận kết nối nạp trước bài test Linux. Cấu hình Linux chính thức khai báo 16 MiB PSRAM; dung lượng khả dụng phải kiểm chứng qua boot log và `/proc/meminfo`.

- [Quy trình](docs/PROCEDURE.md): chuẩn bị, build, nạp, test và phục hồi.
- [Nhật ký](docs/JOURNAL.md): những việc thực sự đã làm.
- [Lỗi và điều kiện](docs/ERRORS.md): lỗi đã gặp, hành vi tất định theo cấu hình và rủi ro có điều kiện.
- [Ma trận kết quả](docs/RESULTS.md): PASS / FAIL / BLOCKED / NOT TESTED.
- [Nguồn khóa phiên bản](sources.lock.json).

## Build

Chạy workflow **Build ESP32-S31 Linux** trong tab Actions. Workflow chạy trên Ubuntu 24.04, lấy Buildroot 2025.02 và các commit Espressif được khóa, tạo `s31_full_flash.bin` cùng SHA-256, config và log trong artifact. Build thành công chưa chứng minh board chạy Linux.

Trên Linux/WSL có đủ dung lượng, cài các gói trong workflow rồi chạy:

```sh
bash scripts/build.sh
```

Chỉ build trên filesystem Linux. Không dùng GCC bare-metal của ESP-IDF để thay toolchain Linux musl. Script build không tự nạp board.

## Phạm vi

Ưu tiên boot đến shell, nhận diện CPU/RAM/flash, tác vụ userspace, tệp tạm, tính chỉ đọc của rootfs, log lỗi và reboot. Ethernet/USB cần thiết bị/cáp tương ứng. Wi-Fi, Bluetooth, audio và mọi GPIO không tự động được xem là đã hỗ trợ chỉ vì board có phần cứng.

Đây là bản Developer Preview của Espressif. Không thể liệt kê mọi lỗi có thể tồn tại; danh mục trong repo bao gồm bằng chứng thực nghiệm và các điều kiện liên quan đến cấu hình đã chọn, không khẳng định lỗi chưa tái hiện là lỗi chắc chắn.

## Nguồn chính

- https://github.com/espressif/esp-buildroot-external
- https://github.com/espressif/esp-linux-bsp
- https://github.com/espressif/linux/tree/integration/v6.18-esp32s31
- https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32s31/esp32-s31-function-coreboard-1/user_guide.html

Các bản sao config/DTS trong `configs/` giữ thông báo bản quyền của upstream; mã nguồn hệ thống được tải trực tiếp từ upstream, không nhập toàn bộ vào repo này. Firmware sao lưu riêng của board không được đưa lên repo public.
