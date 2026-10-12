# Dự kiến nối ST7701S 480×854 với header J2

**Trạng thái: đã lập và kiểm tra phân bổ GPIO; chưa cấu hình lên board, chưa nối/test màn hình.** Bảng này dùng ảnh pinout 40 chân và ảnh thông số do người dùng cung cấp: 5 inch IPS, 480×854, ST7701S/GT911, nguồn logic 3,3 V. Chưa biết mã module/FPC cụ thể.

## Phương án

Chọn **RGB565 native 16-bit của ST7701S**, gồm 16 dây dữ liệu + PCLK/HS/VS/DE + RST/SDA/SCL/CS = 24 GPIO. Header J2 có 29 GPIO; giữ GPIO58/59 cho UART, GPIO60 cho LED và GPIO61 cho BOOT thì còn 25 GPIO. Còn GPIO4 dự phòng. RGB888 với đầy đủ bốn tín hiệu đồng bộ và bốn tín hiệu điều khiển riêng cần 32 GPIO, không phù hợp với header này.

Nguồn pixel vẫn là LCD peripheral + DMA. SPI chỉ gửi lệnh cấu hình ST7701S. Không thể lấy chương trình SPI điều khiển một LED làm bộ phát RGB liên tục cho LCD.

**Điều kiện của bảng:** nhãn R0–R7 trên module tương ứng DB16–DB23, G0–G7 tương ứng DB8–DB15, B0–B7 tương ứng DB0–DB7 của ST7701S. Datasheet ST7701S v1.4, trang 73, Table 12 quy định native RGB565 sử dụng **R0–R4, G0–G5, B0–B4**. Không tự thay bằng R3–R7/G2–G7/B3–B7: cách đó là một phương án giảm màu trên bus RGB888, khác chế độ native 16-bit đang chọn. Nếu FPC/adapter của module đã đổi thứ tự đường tín hiệu, phải sửa bảng theo module.

## Bảng nối dự kiến

`Chân LCD` là số 1–40 theo ảnh màn hình; `Chân J2` là số vật lý header board; `GPIO` là số in tên tín hiệu. Hai đầu 40 chân không có cùng pinout, không cắm thẳng với nhau.

| Chân LCD | Tín hiệu LCD | GPIO S31 | Chân J2 | Tín hiệu host |
|---|---|---|---|---|
| 5 | R0 | 42 | 20 | LCD_DATA11 |
| 6 | R1 | 46 | 16 | LCD_DATA12 |
| 7 | R2 | 47 | 13 | LCD_DATA13 |
| 8 | R3 | 48 | 14 | LCD_DATA14 |
| 9 | R4 | 49 | 11 | LCD_DATA15 |
| 13 | G0 | 25 | 31 | LCD_DATA5 |
| 14 | G1 | 35 | 25 | LCD_DATA6 |
| 15 | G2 | 36 | 24 | LCD_DATA7 |
| 16 | G3 | 37 | 23 | LCD_DATA8 |
| 17 | G4 | 38 | 22 | LCD_DATA9 |
| 18 | G5 | 39 | 21 | LCD_DATA10 |
| 21 | B0 | 20 | 26 | LCD_DATA0 |
| 22 | B1 | 21 | 27 | LCD_DATA1 |
| 23 | B2 | 22 | 28 | LCD_DATA2 |
| 24 | B3 | 23 | 29 | LCD_DATA3 |
| 25 | B4 | 24 | 30 | LCD_DATA4 |
| 30 | PCLK | 40 | 19 | PCLK |
| 32 | HS | 44 | 18 | HS |
| 33 | VS | 45 | 15 | VS |
| 34 | DE | 43 | 17 | DE |
| 37 | RST | 0 | 9 | RST |
| 38 | SDA_SPI | 1 | 12 | SDA_SPI |
| 39 | SCL_SPI | 2 | 7 | SCL_SPI |
| 40 | CS | 3 | 10 | CS |

PCLK/HS/VS/DE chọn các GPIO tương ứng chức năng LCD native. Dữ liệu đi qua GPIO matrix vì nhiều chân LCD native không được đưa ra J2; việc chọn bốn chân sync native không có nghĩa toàn bus bypass matrix. Sơ đồ board cho thấy các GPIO đã chọn đi ra J2; Ethernet dùng phần lớn GPIO5–19, audio dùng GPIO50–57, UART58/59, LED60. GPIO20–25 không thể dùng đồng thời cho SDMMC trong phương án này.

| Chân LCD còn lại | Cách xử lý |
|---|---|
| 3, 29, 36 — GND | Nối GND chung, ví dụ J2-1/2/8/33/34/37/38 |
| 4 — VCC | Logic 3,3 V, dự kiến J2-35 hoặc J2-36; kiểm dòng tải của module trước khi cấp |
| 10–12 — R5–R7; 19–20 — G6–G7; 26–28 — B5–B7 | Không dùng trong native RGB565; giữ mức GND sau khi xác minh mapping/mode của module |
| 31, 35 — NC | Không nối |
| 1 — LEDK, 2 — LEDA | Chờ thông số backlight. Dùng mạch cấp dòng phù hợp; không nối trực tiếp vào GPIO và không suy ra điện áp đèn nền từ VCC logic 3,3 V |

