# Project 3: Smart Plant Monitor with Web Calibration

A plant health monitoring system featuring automated soil moisture sensing, web threshold calibration, sound alerts, and an interactive phone dashboard.

No potentiometer or screwdriver required: calibrate your desired dry trigger directly from your smartphone or browser using the live threshold slider.

---

## Parts Required

From your **Hosyond 45-in-1 Kit** & **Starter Kit**:
1. **Raspberry Pi Pico W**
2. **830-Point Breadboard**
3. **Water Level Detection Sensor Module** (Kit Card: Row 1, #9 — red PCB with exposed parallel immersion traces)
4. **Active Buzzer Module** (Kit Card: Row 5, #43, KY-012 — black epoxy sealed bottom)
5. **3x Discrete LEDs**: Green (Healthy), Yellow (Moderate), Red (Dry) + 3x 220-ohm resistors
6. **Jumper Wires**

---

## Pin Connections & Wiring Guide

> **Important:** Always wire your circuit with the Pico W **unplugged from USB**.

### 1. Power Distribution
| From Pico W Pin | Label | Wire To | Purpose |
| :--- | :--- | :--- | :--- |
| **Pin 36** | `3V3 OUT` | Breadboard Red (+) Power Rail | Main 3.3V power bus for sensor and LEDs |
| **Pin 38** | `GND` | Breadboard Blue (-) Ground Rail | Common circuit ground |

---

### 2. Sensor Connections

#### Water Level / Soil Moisture Sensor Module (Row 1, #9)
| PCB Pin Label | Physical Position | Connects To | Pico W Pin Details | Function |
| :--- | :--- | :--- | :--- | :--- |
| **`+`** | Middle pin | Breadboard Red (+) Rail | `3.3V Power` | Sensor power supply |
| **`-`** | Ground pin (marked `-`) | Breadboard Blue (-) Rail | `Common GND` | Ground reference |
| **`S`** | Signal pin | **Pico Physical Pin 31** | **`GP26 / ADC0`** | Analog moisture reading (0–65535 raw ADC) |

---

### 3. Indicator & Alarm Connections

#### Status LEDs (3x Discrete LEDs from Starter Kit)
| LED Color | Plant State | Anode (+) Pin | Cathode (-) Pin | Pico W Details |
| :--- | :--- | :--- | :--- | :--- |
| **Green** | Healthy / Hydrated | Through 220-ohm to **Pico Pin 21** | Breadboard Blue (-) Rail | **`GP16`** |
| **Yellow** | Moderate / Getting Low | Through 220-ohm to **Pico Pin 22** | Breadboard Blue (-) Rail | **`GP17`** |
| **Red** | Critically Dry / Alert | Through 220-ohm to **Pico Pin 24** | Breadboard Blue (-) Rail | **`GP18`** |

*(Connect each GPIO pin to a 220-ohm resistor, connect the other end of the resistor to the longer anode leg of the LED, and connect the shorter cathode leg to the Blue GND rail).*

#### Active Buzzer Module (`KY-012`, Row 5, #43)
*(Note: Has a solid black epoxy seal on the bottom. Sounds a short chirp when moisture drops below threshold).*
| PCB Pin Label | Physical Position | Connects To | Pico W Pin Details | Function |
| :--- | :--- | :--- | :--- | :--- |
| **`S`** | Signal pin | **Pico Physical Pin 25** | **`GP19`** | Chirp alarm control (HIGH = Sound) |
| **`-`** | Ground pin (marked `-`) | Breadboard Blue (-) Rail | `Common GND` | Ground |
| **`+`** | Middle pin | *Leave Unconnected* | *Not Connected* | Internal dummy pin on KY-012 |

---

## How to Run

1. Open this folder in VS Code with the **MicroPico** extension installed.
2. Ensure your [`secrets.py`](../secrets.py) is configured with your 2.4 GHz Wi-Fi credentials (`WIFI_SSID` and `WIFI_PASSWORD`) and uploaded to the Pico.
3. Plug in your Pico W via USB.
4. Open [`main.py`](./main.py) and press **`Ctrl+F5`** (or click **MicroPico: Run current file** in the status bar).
5. The VS Code terminal will output the Pico's IP address:
   ```text
   Connecting to Wi-Fi: MyHomeWiFi ...
   Plant Monitor online at http://192.168.1.113
   ```
6. Insert the sensor probe into your plant's soil.
7. Open the URL on your phone or computer to view the live moisture gauge, and adjust the threshold slider to match your plant's watering needs.
