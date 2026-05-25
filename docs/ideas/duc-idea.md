# SmartDesk Buddy — AIoT Productivity & Wellness Companion

Một thiết bị AIoT để bàn tích hợp hỗ trợ học tập, theo dõi môi trường, đánh giá giấc ngủ và giải trí cá nhân.
Thiết bị vận hành trên nền tảng ESP32 kết hợp TinyML/Edge AI, có khả năng xử lý trực tiếp tín hiệu âm thanh từ microphone INMP441 và đồng bộ dữ liệu lên cloud phục vụ phân tích, thống kê và hiển thị web dashboard.

---

## 1. System Overview

### 1.1 Hardware Components

| Thành phần     | Mô tả                                  |
| -------------- | -------------------------------------- |
| MCU            | ESP32-S3                               |
| Display        | TFT LCD Display                        |
| Audio Input    | INMP441 MEMS Microphone                |
| Audio Output   | Speaker/Buzzer                         |
| Interaction    | 5 Physical Buttons                     |
| Sensor         | Ambient Light Sensor                   |
| Connectivity   | WiFi                                   |
| Database       | Firebase                               |
| Backend Server | AI Evaluation & Data Processing Server |

### 1.2 System Architecture

```mermaid
flowchart LR
    subgraph Device["ESP32-S3 (Edge)"]
        BTN[Buttons]
        MIC[INMP441]
        LUX[Light Sensor]
        TFT[TFT Display]
        SPK[Speaker]
        EDGE[Edge AI / TinyML]
    end

    subgraph Cloud["Cloud Layer"]
        FB[(Firebase)]
        SRV[AI Server]
        WEB[Web Dashboard]
    end

    BTN --> TFT
    MIC --> EDGE
    LUX --> EDGE
    EDGE --> TFT
    EDGE --> SPK
    Device <-->|WiFi sync| FB
    FB <--> SRV
    FB --> WEB
    SRV -->|Analysis result| FB
```

---

## 2. System States & Navigation

### 2.1 Top-Level States

| State | Chức năng           |
| ----- | ------------------- |
| HOME  | Giám sát môi trường |
| STUDY | Hỗ trợ học tập      |
| SLEEP | Hỗ trợ giấc ngủ     |
| RELAX | Giải trí            |

**Button (1):** chuyển vòng trạng thái `HOME → STUDY → SLEEP → RELAX → HOME`.

### 2.2 Global State Machine

```mermaid
stateDiagram-v2
    [*] --> HOME

    HOME --> STUDY: Btn1
    STUDY --> SLEEP: Btn1
    SLEEP --> RELAX: Btn1
    RELAX --> HOME: Btn1

    state STUDY {
        [*] --> StudyMenu
        StudyMenu --> Pomodoro: Btn2
        StudyMenu --> Seminar: Btn3
        Pomodoro --> StudyTimer: Btn5
        StudyTimer --> Pomodoro: Btn2 confirm
        Pomodoro --> StudyMenu: Btn2
        Seminar --> StudyMenu: Btn2
    }

    state SLEEP {
        [*] --> SleepMenu
        SleepMenu --> StartSleep: Btn2
        SleepMenu --> SleepSettings: Btn3
        SleepMenu --> SleepTimer: Btn4
        StartSleep --> SleepMenu: Btn2 stop + confirm
        SleepSettings --> SleepTimer: Btn4
        SleepTimer --> SleepSettings: Btn2 confirm
        SleepSettings --> SleepMenu: Btn2 confirm
    }

    state RELAX {
        [*] --> RelaxMenu
        RelaxMenu --> FlappyBird: Btn2
        RelaxMenu --> MusicPlayer: Btn3
        FlappyBird --> RelaxMenu: Btn2
        MusicPlayer --> RelaxMenu: Btn2
    }
```

### 2.3 Screen Hierarchy

```text
HOME
├── STUDY
│   ├── Pomodoro
│   │   └── STUDY_TIMER (cấu hình)
│   └── Seminar Practice
├── SLEEP
│   ├── START_SLEEP (monitoring)
│   ├── Sleep Settings
│   └── SLEEP_TIMER (cấu hình)
└── RELAX
    ├── Flappy Bird
    └── Music Player
```

---

## 3. Functional Specification

---

### 3.0 HOME — Environmental Monitoring

#### Mục tiêu

