# Danh mục lỗi và giới hạn

Phạm vi: board Function CoreBoard-1, hai profile phải phân biệt: **community đã test** trong prebuilt.lock.json và **official minimal chưa build được** trong sources.lock.json. Không có cơ sở nói mọi lỗi xuất hiện trên mọi board. `Đã gặp` có log; `tất định` chỉ áp dụng khi đúng điều kiện; `có điều kiện` chưa phải lỗi tái hiện. Không cam kết danh sách bao quát mọi lỗi có thể tồn tại.

## Đã gặp khi chạy Linux — profile community

| ID | Quan sát / bằng chứng | Đánh giá và xử lý |
|---|---|---|
| L01 | `Failed to add a System RAM resource at 50000000` trong boot/dmesg | Cảnh báo khởi tạo resource có lặp; Linux vẫn có MemTotal 15640 kB và shell. Chưa điều tra/sửa nguyên nhân, không gọi RAM hỏng hoặc đã sửa |
| L02 | `regulatory.db ... error -2` | Không tải được regulatory database; chưa kiểm thử Wi-Fi, không quy thành Wi-Fi đã PASS. Cần database/driver/config phù hợp trước test radio |
| L03 | USB `vusb_d/vusb_a ... dummy regulator` | DT/driver dùng regulator thay thế; root hub vẫn được tạo. Chưa xác minh điện áp cấp USB hay thiết bị ngoài |
| L04 | `No soundcards found`, không có `/dev/i2c*` | Kernel có subsystem không có nghĩa đã tạo thiết bị cụ thể. Chưa kiểm tra chức năng audio/I2C |
| L05 | `check access for rdinit=/init failed: -2, ignoring` rồi `Run /init as init process` | Boot tiếp tục với root filesystem và init thật; không phải kernel panic thiếu init trong lần này |
| L06 | OverlayFS upper không hỗ trợ tmpfile/RENAME_WHITEOUT | Cảnh báo giới hạn upper filesystem. Tạo/xóa marker và lưu qua reboot đạt; chưa kiểm thử mọi thao tác rename/copy-up/whiteout |
| L07 | `This architecture does not have kernel memory protection` | Giữ đúng thông báo kernel; chưa xác minh cơ chế bảo vệ kernel. Không suy ra không có MMU: cpuinfo xác nhận sv32 |
| L08 | Shutdown báo crond/syslog/klog `FAIL`, `lo not configured`, tmpfs không remount được | Xảy ra khi script reboot lại ngay sau login; rcS đang chạy nền, có lúc ở S01s31-swap. Ở uptime 33.66s rcS.status=0 và các dịch vụ OK. Chờ rcS.done để test dịch vụ; reboot vẫn về shell |
| L09 | `Starting USB swap: no /dev/sd* device found`; SwapTotal=0 | Không có USB storage trong bài này, không tạo swap. Không lỗi boot; RAM vẫn hữu hạn |
| L10 | Chỉ có interface lo | rcS ghi `Wi-Fi disabled`. Chưa cấu hình/test mạng ngoài; không gọi là lỗi driver Ethernet/Wi-Fi |
| L11 | Một vài byte hỏng lúc reset | Host cp1252 lỗi khi in ký tự replacement làm dừng capture lần đầu. Sửa stdout UTF-8 trong cả 3 script; log binary giữ nguyên byte nhận; board vẫn reboot thành công |

Bằng chứng: [smoke](../evidence/linux-smoke.log), [software reboot](../evidence/software-reboot.log), [dịch vụ sớm](../evidence/services-after-reboot.log), [dịch vụ hoàn tất](../evidence/services-settled.log). Các cảnh báo còn xuất hiện không được đánh dấu đã khắc phục.

## Hành vi có điều kiện xác định — profile community

| Điều kiện | Hệ quả |
|---|---|
| Root mount OverlayFS rw với upper JFFS2 | Root có thể ghi/lưu qua reboot; không áp dụng kỳ vọng cramfs chỉ đọc của profile official |
| Tệp nằm trong /tmp tmpfs | Mất sau reboot/ngắt nguồn; đã xác nhận với marker |
| Chưa có /run/rcS.done | Có shell vẫn chưa đảm bảo dịch vụ nền hoàn tất; script init upstream chạy rcS ở nền |
| Không đổi mặc định login | UART cho root không cần mật khẩu; phải thiết kế xác thực trước khi đưa dịch vụ ra mạng |
| Vượt dung lượng partition persist 0x90000 byte, hoặc RAM khả dụng | Có thể gặp ENOSPC/OOM; chưa chủ động thử đến hỏng. Không nhầm 16 MiB flash với 16 MiB writable root |
| Dùng erase-flash/full image để update | Có thể mất persistent data; chỉ cài mới như đã làm sau backup. Update cần đúng các image thành phần/layout |
| Dùng offset tương đối MTD làm offset esptool | Nạp sai vị trí. Layout raw có FIT 0x100000, DTB 0x300000, kernel 0x500000, persist 0xB30000, rootfs 0xBD0000 |

## Đã gặp trên máy build/chuẩn bị

| ID | Triệu chứng | Nguyên nhân / bằng chứng | Xử lý và trạng thái |
|---|---|---|---|
| H01 | C chỉ còn 4.44 GB | Windows Get-PSDrive; không đồng nhất với con số free bên trong WSL VHDX | Người dùng chọn GitHub Actions; chưa làm đầy đĩa và chưa gặp ENOSPC |
| H02 | `sudo: a password is required` | `sudo -n true` trong WSL Ubuntu-24.04 | Dùng runner Ubuntu cho build; không thay sudo local |
| H03 | HTTP 429 khi đọc raw GitHub | Hai URL raw config/DTS bị rate limit | Đọc cùng nguồn qua authenticated Contents API thành công |
| H04 | `UnicodeEncodeError ... cp1252` | Python Windows in nội dung HTML Unicode | Dùng PYTHONUTF8=1 / ghi log UTF-8 |
| H05 | GitHub Actions không bắt đầu job | Account locked due to billing; annotation run 38204464647 | BLOCKED cho build nguồn; dùng community prebuilt có SHA riêng để test board |
| H06 | Capture reboot dừng do cp1252 | Ký tự lỗi UTF-8 khi reset không in được ra stdout cp1252 | Đặt stdout UTF-8 trong script; chạy lại 2 vòng reboot đầy đủ thành công |

## Hành vi tất định — chỉ profile official minimal CHƯA TEST

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
