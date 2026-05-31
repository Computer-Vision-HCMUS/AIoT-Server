# ESP32 Arduino — Chuẩn OOP & Tổ chức File

> Ví dụ thực tế: **SmartDesk Buddy** (TFT + INMP441 + BH1750 + DS3231 + MAX98357A)

---

## Cây thư mục

```
SmartDeskBuddy/
│
├── SmartDeskBuddy.ino          # Entry point: khai báo object + gọi begin()/update()
├── config.h                    # Toàn bộ hằng số: pin, WiFi, threshold, interval
│
├── hal/                        # Hardware Abstraction Layer — wrap từng chip
│   ├── ISensor.h               # Abstract interface cho mọi sensor
│   ├── SoundSensor.h / .cpp    # INMP441
│   ├── LightSensor.h / .cpp    # BH1750
│   ├── RtcModule.h   / .cpp    # DS3231
│   └── AudioPlayer.h / .cpp    # MAX98357A + SD card
│
├── ui/                         # Toàn bộ render TFT — không có business logic
│   ├── Screen.h                # Abstract base class: onEnter / update / onExit
│   ├── HomeScreen.h  / .cpp
│   ├── StudyScreen.h / .cpp
│   ├── SleepScreen.h / .cpp
│   └── RelaxScreen.h / .cpp
│
├── core/                       # Business logic — không phụ thuộc hardware cụ thể
│   ├── StateMachine.h  / .cpp  # HOME → STUDY → SLEEP → RELAX
│   ├── PomodoroTimer.h / .cpp
│   ├── SleepMonitor.h  / .cpp
│   ├── AlertManager.h  / .cpp
│   └── DataCollector.h / .cpp  # Orchestrate: đọc sensor → JSON → Firebase
│
├── network/
│   ├── WiFiManager.h    / .cpp
│   └── FirebaseClient.h / .cpp
│
└── utils/                      # Không phụ thuộc project, dùng lại được
    ├── Logger.h                # Header-only
    └── TimeUtils.h             # Header-only
```

---

## Dependency — layer nào dùng layer nào

```
SmartDeskBuddy.ino
       │
  ┌────┼────┬─────┐
  ▼    ▼    ▼     ▼
core/ ui/ network/ hal/ (init trực tiếp)
  │    │
  ▼    ▼
 hal/ hal/          ← qua ISensor interface
  │
  ▼
utils/
```

**Quy tắc cứng:** mũi tên chỉ đi xuống.  
`hal/` không bao giờ `#include` file từ `core/` hay `ui/`.  
`core/` không bao giờ `#include <TFT_eSPI.h>` hay bất kỳ thư viện display nào.

---

## Đặt code ở đâu?

| Đây là gì | Đặt ở đâu |
|---|---|
| Đọc INMP441 / BH1750 / DS3231 | `hal/SoundSensor.cpp` ... |
| Vẽ màn hình | `ui/HomeScreen.cpp` ... |
| Logic Pomodoro (đếm giây, session) | `core/PomodoroTimer.cpp` |
| Quy tắc chuyển state HOME→STUDY... | `core/StateMachine.cpp` |
| Upload Firebase / MQTT | `network/FirebaseClient.cpp` |
| WiFi connect + reconnect | `network/WiFiManager.cpp` |
| Hằng số: pin, SSID, threshold | `config.h` |
| Serial debug log | `utils/Logger.h` |
| Khai báo object + gọi begin/update | `SmartDeskBuddy.ino` — **chỉ ở đây** |

---

## config.h

```cpp
#pragma once

// ── Pin ──────────────────────────────────────────
#define PIN_MIC_WS      15
#define PIN_MIC_SCK     14
#define PIN_MIC_SD      13

#define PIN_AMP_BCLK    26
#define PIN_AMP_LRC     25
#define PIN_AMP_DIN     22

#define PIN_SDA         21
#define PIN_SCL         22

#define PIN_RTC_INT     35
#define PIN_SD_CS       32

#define PIN_BTN1        34
#define PIN_BTN2        36
#define PIN_BTN3        37
#define PIN_BTN4        38
#define PIN_BTN5        39

#define PIN_BUZZER      33
#define PIN_BL          21

// ── WiFi / Firebase ───────────────────────────────
#define WIFI_SSID       "YourSSID"
#define WIFI_PASSWORD   "YourPassword"
#define FB_URL          "https://your-project.firebaseio.com"
#define FB_KEY          "your-api-key"
#define DEVICE_ID       "desk-01"

// ── Threshold ────────────────────────────────────
#define SOUND_NOISY_DB  65.0f   // dB
#define LIGHT_MIN_LUX   300.0f
#define LIGHT_MAX_LUX   1500.0f

// ── Timing ───────────────────────────────────────
#define PUBLISH_INTERVAL_MS   30000
#define POMODORO_STUDY_MIN    25
#define POMODORO_BREAK_MIN    5
#define DOOR_ALERT_MS         120000
#define TFT_ROTATION          1
```