Hiển thị realtime chất lượng môi trường xung quanh.

#### Thông tin hiển thị

| Thông tin     | Mô tả                        |
| ------------- | ---------------------------- |
| Sound Level   | Mức độ âm thanh              |
| Sound Quality | Đánh giá chất lượng âm thanh |
| Light Level   | Mức độ ánh sáng              |
| Light Quality | Đánh giá chất lượng ánh sáng |

#### Processing Flow

```mermaid
flowchart TD
    A[Đọc MIC + Light Sensor] --> B[Edge AI phân loại]
    B --> C{Âm thanh}
    B --> D{Ánh sáng}
    C --> C1[Quiet / Noisy]
    D --> D1[Suitable / Unsuitable]
    C1 --> E[Cập nhật TFT realtime]
    D1 --> E
```

| Bước | Thành phần | Hành động |
| ---- | ---------- | --------- |
| 1    | INMP441    | Thu mẫu audio liên tục |
| 2    | Light Sensor | Đọc cường độ ánh sáng |
| 3    | Edge AI    | Phân loại môi trường (Quiet/Noisy, Suitable/Unsuitable) |
| 4    | TFT        | Render metrics và trạng thái đánh giá |

---

### 3.1 STUDY — Learning Assistant

#### Main Menu — Input Mapping

| Button     | Hành động        |
| ---------- | ---------------- |
| Button (2) | Mở Pomodoro      |
| Button (3) | Mở Practice Seminar |

---

#### 3.1.1 Pomodoro Module

**Cấu hình mặc định:** Study 25 min · Break 5 min

##### User Flow

```mermaid
flowchart TD
    A[STUDY Menu] -->|Btn2| B[Pomodoro Screen]
    B -->|Btn3| C{Timer đang chạy?}
    C -->|No| D[Start Timer]
    C -->|Yes| E[Stop Timer]
    B -->|Btn4| F[Reset Timer]
    B -->|Btn5| G[STUDY_TIMER Config]
    G -->|Btn2 confirm| B
    B -->|Btn2| A
    D --> H[Session Complete]
    E --> B
    F --> B
    H --> I[3× Beep + Log Firebase]
    I --> B
```

##### Input Mapping

| Button     | Hành động              |
| ---------- | ---------------------- |
| Button (2) | Quay về STUDY Menu     |
| Button (3) | Start / Stop Timer     |
| Button (4) | Reset Timer            |
| Button (5) | Mở STUDY_TIMER Config  |

##### Session Completion Sequence

```mermaid
sequenceDiagram
    participant U as User
    participant ESP as ESP32
    participant SPK as Speaker
    participant FB as Firebase
    participant WEB as Web Dashboard

    Note over ESP: Timer hết thời gian
    ESP->>SPK: Phát 3 tiếng beep
    ESP->>FB: Ghi session (timestamp, duration, type)
    FB->>WEB: Cập nhật analytics / productivity score
    ESP->>U: Hiển thị trạng thái hoàn tất trên TFT
```

**Payload Firebase (session log):**

- `timestamp`
- `duration`
- `session_type` (study / break)

---

#### 3.1.2 STUDY_TIMER Configuration

##### Input Mapping

| Button     | Hành động        |
| ---------- | ---------------- |
| Button (2) | Xác nhận & quay lại |
| Button (3) | Đổi đơn vị (phút/giây) |
| Button (4) | Tăng giá trị     |
| Button (5) | Giảm giá trị     |

##### Cloud Sync Sequence

```mermaid
sequenceDiagram
    participant U as User
    participant TFT as TFT Display
    participant ESP as ESP32
    participant FB as Firebase

    U->>ESP: Btn2 — Xác nhận cấu hình
    ESP->>TFT: Hiển thị loading
    ESP->>FB: PUT timer config
    FB-->>ESP: ACK
    ESP->>TFT: Cập nhật UI + quay Pomodoro

    Note over ESP,FB: Khi khởi động lại thiết bị
    ESP->>FB: GET timer config
    FB-->>ESP: Trả cấu hình
    ESP->>ESP: Đồng bộ local state
```

---

#### 3.1.3 Seminar Practice Module

Cho phép người dùng luyện thuyết trình và nhận đánh giá chất lượng giọng nói.

##### Input Mapping

