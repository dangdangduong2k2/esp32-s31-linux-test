# Điều khiển RGB bằng Linux trên S31

Đã phát tín hiệu bằng chương trình C chạy trên Linux `6.18.0-g888671b7ed45` ngày 12/10/2026. Người dùng xác nhận **LED đỏ**. Không thay kernel hoặc nạp lại firmware. Các màu khác đã gửi thành công qua SPI, chưa có xác nhận riêng bằng mắt.

## Dùng trên board đã cài

Mở console UART của board, nhấn Enter để có dấu nhắc `~ #`, rồi gõ từng lệnh:

```sh
rgb-led red
rgb-led green
rgb-led blue
rgb-led white
rgb-led off
rgb-led 64 0 0
```

Ba số là **R G B**, mỗi số 0–255. Màu đặt tên dùng độ sáng vừa phải: đỏ/xanh lá/xanh dương 64; trắng 32 mỗi kênh. Lệnh kết thúc ngay; LED giữ màu cho đến lệnh tiếp theo hoặc mất nguồn.

Trên máy Windows của phiên này, `Win + R` → `D:\Codex\open-s31-console.cmd`. Console dùng COM56, 115200 8N1. Chỉ một chương trình được giữ COM56; `Ctrl + ]` thoát console. Các lệnh `rgb-led` chạy ở shell Linux của board, không phải dấu nhắc PowerShell Windows.

Tệp chương trình và overlay nằm trên root OverlayFS và đã `sync`. Overlay LED chỉ áp dụng cho phiên boot hiện tại; wrapper tự áp dụng lại khi gọi `rgb-led` sau boot. Chưa reboot kiểm tra riêng việc lưu các tệp LED hoặc Wi-Fi reconnect; không tự bật LED lúc boot.

## Cách hoạt động

- WS2812 onboard nhận dữ liệu tại GPIO60, thứ tự byte GRB.
- Kernel đang chạy có driver GPSPI2 và cơ chế dynamic device-tree overlay; không có driver RMT sẵn cho bài này.
- Overlay `rgb-led` chỉ định tuyến **MOSI GPSPI2 → GPIO60**. Không định tuyến SCLK, MISO hoặc chip select ra chân vật lý. Resource claim giữ GPSPI2; không dùng nó đồng thời cho thiết bị SPI khác.
- Mỗi bit WS2812 được mã hóa thành bốn bit SPI: `0 → 1000`, `1 → 1110`, yêu cầu tốc độ 3,2 MHz, MSB trước. 24 bit màu thành 12 byte, thêm 4 byte zero thành một transfer 16 byte, nhỏ hơn FIFO 64 byte của driver. Không chia khung màu thành các transfer rời.
- Trước khung, gửi zero rồi chờ 20 ms; sau khung cũng chờ 20 ms. Driver đặt mức dữ liệu idle thấp. Linux chỉ điều phối transfer/chờ; phần cứng SPI tạo xung trong khung màu.
- Tốc độ là yêu cầu gửi xuống driver; chưa đo dạng sóng hoặc tốc độ thực bằng oscilloscope. Kết quả mắt thường xác nhận màu đỏ hoạt động trên board này, không chứng nhận timing cho mọi biến thể WS2812 hay chuỗi nhiều LED.

`led/rgb-led.c` là userspace Linux RV32 dùng syscall trực tiếp, không có libc hoặc ESP-IDF runtime. Dùng compiler ESP bare-metal chỉ để sinh mã máy/ELF `rv32imac/ilp32`; startup và syscall Linux được viết rõ trong source. Cách này không thay thế Linux/musl toolchain cho ứng dụng có libc hoặc build kernel.

## Build và cài lại

Toàn bộ output ở ổ D. Ví dụ PowerShell tại thư mục repo:

```powershell
$py = 'D:\Codex\Projects\2026-10-12\https-esp32-s31-espressif-com-en\work\idf-python\Scripts\python.exe'
$cc = 'C:\Espressif\tools\riscv32-esp-elf\esp-16.1.0_20260609\riscv32-esp-elf\bin\riscv32-esp-elf-gcc.exe'
.\led\build.ps1 -Compiler $cc -Python $py
& $py led/make-install.py --build-dir .work/led --output .work/led/install.sh
# Thoát console bằng Ctrl + ] trước khi uploader mở COM56.
& $py scripts/serial-run.py --port COM56 --script .work/led/install.sh --output .work/led/install.log --seconds 60
```

Compiler ở C là công cụ có sẵn được đọc/chạy; build, temp và nguồn mới nằm ở D. `build-overlay.py` tuần tự hóa một cây cố định thành FDT v17 và xuất DTS đọc được; đây không phải compiler DTS tổng quát. DTS được lưu tại [led/rgb-led.dtso](../led/rgb-led.dtso). Installer kiểm SHA-256 các tệp đã chuyển qua UART trước khi cài:

| Tệp trên board | Vai trò |
|---|---|
| `/usr/bin/rgb-led` | Shell wrapper kiểm kernel, áp dụng overlay rồi chạy chương trình |
| `/usr/libexec/s31-rgb-led` | ELF Linux RV32, khoảng 3,3 KB |
| `/usr/lib/s31-overlays/esp32s31-overlay-rgb-led.dtbo` | GPSPI2 + một tuyến GPIO60 |

