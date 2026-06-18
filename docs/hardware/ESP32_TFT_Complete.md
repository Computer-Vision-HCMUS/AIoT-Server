# ESP32-S3 & TFT LCD — Tài liệu đầy đủ

---

## ESP32-S3

### Chức năng & Vai trò

ESP32-S3 là **"não"** của toàn hệ thống — đọc sensor, xử lý logic, điều phối mọi ngoại vi, kết nối mạng.

```
INMP441  ──I2S──►┐
BH1750   ──I2C──►│
DS3231   ──I2C──►├── ESP32-S3 ──SPI──► TFT (hiển thị)
MicroSD  ──SPI──►│              ──I2S──► MAX98357A (phát nhạc)
Buttons  ──GPIO─►│              ──WiFi──► Firebase
                 └── xử lý logic, state machine, AI inference
```

### Hoạt động thế nào

Chip 2 nhân chạy song song:
- **Core 0** — WiFi stack, Firebase sync (Espressif tự quản lý)
- **Core 1** — code của bạn: đọc sensor, render TFT, xử lý nút

Có thêm **AI accelerator** (vector SIMD 128-bit) giúp chạy mô hình TFLite trực tiếp trên chip. **8 MB PSRAM** cho phép load model lớn hơn, tạo sprite toàn màn hình, buffer audio.

### Thông số chip

| | |
|---|---|
| CPU | Xtensa LX7 dual-core 240 MHz |
| AI Accelerator | Vector SIMD 128-bit — nhân ma trận CNN nhanh ~5× so với ESP32 thường |
| SRAM | 512 KB internal |
| PSRAM (N8R8) | 8 MB |
| Flash (N8R8) | 8 MB |
| WiFi | 2.4 GHz 802.11 b/g/n |
| Bluetooth | BLE 5.0 |
| USB | USB 2.0 OTG |

### Peripheral

| Peripheral | Số lượng | Dùng cho |
|---|---|---|
| SPI | 4 bus | TFT + MicroSD (share bus, CS riêng) |
| I2S | 2 port | Port 0: INMP441 thu âm · Port 1: MAX98357A phát nhạc |
| I2C | 2 bus | BH1750 + DS3231 (chung 1 bus, địa chỉ khác nhau) |
| LEDC PWM | 8 channel | Buzzer, backlight dimming |
| ADC | 20 kênh 12-bit | **ADC2 không dùng được khi WiFi active** — dùng ADC1 (GPIO 1–10) |
| GPIO | 45 pin | Nút nhấn (INPUT_PULLUP), buzzer, LED |

### Tiêu thụ điện

| Mode | Dòng |
|---|---|
| Active (WiFi + CPU 240 MHz) | ~150–240 mA |
| Modem sleep | ~15–30 mA |
| Light sleep | ~2–5 mA |
| Deep sleep | ~10–50 µA |

TFT backlight (~60 mA) + ESP32-S3 (~200 mA) + MAX98357A peak (~200 mA) → dùng nguồn USB 5V/1A là đủ.

### Tại sao không dùng ESP8266

| | ESP8266 | ESP32-S3 |
|---|---|---|
| I2S hardware | ❌ Không có | ✅ 2 port hardware |
| RAM | ~40–50 KB khả dụng | 512 KB + 8 MB PSRAM |
| AI accelerator | ❌ | ✅ SIMD 128-bit |
| Core | 1 core | 2 core |
| ADC khi WiFi | ❌ Không dùng được | ✅ ADC1 hoạt động bình thường |

### Vai trò trong SmartDesk Buddy

| Tính năng | ESP32-S3 làm gì |
|---|---|
| HOME | Đọc INMP441 (I2S) + BH1750 (I2C) → tính dB/lux → render TFT |
| STUDY Pomodoro | Đếm millis(), quản lý session state, beep buzzer (LEDC PWM) |
| STUDY Seminar | Thu âm INMP441 → buffer → HTTP POST lên AI server |
| SLEEP | Đọc DS3231 alarm interrupt → kích hoạt buzzer wakeup |
| RELAX Music | Decode MP3 từ SD (SPI) → stream I2S → MAX98357A |
| RELAX Game | Game loop + collision logic + render TFT qua Sprite |
| Sync | WiFi → Firebase RTDB mỗi 30s |

### Dùng trong code

```cpp
// Cách đơn giản — millis() thay FreeRTOS
void loop() {
  wifi.maintain();              // reconnect nếu mất
  fsm.update();                 // đọc nút, chuyển state, render TFT
  collector.update(30000);      // đọc sensor → JSON → Firebase mỗi 30s
  alertMgr.check(...);          // kiểm tra ngưỡng → buzzer/Firebase
}
```