---

## hal/ — ISensor interface

```cpp
// hal/ISensor.h
#pragma once
#include <Arduino.h>
#include <ArduinoJson.h>

class ISensor {
public:
  virtual ~ISensor() = default;
  virtual bool        begin()                       = 0;
  virtual bool        read()                        = 0;
  virtual void        toJson(JsonObject& out) const = 0;
  virtual const char* name()               const    = 0;
  virtual bool        isOk()              const { return _ok; }
protected:
  bool _ok = false;
};
```

### Concrete sensor — cấu trúc chuẩn

**`.h` — chỉ khai báo, không implement**

```cpp
// hal/SoundSensor.h
#pragma once
#include "ISensor.h"
#include <driver/i2s.h>

class SoundSensor : public ISensor {
public:
  SoundSensor(i2s_port_t port, int wsPin, int sckPin, int sdPin);

  bool        begin()                       override;
  bool        read()                        override;
  void        toJson(JsonObject& out) const override;
  const char* name()                  const override { return "INMP441"; }

  float  decibels() const { return _db; }
  bool   isNoisy()  const { return _db > NOISE_THRESHOLD; }
  String quality()  const { return isNoisy() ? "NOISY" : "QUIET"; }

private:
  i2s_port_t _port;
  int        _ws, _sck, _sd;
  float      _db = 0.0f;

  static constexpr float NOISE_THRESHOLD = 65.0f;
  float computeRMS(int32_t* samples, int count);
};
```

**`.cpp` — implement, import thư viện tại đây**

```cpp
// hal/SoundSensor.cpp
#include "SoundSensor.h"   // luôn include .h tương ứng đầu tiên

SoundSensor::SoundSensor(i2s_port_t port, int ws, int sck, int sd)
  : _port(port), _ws(ws), _sck(sck), _sd(sd) {}

bool SoundSensor::begin() {
  i2s_config_t cfg = {
    .mode             = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate      = 16000,
    .bits_per_sample  = I2S_BITS_PER_SAMPLE_32BIT,
    .channel_format   = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_STAND_I2S,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count    = 4,
    .dma_buf_len      = 256,
  };
  i2s_pin_config_t pins = {
    .bck_io_num  = _sck, .ws_io_num = _ws,
    .data_in_num = _sd,  .data_out_num = I2S_PIN_NO_CHANGE,
  };
  _ok = (i2s_driver_install(_port, &cfg, 0, NULL) == ESP_OK);
  if (_ok) i2s_set_pin(_port, &pins);
  return _ok;
}

bool SoundSensor::read() {
  int32_t buf[256]; size_t bytes;
  if (i2s_read(_port, buf, sizeof(buf), &bytes, 50) != ESP_OK)
    return (_ok = false);
  _db = 20.0f * log10f(computeRMS(buf, bytes / 4) + 1e-9f) + 120.0f;
  return (_ok = true);
}

void SoundSensor::toJson(JsonObject& out) const {
  out["sound_db"]      = _db;
  out["sound_quality"] = quality();
}

float SoundSensor::computeRMS(int32_t* s, int n) {
  double sum = 0;
  for (int i = 0; i < n; i++) {
    double v = (double)(s[i] >> 8) / 8388608.0;
    sum += v * v;
  }
  return (float)sqrt(sum / n);
}
```

> **Quy tắc `.h` / `.cpp`**
> - `.h` — `#pragma once`, khai báo class, inline chỉ khi method 1 dòng
> - `.cpp` — `#include "ClassName.h"` luôn là dòng đầu tiên, thư viện nặng (`<driver/i2s.h>`, `<BH1750.h>`...) import ở đây, không ở `.h`
> - 1 class = 1 cặp file, tên file = tên class

---

## ui/ — Screen hierarchy