`compatible = "rohm,dh2228fv"` kế thừa cách binding spidev trong overlay GPSPI2 của image cộng đồng; không mô tả một chip ROHM thật trên board. Cấu hình này dành cho đúng bản thử nghiệm được khóa commit.

## Kiểm tra đã chạy

[Log đầu tiên](../evidence/linux-led-first-test.log), [cài đặt](../evidence/linux-led-install.log), [kiểm tra](../evidence/linux-led-check.log), [xác nhận người dùng](../evidence/linux-led-visual.json).

- ELF thực thi trên Linux; self-test giải mã lại 256 bộ giá trị GRB, kiểm phần đuôi thấp và giới hạn tham số: PASS.
- Tham số âm, vượt 255, tên lạ, thừa tham số: trả exit code 2.
- Gửi off/green/blue/white/red và RGB tùy chỉnh: tất cả thành công ở mức SPI.
- Remove overlay rồi gọi wrapper tự apply lại: PASS; thiết bị spidev biến mất/được tạo lại.
- Resource mask `1000000000000000` chỉ chiếm GPIO60. `gpioinfo` vẫn hiển thị `input consumer="kernel"`; thông tin hướng GPIO không phản ánh đầy đủ đường xuất peripheral qua matrix, không dùng dòng đó để phủ nhận LED đã sáng.
- Sau apply lại, SPI thống kê 0 errors, 0 timedout, 2 transfers (counters mới sau tạo lại controller, không phải tổng toàn bộ bài test). Wi-Fi carrier = 1 và overlay radio-wifi vẫn active/persisted.
- Người dùng nhìn và xác nhận **đỏ**; không có camera/oscilloscope tự động xác minh màu.

## Lỗi chắc chắn theo cấu hình và lỗi có điều kiện

| Điều kiện | Kết quả / xử lý |
|---|---|
| Gõ lệnh ở PowerShell Windows | Windows không tìm thấy lệnh; vào UART root shell trước |
| Kernel khác bản đã kiểm tra | Wrapper chủ động dừng; phải kiểm driver/binding trước khi mở rộng hỗ trợ |
| Giá trị ngoài 0–255 / sai cú pháp | Chương trình trả 2 và không gửi màu |
| Chưa apply overlay khi chạy ELF trực tiếp | Không mở được `/dev/spidev2.0`; dùng wrapper `rgb-led` |
| GPSPI2 hoặc GPIO60 đang bị overlay khác giữ | Apply có thể bị từ chối do xung đột; xem `s31-overlay status`, không tháo radio-wifi |
| Thiếu driver/overlay symbols hoặc node SPI không probe được | Không có spidev hoặc ioctl lỗi; xem dmesg, đối chiếu đúng kernel/image |
| Không có quyền root | Không mở được node spidev đang có mode 0600 |
| Mất điện/reset trong lúc cài vào OverlayFS | Có thể thiếu tệp; chạy installer lại sau boot ổn định |
| SPI ioctl thành công nhưng LED không sáng/khác màu | Kiểm đúng model/GPIO60/GRB, power và timing thực; kết quả syscall không tự chứng minh màu |
| Đổi LED hoặc nối nhiều LED | Khung hiện tại chỉ dành cho một LED; không tự tăng chiều dài vượt FIFO mà chưa kiểm timing |
| Có hai ứng dụng cùng điều khiển GPSPI2 | Có thể xen các bước reset/frame và ghi đè màu; chỉ dùng một chương trình điều khiển tại một thời điểm |

Để tắt chỉ cần `rgb-led off`. Để gỡ cấu hình phiên hiện tại sau khi tắt: `s31-overlay remove rgb-led --volatile`. Không dùng `remove --all` vì sẽ ảnh hưởng Wi-Fi. Muốn gỡ cài đặt thì xóa đúng ba tệp nêu trên sau khi tắt/gỡ overlay.

## Nguồn đối chiếu

- [Espressif: Function CoreBoard-1, RGB GPIO60](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32s31/esp32-s31-function-coreboard-1/user_guide.html).
- [GPSPI driver tại kernel đã chạy](https://github.com/GrieferPig/linux-esp32-s31/blob/888671b7ed45e734f529cdd2f05fa873e250a522/drivers/spi/spi-esp32s31.c): FIFO, divider, idle data và transfer.
- [Pinmux binding](https://github.com/GrieferPig/linux-esp32-s31/blob/888671b7ed45e734f529cdd2f05fa873e250a522/include/dt-bindings/pinctrl/esp32s31-pinmux.h), [DTS cơ sở](https://github.com/GrieferPig/linux-esp32-s31/blob/888671b7ed45e734f529cdd2f05fa873e250a522/arch/riscv/boot/dts/espressif/esp32s31.dtsi), [overlay SPI gốc](https://github.com/GrieferPig/linux-esp32-s31/blob/888671b7ed45e734f529cdd2f05fa873e250a522/arch/riscv/boot/dts/espressif/esp32s31-overlay-gpspi2.dtso).
- [Linux SPI userspace ABI](https://github.com/GrieferPig/linux-esp32-s31/blob/888671b7ed45e734f529cdd2f05fa873e250a522/include/uapi/linux/spi/spidev.h).