```cpp
// Cách nâng cao — FreeRTOS dual-core
void firebaseTask(void* pvParams) {
  while (true) {
    Firebase.RTDB.setFloat(&fbdo, "/sound_db", currentDB);
    vTaskDelay(pdMS_TO_TICKS(5000));
  }
}

void setup() {
  // Firebase chạy Core 0, loop() chạy Core 1 — không block nhau
  xTaskCreatePinnedToCore(firebaseTask, "Firebase", 4096, NULL, 1, NULL, 0);
}
```

---

## TFT LCD 2.4" (ILI9341)

### Chức năng & Vai trò

TFT là **"mặt"** của hệ thống — giao diện duy nhất người dùng nhìn vào. Chỉ render những gì ESP32-S3 chỉ định, không tự làm gì.

| State | TFT hiển thị |
|---|---|
| HOME | Sound level (dB) + quality · Light level (lux) + quality — cập nhật 2 Hz |
| STUDY Pomodoro | Đồng hồ đếm ngược font lớn + progress bar session |
| STUDY Seminar | Trạng thái recording → "Processing..." → kết quả điểm AI |
| SLEEP | Realtime noise + light + thời gian đã ngủ → Sleep Score |
| RELAX Game | Canvas 320×240, game loop ~60 fps qua Sprite |
| RELAX Music | Tên bài, trạng thái play/pause, progress bar |

### Hoạt động thế nào

```
Backlight LED → [Polarizer] → [TFT matrix] → [LC Cell] → [Color Filter RGB] → mắt người
```

- **Backlight LED** phát sáng trắng từ sau màn hình
- **TFT matrix** — mỗi pixel có 1 transistor, nhận điện áp từ chip ILI9341
- **LC Cell** — điện áp cao/thấp → phân tử tinh thể lỏng xoay → cho nhiều/ít sáng qua
- **Color Filter** — 3 sub-pixel R/G/B ghép thành màu cuối

Chip **ILI9341** giữ toàn bộ nội dung trong GRAM nội (`240×320×2 = 150 KB`). ESP32-S3 ghi dữ liệu mới qua SPI — ILI9341 tự refresh ~60 Hz.

### Thông số

| | |
|---|---|
| Kích thước | 2.4 inch |
| Độ phân giải | 240 × 320 px |
| Màu sắc | RGB565 — 16-bit, 65,536 màu |
| Giao tiếp | SPI — tối đa 40 MHz |
| Controller | ILI9341 hoặc ST7789 (API giống nhau) |
| Nguồn | 3.3 V · ~60 mA (backlight) |

### RGB565

```
Bit: [15..11] [10..5] [4..0]
      Red 5    Green 6  Blue 5
```

```cpp
uint16_t c = tft.color565(255, 128, 0);   // RGB888 → RGB565

// Màu định sẵn
TFT_BLACK   TFT_WHITE   TFT_RED     TFT_GREEN
TFT_BLUE    TFT_YELLOW  TFT_CYAN    TFT_MAGENTA   TFT_ORANGE
```

### Chân kết nối

| Chân | GPIO (ESP32-S3) | Mô tả |
|---|---|---|
| VCC | 3.3V | Nguồn |
| GND | GND | Đất |
| CS | 5 | Chip Select — LOW để chọn |
| RESET | 4 | Reset controller — pulse LOW 10ms khi init |
| DC/RS | 2 | HIGH = data pixel · LOW = lệnh register |
| SDI/MOSI | 23 | Data ESP32 → TFT |
| SCK | 18 | SPI clock |
| LED/BL | 21 | Backlight — HIGH bật full, PWM để dim |

MISO không cần nối nếu chỉ write. Share SPI bus với SD card thì cần MISO + CS riêng cho mỗi thiết bị.

---

## TFT_eSPI — Thư viện

### Cài đặt

Arduino IDE → Library Manager → `TFT_eSPI` by Bodmer → Install.

### User_Setup.h — bắt buộc cấu hình

File tại `Arduino/libraries/TFT_eSPI/User_Setup.h`. Sai hoặc bỏ qua → màn hình không hiển thị gì. Sau khi sửa phải **rebuild lại project**.

```cpp
#define ILI9341_DRIVER      // chọn driver — chỉ uncomment 1 dòng
// #define ST7789_DRIVER

#define TFT_WIDTH   240
#define TFT_HEIGHT  320

// Pin — ESP32-S3
#define TFT_MOSI  23
#define TFT_MISO  -1        // không dùng nếu chỉ write
#define TFT_SCLK  18
#define TFT_CS     5
#define TFT_DC     2
#define TFT_RST    4

#define SPI_FREQUENCY  27000000   // 27 MHz ổn định — dây dài, breadboard
// #define SPI_FREQUENCY  40000000  // 40 MHz — PCB, dây ngắn

#define ESP32_DMA                 // bật DMA (tùy chọn, tăng tốc)
```

### API — vẽ hình