| Button     | Hành động              |
| ---------- | ---------------------- |
| Button (2) | Quay về STUDY Menu     |
| Button (3) | Start / Stop Recording |
| Button (4) | Evaluate Speech        |

##### Evaluation Pipeline

```mermaid
sequenceDiagram
    participant U as User
    participant MIC as INMP441
    participant ESP as ESP32
    participant TFT as TFT Display
    participant SRV as AI Server

    U->>ESP: Btn3 — Bắt đầu ghi
    ESP->>MIC: Thu audio
    U->>ESP: Btn3 — Dừng ghi
    U->>ESP: Btn4 — Đánh giá
    ESP->>TFT: Hiển thị "Processing..."
    ESP->>SRV: Upload audio
    SRV->>SRV: Phân tích (clarity, speed, noise, confidence)
    SRV-->>ESP: Trả kết quả JSON
    ESP->>TFT: Hiển thị feedback
```

| Metric           | Mô tả                          |
| ---------------- | ------------------------------ |
| Speech clarity   | Độ rõ ràng phát âm             |
| Speaking speed   | Tốc độ nói (WPM hoặc tương đương) |
| Noise level      | Mức nhiễu môi trường            |
| Confidence score | Ước lượng độ tự tin khi nói     |

---

### 3.2 SLEEP — Sleep Monitoring Assistant

**Cấu hình mặc định:** Sleep duration 8h · Alarm disabled · Lưu trên Firebase

#### SLEEP Menu — Input Mapping

| Button     | Hành động              |
| ---------- | ---------------------- |
| Button (2) | Bắt đầu giám sát ngủ   |
| Button (3) | Mở Sleep Settings      |
| Button (4) | Mở SLEEP_TIMER Config  |

---

#### 3.2.1 START_SLEEP Screen

##### Monitoring Loop

```mermaid
flowchart TD
    A[Btn2 — Start Monitoring] --> B[START_SLEEP Screen]
    B --> C[Hiển thị realtime metrics]
    C --> D{Mỗi 240s}
    D --> E[Upload sensor batch → Firebase]
    E --> C
    C --> F{Btn2 — Stop?}
    F -->|No| C
    F -->|Yes| G[Gửi yêu cầu đánh giá → AI Server]
    G --> H[Hiển thị Sleep Score]
    H --> I[User xác nhận]
    I --> J[Quay SLEEP Menu]
```

##### Metrics hiển thị (realtime)

- Sound Level / Sound Quality
- Light Level / Light Quality
- Sleep Duration (elapsed)

##### Stop & Scoring Sequence

```mermaid
sequenceDiagram
    participant U as User
    participant ESP as ESP32
    participant FB as Firebase
    participant SRV as AI Server
    participant TFT as TFT Display

    U->>ESP: Btn2 — Stop monitoring
    ESP->>FB: Đóng session + gửi dữ liệu tổng hợp
    FB->>SRV: Trigger sleep analysis
    SRV->>SRV: Tính điểm (duration, light, sound)
    SRV-->>FB: Sleep score
    FB-->>ESP: Kết quả
    ESP->>TFT: Hiển thị báo cáo
    U->>ESP: Xác nhận
    ESP->>TFT: Quay SLEEP Menu
```

---

#### 3.2.2 Sleep Settings

##### Input Mapping

| Button     | Hành động              |
| ---------- | ---------------------- |
| Button (2) | Xác nhận & lưu         |
| Button (3) | Bật / tắt Alarm        |
| Button (4) | Mở SLEEP_TIMER Config  |

**Alarm mặc định khi bật:** 07:00 AM · Danh sách alarm hiển thị tại SLEEP Menu

---

#### 3.2.3 SLEEP_TIMER Configuration

| Button     | Hành động        |
| ---------- | ---------------- |
| Button (2) | Xác nhận & quay lại |
| Button (3) | Đổi đơn vị       |
| Button (4) | Tăng giá trị     |
| Button (5) | Giảm giá trị     |

```mermaid
sequenceDiagram
    participant ESP as ESP32
    participant FB as Firebase

    ESP->>FB: PUT sleep config (duration, alarm)
    FB-->>ESP: ACK — persistent storage
    Note over FB: Config khôi phục sau reboot
```

---

#### 3.2.4 Alarm Trigger

```mermaid
flowchart LR
    A[RTC đạt alarm time] --> B[TFT: Alarm Active]
    B --> C[Speaker: 3× beep]
    C --> D[Chờ user dismiss / snooze]
```

