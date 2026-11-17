# Project 1: Wi-Fi Climate Station with Web Dashboard

A complete environmental monitoring station using your Raspberry Pi Pico W, the Hosyond DHT11 & LDR sensors, and an RGB LED. It hosts a modern, responsive web dashboard accessible from your phone or PC on your home Wi-Fi network.

---

## Parts Required

From your **Hosyond 45-in-1 Kit** & **Starter Kit**:
1. **Raspberry Pi Pico W**
2. **830-Point Breadboard**
3. **Temp and Humidity Module** (Kit Card: Row 2, #13, DHT11 blue casing)
4. **Photoresistor Module** (Kit Card: Row 3, #22, KY-018 light sensor)
5. **RGB LED Module** (Kit Card: Row 5, #41, KY-016 5mm RGB or Row 5, #39, KY-009 SMD RGB)
6. **Male-to-Female and Male-to-Male Jumper Wires**

---

## Pin Connections & Wiring Guide

> **Important:** Always wire your circuit with the Pico W **unplugged from USB**.

### 1. Power Distribution
| From Pico W Pin | Label | Wire To | Purpose |
| :--- | :--- | :--- | :--- |
| **Pin 36** | `3V3 OUT` | Breadboard Red (+) Power Rail | Main 3.3V power bus for all sensors |
| **Pin 38** | `GND` | Breadboard Blue (-) Ground Rail | Common circuit ground |

---

### 2. Module Pin Connections

#### Temp & Humidity Sensor (`DHT11`, Row 2, #13)
| PCB Pin Label | Pin Location on Module | Connects To | Pico W Pin Details | Function |
| :--- | :--- | :--- | :--- | :--- |
| **`+`** / `VCC` | Middle pin | Breadboard Red (+) Rail | `3.3V Power` | Sensor power supply |
| **`-`** / `GND` | Left/Right pin (marked `-`) | Breadboard Blue (-) Rail | `Common GND` | Ground |
| **`S`** / `Out` | Signal pin | **Pico Physical Pin 20** | **`GP15`** | Digital bi-directional data line |

#### Photoresistor / Light Sensor (`KY-018`, Row 3, #22)
| PCB Pin Label | Pin Location on Module | Connects To | Pico W Pin Details | Function |
| :--- | :--- | :--- | :--- | :--- |
| **`+`** | Middle pin | Breadboard Red (+) Rail | `3.3V Power` | Voltage divider power |
| **`-`** | Left pin (marked `-`) | Breadboard Blue (-) Rail | `Common GND` | Ground reference |
| **`S`** | Right pin (marked `S`) | **Pico Physical Pin 31** | **`GP26 / ADC0`** | Analog voltage output (0–65535) |

#### Full-Color RGB LED Module (`KY-016` Row 5, #41 or `KY-009` Row 5, #39)
| PCB Pin Label | Pin Location on Module | Connects To | Pico W Pin Details | Function |
| :--- | :--- | :--- | :--- | :--- |
| **`-`** | Ground pin (marked `-`) | Breadboard Blue (-) Rail | `Common GND` | Common cathode ground |
| **`R`** | Red channel pin | **Pico Physical Pin 21** | **`GP16`** | Red LED control |
| **`G`** | Green channel pin | **Pico Physical Pin 22** | **`GP17`** | Green LED control |
| **`B`** | Blue channel pin | **Pico Physical Pin 24** | **`GP18`** | Blue LED control |

*(Note: If using individual discrete LEDs from your starter kit instead of the module: connect each Pico GPIO pin through a 220Ω resistor to the longer anode leg of an LED, and connect all shorter cathode legs to the Blue GND rail).*

---

## How to Run

1. Open this folder in VS Code with the **MicroPico** extension installed.
2. Ensure your [`secrets.py`](../secrets.py) is configured with your 2.4 GHz Wi-Fi credentials (`WIFI_SSID` and `WIFI_PASSWORD`) and uploaded to the Pico.
3. Plug in your Pico W via USB.
4. Open [`main.py`](./main.py) and press **`Ctrl+F5`** (or click **MicroPico: Run current file** in the status bar).
5. The VS Code terminal will output the Pico's IP address:
   ```text
   Connecting to Wi-Fi: MyHomeWiFi ...
   Dashboard ready at http://192.168.1.111
   ```
6. Open that URL on any phone or browser connected to the same Wi-Fi network to view your live climate station!