Màn hình chưa được cấp điện/nối dây trong bài kiểm tra này. Cần xác định chiều đếm FPC từ dấu pin 1 của module/adapter; không suy ra chiều nhìn chỉ từ bảng số chân.

## Phần Linux còn thiếu

Kiểm đúng source kernel `888671b7ed45e734f529cdd2f05fa873e250a522`: DTS S31 chưa có node LCD; cây DRM và fbdev không có driver bộ phát LCD dành cho S31. Có driver panel `panel-sitronix-st7701.c` chung, với hỗ trợ SPI/DPI theo model panel, nhưng driver panel không thay thế driver bộ phát pixel LCD/DMA của SoC. Defconfig đang kiểm tra không bật cấu hình DRM/LCD cần thiết. Chưa đọc lại config runtime trên board trong lượt này.

Do đó đây là **pin plan**, không phải device-tree overlay có thể apply rồi hiện ảnh. Cần bổ sung/tích hợp driver LCD S31, framebuffer/DMA, clock/pinctrl, panel init và timing phù hợp. ESP-IDF có driver RGB S31 để tham khảo, nhưng thư viện ESP-IDF không chạy trực tiếp như một driver Linux.

Đã lưu các giá trị xác định tại [pinplan JSON](../display/st7701s-480x854.pinplan.json); thông số chưa biết để `null`, không điền timing hay gamma từ một panel ST7701S khác. Một framebuffer RGB565 là 480 × 854 × 2 = 819840 byte; chưa kiểm tra khả năng cấp DMA/băng thông trên kernel này.

## Những thông số chưa suy ra từ tên IC

- PCLK, porch/pulse và cực tính đồng bộ của module.
- Chuỗi khởi tạo analog/GIP/gamma riêng của panel; 480×854 không xác định các giá trị này.
- Cách module strap SPI 8/9/16-bit và cạnh clock. Ảnh chỉ có SDA/SCL/CS, chưa có cấu hình strap.
- Dòng và điện áp LEDA/LEDK, module đã có driver backlight hay chỉ có chuỗi LED.
- Đầu nối cảm ứng GT911 và pinout riêng. SDA/SCL ở LCD-38/39 được ảnh ghi rõ là **SPI của LCD**, không dùng như I²C của GT911. Bảng này chỉ phân bổ phần hiển thị; cảm ứng chưa được gán chân.

## Lỗi và giới hạn cần kiểm tra

| Điều kiện | Hệ quả / xử lý |
|---|---|
| Chỉ apply pinctrl nhưng không có LCD engine driver | Không có luồng pixel; màn chưa thể hiển thị |
| Sai mode RGB565/RGB888 hoặc mapping bit | Sai màu, mất kênh màu hoặc không có ảnh |
| Timing/init lấy từ module khác cùng ST7701S | Có thể trắng/đen, lệch ảnh, không ổn định; không coi controller trùng tên là đủ |
| SPI framing/cạnh clock sai | Lệnh khởi tạo có thể không được nhận |
| Header đang dùng cho SDMMC hoặc ngoại vi khác | Tranh chấp GPIO; phải đối chiếu overlay đang active trước khi apply |
| Cắm LCD 40-pin trực tiếp vào J2 40-pin | Pinout khác nhau, có thể nối nguồn vào tín hiệu; phải dùng dây/adapter đúng mapping |
| Cấp sai nguồn/dòng backlight | Có thể không sáng hoặc hỏng đèn/mạch; xác minh nguồn backlight riêng |
| Dây RGB dài, tiếp xúc kém hoặc PCLK quá cao | Có thể nhiễu ảnh; cần kiểm tín hiệu, dây ngắn và GND chung |
| Thiếu DMA buffer/băng thông RAM | Không khởi tạo được framebuffer hoặc mất ổn định hiển thị; chưa test |

Không thay kernel, không đổi overlay đang active và không chiếm cổng UART trong lượt lập bảng này.

## Nguồn

- [Espressif: header J2 và schematic Function CoreBoard-1](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32s31/esp32-s31-function-coreboard-1/user_guide.html#header-block).
- [Schematic chính thức, sheet 2](https://dl.espressif.com/schematics/esp32-s31-function-coreboard-1-schematics.pdf).
- [ST7701S v1.4, trang 38 và 72–75, do Espressif cung cấp](https://dl.espressif.com/AE/esp-iot-solution/ST7701S_SPEC_%20V1.4.pdf).
- [ESP-IDF: LCD RGB của S31](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s31/api-reference/peripherals/lcd/rgb_lcd.html).
- [Driver panel ST7701 tại kernel đang dùng](https://github.com/GrieferPig/linux-esp32-s31/blob/888671b7ed45e734f529cdd2f05fa873e250a522/drivers/gpu/drm/panel/panel-sitronix-st7701.c).