```cpp
// ui/Screen.h
#pragma once
#include <TFT_eSPI.h>

class Screen {
public:
  explicit Screen(TFT_eSPI& tft) : _tft(tft) {}
  virtual ~Screen() = default;

  virtual void onEnter() = 0;   // khởi tạo sprite, vẽ nền tĩnh
  virtual void update()  = 0;   // gọi mỗi loop, chỉ redraw phần thay đổi
  virtual void onExit()  = 0;   // giải phóng sprite

protected:
  TFT_eSPI& _tft;
  void drawHeader(const char* title, uint16_t color);
};
```

```cpp
// ui/HomeScreen.h
#pragma once
#include "Screen.h"
#include "../hal/SoundSensor.h"
#include "../hal/LightSensor.h"

class HomeScreen : public Screen {
public:
  HomeScreen(TFT_eSPI& tft,
             const SoundSensor& sound,
             const LightSensor& light);

  void onEnter() override;
  void update()  override;
  void onExit()  override;

private:
  const SoundSensor& _sound;   // const ref — chỉ đọc
  const LightSensor& _light;
  TFT_eSprite        _spr;
  unsigned long      _lastDraw = 0;
};
```

```cpp
// ui/HomeScreen.cpp
#include "HomeScreen.h"

HomeScreen::HomeScreen(TFT_eSPI& tft,
                       const SoundSensor& sound,
                       const LightSensor& light)
  : Screen(tft), _sound(sound), _light(light), _spr(&tft) {}

void HomeScreen::onEnter() {
  _tft.fillScreen(TFT_BLACK);
  drawHeader("HOME", TFT_CYAN);
  _spr.createSprite(300, 160);
}

void HomeScreen::update() {
  if (millis() - _lastDraw < 500) return;
  _lastDraw = millis();

  _spr.fillSprite(TFT_BLACK);
  // vẽ metric card sound + light
  _spr.pushSprite(10, 35);
}

void HomeScreen::onExit() {
  _spr.deleteSprite();
}
```

---

## core/ — StateMachine

```cpp
// core/StateMachine.h
#pragma once
#include "../ui/Screen.h"

enum class AppState { HOME, STUDY, SLEEP, RELAX };

class StateMachine {
public:
  StateMachine(Screen& home, Screen& study,
               Screen& sleep, Screen& relax);

  void begin();
  void update();   // xử lý nút + gọi currentScreen->update()

private:
  Screen*  _screens[4];
  AppState _state = AppState::HOME;
  unsigned long _lastBtn = 0;

  void transitionTo(AppState next);
  void handleButtons();
};
```

```cpp
// core/StateMachine.cpp
#include "StateMachine.h"
#include "../config.h"

StateMachine::StateMachine(Screen& home, Screen& study,
                           Screen& sleep, Screen& relax) {
  _screens[0] = &home;
  _screens[1] = &study;
  _screens[2] = &sleep;
  _screens[3] = &relax;
}

void StateMachine::begin() { transitionTo(AppState::HOME); }

void StateMachine::update() {
  handleButtons();
  _screens[(int)_state]->update();
}

void StateMachine::transitionTo(AppState next) {
  _screens[(int)_state]->onExit();
  _state = next;
  _screens[(int)_state]->onEnter();
}

void StateMachine::handleButtons() {
  if (millis() - _lastBtn < 200) return;
  if (digitalRead(PIN_BTN1) == LOW) {
    _lastBtn = millis();
    transitionTo((AppState)(((int)_state + 1) % 4));
  }
  // Btn2–5: Screen tự xử lý trong update() của nó
}
```

---

## core/ — DataCollector

```cpp
// core/DataCollector.h
#pragma once
#include "../hal/ISensor.h"
#include "../network/FirebaseClient.h"
#include <vector>

class DataCollector {
public:
  DataCollector(FirebaseClient& fb, const char* deviceId);

  void addSensor(ISensor* s) { _sensors.push_back(s); }
  bool begin();
  void update(unsigned long intervalMs = 30000);

private:
  std::vector<ISensor*> _sensors;
  FirebaseClient&       _fb;
  const char*           _deviceId;
  unsigned long         _lastUpload = 0;

  String buildJson();
};
```

```cpp
// core/DataCollector.cpp
#include "DataCollector.h"
#include <ArduinoJson.h>

bool DataCollector::begin() {
  bool ok = true;
  for (auto* s : _sensors)
    if (!s->begin()) ok = false;
  return ok;
}

void DataCollector::update(unsigned long intervalMs) {
  if (millis() - _lastUpload < intervalMs) return;
  _lastUpload = millis();

  for (auto* s : _sensors) s->read();

  String path = String("/devices/") + _deviceId + "/latest";
  _fb.set(path.c_str(), buildJson().c_str());
}

String DataCollector::buildJson() {
  StaticJsonDocument<512> doc;
  doc["device_id"] = _deviceId;
  doc["ts"]        = millis();
  JsonObject data  = doc.createNestedObject("data");
  for (auto* s : _sensors)
    if (s->isOk()) s->toJson(data);
  String out; serializeJson(doc, out);
  return out;
}
```