```cpp
TFT_eSPI tft = TFT_eSPI();

tft.init();
tft.setRotation(1);               // 0=portrait 240×320 · 1=landscape 320×240
tft.fillScreen(TFT_BLACK);

tft.fillRect(x, y, w, h, color);
tft.drawRect(x, y, w, h, color);
tft.fillRoundRect(x, y, w, h, radius, color);
tft.fillCircle(x, y, r, color);
tft.fillTriangle(x0,y0, x1,y1, x2,y2, color);
tft.drawFastHLine(x, y, w, color);   // nhanh hơn drawLine khi ngang
tft.drawFastVLine(x, y, h, color);   // nhanh hơn drawLine khi dọc
```

### API — text

```cpp
// Luôn dùng 2 tham số màu khi text thay đổi — tự xóa text cũ
tft.setTextColor(TFT_WHITE, TFT_BLACK);

// drawString(text, x, y, font)
tft.drawString("Hello", 10, 20, 2);    // font 2 = 16pt
tft.drawString("25:00", 80, 80, 7);    // font 7 = 48pt digits — đẹp cho timer

// Font numbers:
// 1=6pt  2=16pt  4=26pt  6=48pt  7=48pt  8=75pt
// Font 6,7,8 chỉ render được 0-9 và ':'

// Căn giữa
int x = (320 - tft.textWidth("TEXT", 4)) / 2;
tft.drawString("TEXT", x, y, 4);
```

### Sprite — chống nháy màn hình

Vẽ thẳng lên TFT → xóa rồi vẽ lại → người dùng thấy nháy.  
Sprite = vùng RAM, vẽ xong push ra TFT một lần → không nháy.

```cpp
TFT_eSprite spr = TFT_eSprite(&tft);

void setup() {
  tft.init();
  spr.createSprite(240, 60);      // 240×60×2 = 28,800 byte RAM
}

void loop() {
  spr.fillSprite(TFT_BLACK);      // xóa trong RAM — nhanh
  spr.setTextColor(TFT_WHITE, TFT_BLACK);
  spr.drawString(String(millis() / 1000) + "s", 10, 15, 4);
  spr.pushSprite(0, 90);          // push ra TFT — atomic, không nháy
  delay(50);
}
```

| Hàm | Mô tả |
|---|---|
| `spr.createSprite(w, h)` | Cấp phát RAM — `w×h×2` byte |
| `spr.deleteSprite()` | Giải phóng RAM — gọi trong `onExit()` |
| `spr.setColorDepth(8)` | 1 byte/pixel — tiết kiệm RAM, màu 256 |
| `spr.fillSprite(color)` | Xóa sprite |
| `spr.pushSprite(x, y)` | Push ra TFT — không nháy |
| `spr.pushSpriteDMA(x, y)` | Push qua DMA non-blocking — cần `#define ESP32_DMA` |

### Backlight dimming

```cpp
ledcSetup(7, 5000, 8);            // channel 7, 5 kHz, 8-bit
ledcAttachPin(21, 7);             // BL pin = 21

void setBrightness(int pct) {     // 0–100
  ledcWrite(7, map(pct, 0, 100, 0, 255));
}
```

### Share SPI bus: TFT + MicroSD

```cpp
// TFT_CS = 5, SD_CS = 32 — cùng MOSI/MISO/SCK, CS riêng
void setup() {
  SPI.begin(18, 19, 23);    // SCK, MISO, MOSI
  tft.init();               // dùng TFT_CS = 5
  SD.begin(32);             // dùng SD_CS = 32
}
```

---

## Debug nhanh

| Triệu chứng | Nguyên nhân |
|---|---|
| Màn hình trắng/đen hoàn toàn | Sai driver trong User_Setup.h · sai pin CS/DC/RST · chưa gọi `tft.init()` |
| Màu sai / sọc ngang | SPI clock quá cao → giảm xuống 27 MHz |
| Text nháy khi update | Không dùng Sprite · hoặc thiếu tham số `bg` trong `setTextColor(fg, bg)` |
| Xoay sai hướng | Thử `setRotation(0/1/2/3)` |
| SD card không mount | `SPI.begin()` phải gọi trước `SD.begin()` · sai CS pin · format lại FAT32 |
| ADC đọc sai khi WiFi bật | Đang dùng ADC2 → chuyển sang ADC1 (GPIO 1–10) |
| Firebase fail | NTP chưa sync · sai API key / database URL |

---

## Tóm lại

```
ESP32-S3  =  não — xử lý, điều phối, kết nối tất cả ngoại vi
TFT       =  mặt — hiển thị kết quả ra cho người dùng
```

ESP32-S3 đọc sensor → tính toán → quyết định → ghi lên TFT.  
TFT không tự làm gì — chỉ render những gì ESP32-S3 chỉ định.
