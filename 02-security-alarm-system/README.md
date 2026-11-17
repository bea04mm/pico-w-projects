# Project 2: Security & Intrusion Alarm System

A connected security alarm system featuring physical and web-based arming/disarming, motion or vibration detection, active buzzer alarm sirens, and instant web alert notifications.

---

## Parts Required

From your **Hosyond 45-in-1 Kit** & **Starter Kit**:
1. **Raspberry Pi Pico W**
2. **830-Point Breadboard**
3. **Motion / Intrusion Sensor**:
   * **HC-SR501 PIR Motion Sensor** (Kit Card: Row 3, #27 — white dome lens) **OR**
   * **Shock Sensor Module** (Kit Card: Row 4, #34, KY-002 vibration sensor)
4. **Active Buzzer Module** (Kit Card: Row 5, #43, KY-012 — black epoxy sealed bottom)
5. **Button**: Hosyond **Button Module** (Kit Card: Row 5, #37, KY-004) or tactile push button from starter kit
6. **Status Indicators**: **Two-Color LED** (Row 4, #29) / **Mini Two-Color** (Row 4, #28) OR 2x discrete LEDs (Green & Red) + 2x 220Ω resistors
7. **Jumper Wires**

---

## Pin Connections & Wiring Guide

> **Important:** Always wire your circuit with the Pico W **unplugged from USB**.

### 1. Power Distribution
| From Pico W Pin | Label | Wire To | Purpose |
| :--- | :--- | :--- | :--- |
| **Pin 40** | `VBUS` (5V from USB) | HC-SR501 PIR `VCC` pin | **5V Power for PIR Sensor** (Required! The onboard 3.3V regulator on the PIR fails if given only 3.3V) |
| **Pin 36** | `3V3 OUT` | Breadboard Red (+) Power Rail | 3.3V power bus for button, shock sensor, and LEDs |
| **Pin 38** | `GND` | Breadboard Blue (-) Ground Rail | Common circuit ground |

---

### 2. Sensor Connections (Choose Option A or Option B)

#### Option A: HC-SR501 PIR Motion Sensor (Row 3, #27)
*(Under the white dome, looking at the 3-pin connector with the orange adjustment potentiometers facing UP)*:
| PCB Pin Label | Physical Position | Connects To | Pico W Pin Details | Function |
| :--- | :--- | :--- | :--- | :--- |
| **`VCC`** | Left pin | **Pico Physical Pin 40** | **`VBUS (5V USB)`** | 5V Power for sensor's onboard 7133 regulator |
| **`OUT`** | Center pin | **Pico Physical Pin 19** | **`GP14`** | Digital motion signal (3.3V logic: HIGH when motion detected) |
| **`GND`** | Right pin | Breadboard Blue (-) Rail | `Common GND` | Ground reference |

#### Option B: Shock / Vibration Sensor Module (`KY-002`, Row 4, #34)
| PCB Pin Label | Physical Position | Connects To | Pico W Pin Details | Function |
| :--- | :--- | :--- | :--- | :--- |
| **`S`** | Signal pin | **Pico Physical Pin 19** | **`GP14`** | Digital vibration signal |
| **`+`** | Middle pin | Breadboard Red (+) Rail | `3.3V Power` | Module pull-up power |
| **`-`** | Ground pin (marked `-`) | Breadboard Blue (-) Rail | `Common GND` | Ground reference |

---

### 3. Alarm Siren & Controller Connections

#### Active Buzzer Module (`KY-012`, Row 5, #43)
*(Note: Has a solid black epoxy seal on the bottom. Produces tone when pin is pulled HIGH).*
| PCB Pin Label | Physical Position | Connects To | Pico W Pin Details | Function |
| :--- | :--- | :--- | :--- | :--- |
| **`S`** | Signal pin | **Pico Physical Pin 20** | **`GP15`** | Alarm siren control (HIGH = Alarm ON) |
| **`-`** | Ground pin (marked `-`) | Breadboard Blue (-) Rail | `Common GND` | Ground |
| **`+`** | Middle pin | *Leave Unconnected* | *Not Connected* | Internal dummy pin on KY-012 |

#### Arm / Disarm Push Button (`KY-004`, Row 5, #37)
| PCB Pin Label | Physical Position | Connects To | Pico W Pin Details | Function |
| :--- | :--- | :--- | :--- | :--- |
| **`S`** | Signal pin | **Pico Physical Pin 21** | **`GP16`** | Physical button input (Internal Pull-Up) |
| **`-`** | Ground pin (marked `-`) | Breadboard Blue (-) Rail | `Common GND` | Ground reference (shorts to S on press) |
| **`+`** | Middle pin | Breadboard Red (+) Rail or Unconnected | `3.3V Power` | Optional module pull-up |

*(If using a standalone tactile push button from the starter kit: connect Leg 1 to Pico Pin 21 / GP16, and Leg 2 to Breadboard Blue GND Rail).*

#### Armed / Disarmed Status LEDs (`KY-011` / `KY-029` or Discrete LEDs)
| Component | Anode (+) Pin | Cathode (-) Pin | Pico W Details | Function |
| :--- | :--- | :--- | :--- | :--- |
| **Green LED** | Through 220Ω to **Pico Pin 22** | Breadboard Blue (-) Rail | **`GP17`** | Solid ON when system is **DISARMED** |
| **Red LED** | Through 220Ω to **Pico Pin 24** | Breadboard Blue (-) Rail | **`GP18`** | Slow blink when **ARMED**, fast flash during **ALARM** |

*(If using the KY-029 / KY-011 module: pin `-` to GND, pin `G` to Pico Pin 22 / GP17, pin `R` to Pico Pin 24 / GP18).*

---

## Optional: Discord Intrusion Alerts Setup

If you want real-time notification alerts sent to your phone or PC via Discord whenever an intrusion is detected:

1. Open Discord, go to **Server Settings** > **Integrations** > **Webhooks** (or right-click a channel > **Edit Channel** > **Integrations**).
2. Click **New Webhook**, give it a name (e.g. `Pico Security Node`), and click **Copy Webhook URL**.
3. Open `secrets.py` and paste the URL:
   ```python
   DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/YOUR_WEBHOOK_URL_HERE"
   ```
4. If you leave `DISCORD_WEBHOOK_URL = ""` empty, the system runs locally and skips sending web notifications.

---

## How to Run

1. Open this folder in VS Code with the **MicroPico** extension installed.
2. Ensure your [`secrets.py`](../secrets.py) is configured with your 2.4 GHz Wi-Fi credentials (`WIFI_SSID` and `WIFI_PASSWORD`, plus optional `DISCORD_WEBHOOK_URL`) and uploaded to the Pico.
3. Plug in your Pico W via USB.
4. Open [`main.py`](./main.py) and press **`Ctrl+F5`** (or click **MicroPico: Run current file** in the status bar).
5. The VS Code terminal will output the Pico's IP address:
   ```text
   Connecting to Wi-Fi: MyHomeWiFi ...
   Security system active at http://192.168.1.112
   ```
6. Press the physical push button or click **ARM SYSTEM** in your browser. When motion or vibration is detected, the siren sounds and the intrusion is logged in real time!
