# Danh mục lỗi và giới hạn

Phạm vi: cấu hình được khóa trong repo, board Function CoreBoard-1. Không có cơ sở khẳng định mọi lỗi liệt kê sẽ xuất hiện trên mọi board. `Đã gặp` là bằng chứng của phiên này; `tất định theo cấu hình` là hành vi của cấu hình cụ thể; `có điều kiện` chưa phải lỗi đã tái hiện.

## Đã gặp trên máy build/chuẩn bị

| ID | Triệu chứng | Nguyên nhân / bằng chứng | Xử lý và trạng thái |
|---|---|---|---|
| H01 | C chỉ còn 4.44 GB | Windows Get-PSDrive; không đồng nhất với con số free bên trong WSL VHDX | Người dùng chọn GitHub Actions; chưa làm đầy đĩa và chưa gặp ENOSPC |
| H02 | `sudo: a password is required` | `sudo -n true` trong WSL Ubuntu-24.04 | Dùng runner Ubuntu cho build; không thay sudo local |
| H03 | HTTP 429 khi đọc raw GitHub | Hai URL raw config/DTS bị rate limit | Đọc cùng nguồn qua authenticated Contents API thành công |
| H04 | `UnicodeEncodeError ... cp1252` | Python Windows in nội dung HTML Unicode | Dùng PYTHONUTF8=1 / ghi log UTF-8 |

## Hành vi tất định với cấu hình đã chọn

| ID | Điều kiện chính xác | Kết quả dự kiến | Cách xử lý / xác nhận |
|---|---|---|---|
| C01 | root được mount cramfs `ro` đúng bootargs | Ghi tệp mới vào `/` bị từ chối `Read-only file system` | Dùng `/tmp` tmpfs; cần rebuild image để đổi rootfs |
| C02 | Dữ liệu chỉ lưu trong `/tmp`/`/run` tmpfs | Dữ liệu mất sau reboot/mất nguồn | Không gọi đây là lỗi mất flash; persistent storage cần thiết kế riêng |
| C03 | Shell/getty cấu hình `ttyS0` | Shell Linux ở UART0, không tự chuyển sang COM USB Serial/JTAG | Dùng cổng UART; xác nhận port và baud 115200 |
| C04 | Rootfs cramfs lớn hơn 4 MiB | Hook `rootfs-cramfs.sh` báo vượt slot và dừng | Giảm package hoặc thay layout đồng bộ, không cắt binary |
| C05 | Chỉ dùng device tree minimal đang khóa | Chỉ một CPU node được mô tả; không chứng minh dùng cả hai core vật lý | Kiểm tra `/proc/cpuinfo`, không quảng cáo dual-core Linux từ spec phần cứng |
| C06 | Kernel config không bật IPv6 | Không có IPv6 trong image này | Dùng IPv4 hoặc đổi config/build lại nếu cần |
| C07 | Tệp `/` read-only và minimal rootfs | Không phải Ubuntu desktop; không mặc nhiên có apt/systemd/SSH/Wi-Fi tools | Kiểm kê BusyBox và gói đã build trước khi thử |

## Lỗi có điều kiện cần nhận diện

| ID | Điều kiện / triệu chứng | Chẩn đoán và khắc phục |
|---|---|---|
| R01 | Cáp chỉ sạc, driver CP210x thiếu, nhầm cổng | Không có COM; xem Device Manager/hardware ID, dùng cáp data/cổng UART |
| R02 | Serial monitor khác đang mở | esptool `Access denied`/port busy; đóng chương trình đang giữ COM |
| R03 | Auto-reset/download không hoạt động | esptool không sync; giữ BOOT, nhấn RESET, thả BOOT |
| R04 | UART baud cao/cáp/hub không ổn định | Packet timeout, checksum mismatch; giảm baud 460800 hoặc 115200, thử cáp/cổng trực tiếp |
| R05 | Nạp offset hoặc flash header sai | ROM/SPL boot loop; đối chiếu layout BSP và log. BSP quy định DIO/80m, không dùng mặc định QIO/40m cho SPL này |
| R06 | PSRAM thiếu/khác revision hoặc init/cache lỗi | Dừng trước kernel, trap/panic; lưu boot log, xác minh module 16 MiB PSRAM và commit hỗ trợ |
| R07 | FIT/DTB/kernel/rootfs lệch phiên bản/layout | Bad magic, không mount root, panic; build đồng bộ một source lock và SHA image |
| R08 | Tải nguồn/toolchain gặp 404/429/TLS/timeout | Build dừng trước compile; giữ URL/log, retry có giới hạn, sửa URL chỉ với nguồn xác minh |
| R09 | Hết disk hoặc RAM của host | ENOSPC hoặc compiler bị killed; kiểm tra filesystem thật và giảm JOBS |
| R10 | Buildroot trên NTFS/Windows PATH có khoảng trắng | Sai symlink/permission/PATH; dùng filesystem Linux, PATH Linux sạch như script |
| R11 | Dùng bare-metal toolchain hoặc sai ABI | Không build/link userspace musl đúng; dùng toolchain trong defconfig |
| R12 | Thiếu host dependencies hay Python package tương thích | Xem lỗi đầu tiên, thêm đúng dependency vào workflow và ghi lại thay đổi |
| R13 | Userspace chiếm hết RAM 16 MiB | OOM kill/hang; kiểm tra MemAvailable, giảm test/gói, không chủ động ép OOM trong smoke test |
| R14 | Mất nguồn/reset khi ghi flash | Image dở dang; ROM download và nạp lại image hoặc backup đã xác minh |
| R15 | Ethernet không cắm/link down/DHCP vắng | Không có IP/ping; phân biệt PHY/link, DHCP và gateway trước khi gọi lỗi driver |
| R16 | USB host thiếu nguồn/driver/class support | Device không enumerate hoặc không có chức năng; kiểm tra dmesg, nguồn và config |
| R17 | Wi-Fi/BT/audio có phần cứng nhưng thiếu driver/firmware/package | Không có tính năng trên Linux dù ESP-IDF dùng được; ghi NOT TESTED/unsupported trong cấu hình, không đánh đồng phần cứng hỏng |
| R18 | Reset làm COM đổi số | Mất kết nối terminal; quét cổng lại và đối chiếu USB identity |
| R19 | Secure boot/flash encryption bật trên board khác | Firmware không ký/không mã hóa có thể không boot/nạp được; đọc trạng thái, không thay eFuse để vượt qua |
| R20 | Bản preview thay đổi upstream | Build trước thành công nhưng build mới hỏng khi dùng branch động; dùng commit lock và lưu config/log |

Nguồn kiểm chứng chính: [BSP layout](https://github.com/espressif/esp-linux-bsp/blob/22455bf67ccc1aace91a547557af43fd85192281/configs/esp32s31-layout.cfg), [rootfs hook](https://github.com/espressif/esp-buildroot-external/blob/fb8dca11dbf213db1648c25145c28673937f576c/board/espressif/esp32s31/rootfs-cramfs.sh), [kernel config](https://github.com/espressif/linux/blob/dc0e3821e39bd7c169cefd274691e1998a844028/arch/riscv/configs/esp32s31_minimal_defconfig), [DTS](https://github.com/espressif/linux/blob/dc0e3821e39bd7c169cefd274691e1998a844028/arch/riscv/boot/dts/espressif/esp32s31.dts).