---

## SmartDeskBuddy.ino

```cpp
#include "config.h"
#include "hal/SoundSensor.h"
#include "hal/LightSensor.h"
#include "hal/RtcModule.h"
#include "hal/AudioPlayer.h"
#include "ui/HomeScreen.h"
#include "ui/StudyScreen.h"
#include "ui/SleepScreen.h"
#include "ui/RelaxScreen.h"
#include "core/StateMachine.h"
#include "core/DataCollector.h"
#include "core/AlertManager.h"
#include "network/WiFiManager.h"
#include "network/FirebaseClient.h"

// ── Hardware ──────────────────────────────────────────────────────────
TFT_eSPI     tft;
SoundSensor  sound(I2S_NUM_0, PIN_MIC_WS,  PIN_MIC_SCK,  PIN_MIC_SD);
LightSensor  light(PIN_SDA, PIN_SCL);
RtcModule    rtc  (PIN_SDA, PIN_SCL, PIN_RTC_INT);
AudioPlayer  audio(I2S_NUM_1, PIN_AMP_BCLK, PIN_AMP_LRC, PIN_AMP_DIN, PIN_SD_CS);

// ── Network ───────────────────────────────────────────────────────────
WiFiManager    wifi(WIFI_SSID, WIFI_PASSWORD);
FirebaseClient firebase(FB_URL, FB_KEY);

// ── UI ────────────────────────────────────────────────────────────────
HomeScreen   homeScreen (tft, sound, light);
StudyScreen  studyScreen(tft);
SleepScreen  sleepScreen(tft, sound, light, rtc);
RelaxScreen  relaxScreen(tft, audio);

// ── Core ──────────────────────────────────────────────────────────────
StateMachine  fsm(homeScreen, studyScreen, sleepScreen, relaxScreen);
DataCollector collector(firebase, DEVICE_ID);
AlertManager  alertMgr(firebase, DEVICE_ID);

void setup() {
  Serial.begin(115200);
  tft.init();
  tft.setRotation(TFT_ROTATION);

  wifi.connect();
  firebase.begin();

  sound.begin();
  light.begin();
  rtc.begin();
  audio.begin();

  collector.addSensor(&sound);
  collector.addSensor(&light);
  collector.begin();

  alertMgr.setThresholds(SOUND_NOISY_DB, LIGHT_MIN_LUX, LIGHT_MAX_LUX);
  fsm.begin();
}

void loop() {
  wifi.maintain();
  fsm.update();
  collector.update(PUBLISH_INTERVAL_MS);
  alertMgr.check(sound, light, rtc);
}
```

---

## utils/ — header-only

```cpp
// utils/Logger.h
#pragma once
#include <Arduino.h>

enum LogLevel { LOG_DEBUG, LOG_INFO, LOG_WARN, LOG_ERROR };

namespace Logger {
  inline LogLevel level = LOG_INFO;

  template<typename... Args>
  inline void log(LogLevel lv, const char* fmt, Args... args) {
    if (lv < level) return;
    const char* tag[] = { "DBG", "INF", "WRN", "ERR" };
    Serial.printf("[%s][%lu] ", tag[lv], millis());
    Serial.printf(fmt, args...);
    Serial.println();
  }
}

// Dùng:
// Logger::log(LOG_INFO, "Sound = %.1f dB", db);
// Logger::log(LOG_ERROR, "Firebase fail: %s", path);
```

---

## Quy tắc nhanh

| Quy tắc | Chi tiết |
|---|---|
| 1 class = 1 cặp file | `SoundSensor` → `SoundSensor.h` + `SoundSensor.cpp` |
| `.h` bắt đầu bằng | `#pragma once` |
| `.cpp` dòng đầu tiên | `#include "ClassName.h"` |
| Thư viện nặng | Import trong `.cpp`, không phải `.h` |
| Tên file = tên class | PascalCase |
| Tất cả member variable | `private`, prefix `_` |
| Dependency | Truyền qua constructor, không tự tạo bên trong |
| `delay()` trong loop | Không — dùng `millis()` |
| Magic number | Không — đưa vào `config.h` |
| main.ino | Chỉ khai báo + gọi, không có if/else logic |