---

### 3.3 RELAX — Entertainment Module

#### RELAX Menu — Input Mapping

| Button     | Hành động        |
| ---------- | ---------------- |
| Button (2) | Mở Flappy Bird   |
| Button (3) | Mở Music Player  |

#### 3.3.1 Flappy Bird Mini Game

##### Input Mapping

| Button     | Hành động        |
| ---------- | ---------------- |
| Button (2) | Mở / thoát game  |
| Button (3) | Jump             |

##### Game Flow

```mermaid
flowchart TD
    A[RELAX Menu] -->|Btn2| B[Gameplay]
    B -->|Btn3| C[Jump / flap]
    C --> B
    B -->|Collision| D[Game Over]
    D --> E[Upload score → Firebase]
    E --> F[Server cập nhật leaderboard]
    F --> G{Btn2}
    G --> A
```

---

#### 3.3.2 Music Player

##### Input Mapping

| Button     | Hành động       |
| ---------- | --------------- |
| Button (2) | Quay RELAX Menu |
| Button (3) | Play / Pause    |
| Button (4) | Next track      |
| Button (5) | Previous track  |

##### Playback Flow

```mermaid
flowchart LR
    A[Chọn bài từ playlist] --> B[ESP32 decode & stream]
    B --> C[Speaker output]
    B --> D[TFT: title + status]
    D --> E{User action}
    E -->|Pause/Next/Prev| B
```

---

## 4. Objectives & Use Cases

---

### 4.1 Objective 1 — Enhance Learning Productivity

**Mô tả:** Hỗ trợ học tập và cải thiện hiệu suất làm việc cá nhân thông qua quản lý thời gian và đánh giá kỹ năng trình bày.

#### Use Case 1 — Pomodoro Study Assistant

| Tính năng | Mô tả |
| --------- | ----- |
| Pomodoro cycle | Chu kỳ 25/5 phút, cấu hình được |
| Audio notification | Beep khi hết phiên |
| Session tracking | Log mỗi phiên lên Firebase |
| Analytics | Dashboard web theo dõi productivity |

```mermaid
flowchart LR
    subgraph Edge
        U1[User] --> P[Pomodoro Timer]
        P --> S[Speaker Alert]
    end
    subgraph Cloud
        P --> FB[(Firebase)]
        FB --> D[Web Dashboard]
    end
```

#### Use Case 2 — AI Seminar Evaluation

| Tính năng | Mô tả |
| --------- | ----- |
| Voice recording | Ghi qua INMP441 |
| Speech evaluation | AI server phân tích đa metric |
| Feedback | Kết quả hiển thị TFT |

```mermaid
flowchart LR
    U2[User] --> R[Record]
    R --> UP[Upload]
    UP --> AI[AI Server]
    AI --> FB2[Result]
    FB2 --> TFT[TFT Display]
```

---

### 4.2 Objective 2 — Improve Sleep Quality

**Mô tả:** Theo dõi và đánh giá chất lượng giấc ngủ dựa trên dữ liệu môi trường và thời lượng ngủ

#### Use Case 1 — Sleep Quality Scoring

```mermaid
flowchart TD
    S[Sensors] --> E[ESP32]
    E -->|240s batch| F[(Firebase)]
    F --> AI[AI Server]
    AI --> SC[Sleep Score]
    SC --> T[TFT Display]
```

#### Use Case 2 — Smart Alarm System

```mermaid
flowchart LR
    U[User config] --> F[(Firebase)]
    F --> E[ESP32 RTC sync]
    E -->|Alarm time| SPK[Speaker]
    E --> TFT[TFT status]
```

---

### 4.3 Objective 3 — Provide Entertainment Features

**Mô tả:** Tăng trải nghiệm người dùng thông qua game mini và phát nhạc trực tiếp trên thiết bị.

#### Use Case 1 — Flappy Bird

```mermaid
flowchart LR
    U[User] --> G[Gameplay]
    G --> GO[Game Over]
    GO --> FB[(Firebase Leaderboard)]
```

#### Use Case 2 — Music Player

```mermaid
flowchart LR
    U[User] --> PL[Playlist]
    PL --> ESP[ESP32 Playback]
    ESP --> SPK[Speaker]
    ESP --> TFT[TFT UI]
```
