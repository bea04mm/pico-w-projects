# Project 04: Universal Smart IR Remote with Web Interface

A web-controlled infrared remote control station that learns signals from any household remote (TV, soundbar, air conditioner, fan) and re-transmits them on demand via an onboard 38kHz PWM carrier blaster.

Recorded remote codes are persisted directly to the Pico W flash filesystem (`ir_codes.json`), surviving power cycles and resets.

---

## Parts Required

From your **Hosyond 45-in-1 Kit** & **Starter Kit**:
1. **Raspberry Pi Pico W**
2. **830-Point Breadboard**
3. **IR Receiver Sensor Module** (Kit Card: Row 2, #16 — metal-shielded VS1838B sensor)
4. **IR Emission Module** (Kit Card: Row 3, #21, KY-005 — 940nm infrared transmitter LED)
5. **Jumper Wires**

---

## Pin Connections & Wiring Guide

> **Important:** Always connect wires while your Raspberry Pi Pico W is **unplugged from USB**.

### 1. Power Distribution
| From Pico W Pin | Label | Wire To | Purpose |
| :--- | :--- | :--- | :--- |
| **Pin 36** | `3V3 OUT` | Breadboard Red (+) Power Rail | Main 3.3V power bus for receiver and transmitter |
| **Pin 38** | `GND` | Breadboard Blue (-) Ground Rail | Common circuit ground reference |

---

### 2. Sensor & Blaster Connections

#### IR Receiver Sensor Module (`VS1838B`, Row 2, #16)
*(The sensor is equipped with an integrated 38kHz band-pass filter and active-low demodulator).*
| PCB Pin Label | Physical Position | Connects To | Pico W Pin Details | Function |
| :--- | :--- | :--- | :--- | :--- |
| **`-`** (or `G`) | Left pin | Breadboard Blue (-) Rail | `Common GND` | Ground |
| **`+`** (or `VCC`) | Middle pin | Breadboard Red (+) Rail | `3.3V Power` | Module power supply |
| **`S`** (or `OUT`) | Right pin | **Pico Physical Pin 20** | **`GP15`** | Demodulated digital IR input (Active LOW) |

#### IR Emission Module (`KY-005`, Row 3, #21)
*(Infrared transmitting LED board for 38kHz carrier signal emission).*
| PCB Pin Label | Physical Position | Connects To | Pico W Pin Details | Function |
| :--- | :--- | :--- | :--- | :--- |
| **`S`** | Signal pin | **Pico Physical Pin 21** | **`GP16`** | 38kHz PWM carrier modulation output |
| *(Middle)* | Center pin | *Leave unconnected (NC)* | *Not connected* | Unused pin on standard KY-005 breakout |
| **`-`** | Ground pin | Breadboard Blue (-) Rail | `Common GND` | Ground return |

---

### 3. Circuit Wiring Summary

| Module | Pin Label | Breadboard / Pico W Connection | Physical Pin # | GPIO / Function |
| :--- | :--- | :--- | :--- | :--- |
| **Pico W** | `3V3 OUT` | Breadboard Red (+) Rail | Pin 36 | 3.3V System Power |
| **Pico W** | `GND` | Breadboard Blue (-) Rail | Pin 38 | System Ground |
| **VS1838B Receiver** | `-` | Breadboard Blue (-) Rail | -- | Ground |
| **VS1838B Receiver** | `+` | Breadboard Red (+) Rail | -- | 3.3V VCC |
| **VS1838B Receiver** | `S` | Pico W GP15 | Pin 20 | Digital In (Pull-up) |
| **KY-005 Transmitter** | `S` | Pico W GP16 | Pin 21 | PWM Output (38kHz) |
| **KY-005 Transmitter** | `-` | Breadboard Blue (-) Rail | -- | Ground |

---

## How It Works

1. **38kHz Carrier Demodulation (Receiver):**  
   Consumer remote controls modulate infrared light at a 38kHz carrier frequency to differentiate commands from ambient room lighting. The VS1838B receiver detects these 38kHz bursts and outputs a digital LOW (`0`) during bursts and HIGH (`1`) during silence.
2. **Pulse-Duration Timing:**  
   When recording, the Pico W measures the duration of each HIGH and LOW pulse in microseconds with microsecond accuracy. A silent period exceeding 25 milliseconds marks the completion of the transmission packet.
3. **PWM Carrier Generation (Transmitter):**  
   To replay the code, hardware PWM on `GP16` generates a precise 38kHz square wave with a 33.3% duty cycle. The code toggles this carrier on and off according to the recorded pulse array.
4. **Persistent JSON Storage:**  
   Learned commands are saved to `ir_codes.json` in the Pico's onboard flash memory, ensuring your custom remote mappings remain intact across reboots.

---

## How to Run

### 1. Prerequisites
Ensure your Wi-Fi credentials are set in `secrets.py` at the root of the project or inside this folder:
```python
WIFI_SSID = "YOUR_WIFI_NAME"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"
```

### 2. Upload and Execute
1. Connect your Pico W to your computer using a micro-USB cable.
2. In VS Code, verify the **MicroPico** extension shows `Pico Connected`.
3. Open [`04-universal-ir-remote/main.py`](./main.py) and press **`Ctrl+F5`** (or click **Run current file** in MicroPico).
4. The console will display the assigned local IP address:
   ```
   Connecting to Wi-Fi: YourNetwork ...
   Dashboard ready at http://192.168.1.xxx
   ```
5. Open that URL on your smartphone, tablet, or desktop browser.

---

## Web Dashboard Features

- **Signal Capture:** Enter a descriptive command name (e.g., `TV_Power`, `Mute`, `HDMI_1`) and click **Record**. The onboard LED lights up, and the Pico listens for 5 seconds. Press the target button on your remote while pointing at the VS1838B module.
- **Transmit Command:** Click **Send** next to any saved command to trigger the 38kHz IR blaster.
- **Delete Command:** Click the trash icon next to a command to remove it from memory and flash storage.
- **Built-in Sample:** Includes a standard NEC Power Toggle code preloaded for initial verification.

---

## Troubleshooting

- **Checking the IR LED Output:** Human eyes cannot see 940nm infrared light. Open your smartphone camera (especially the front-facing selfie camera, which usually lacks an aggressive IR-blocking filter), point it directly at the KY-005 LED, and click **Send** on the web page. You will see a purplish-white flash when the transmitter fires.
- **Failed Capture:** Ensure the remote is pointed directly at the black dome of the VS1838B sensor from a distance of 5 cm to 30 cm. Avoid bright direct sunlight or high-intensity fluorescent lighting directly hitting the sensor.
- **Code Repeats:** Consumer remotes send continuous repeat pulses if held down. Tap the remote button quickly and release it immediately during capture.
