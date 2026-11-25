# Project 05: Wireless Gamepad & Media Controller

Turn your Raspberry Pi Pico W, Dual-Axis Analog Joystick, and Action Buttons into a responsive wireless controller with real-time 2D radar stick positioning and button telemetry.

The system samples dual 16-bit analog channels (`GP26` and `GP27`), applies deadzone filtering to prevent stick drift, and serves an interactive 60FPS dark-theme canvas dashboard over your local Wi-Fi network.

---

## Parts Required

From your **Hosyond 45-in-1 Kit** & **Starter Kit**:
1. **Raspberry Pi Pico W**
2. **830-Point Breadboard**
3. **Joystick Module** (Kit Card: Row 2, #10 — dual-axis thumbstick with integrated tactile push switch)
4. **Push Buttons**: Hosyond **Button Module** (Kit Card: Row 5, #37, KY-004) and/or tactile push buttons from starter kit
5. **Jumper Wires**

---

## Pin Connections & Wiring Guide

> **Important:** Always wire your circuit with the Raspberry Pi Pico W **unplugged from USB**.

### 1. Power Distribution
| From Pico W Pin | Label | Wire To | Purpose |
| :--- | :--- | :--- | :--- |
| **Pin 36** | `3V3 OUT` | Breadboard Red (+) Rail | 3.3V Power Bus for Joystick and Buttons |
| **Pin 38** | `GND` | Breadboard Blue (-) Rail | Common Circuit Ground |

---

### 2. Sensor & Control Connections

#### Dual-Axis Joystick Module (Row 2, #10)
*(The module combines two 10k potentiometers for X and Y axes plus an integrated tactile push switch).*
| PCB Pin Label | Physical Position | Connects To | Pico W Pin Details | Function |
| :--- | :--- | :--- | :--- | :--- |
| **`GND`** | Pin 1 | Breadboard Blue (-) Rail | `Common GND` | Ground reference |
| **`+5V`** | Pin 2 | Breadboard Red (+) Rail | `3.3V Power` | Analog supply (connect to 3.3V on Pico) |
| **`VRx`** | Pin 3 | **Pico Physical Pin 31** | **`GP26 / ADC0`** | X-Axis horizontal analog input (0–65535) |
| **`VRy`** | Pin 4 | **Pico Physical Pin 32** | **`GP27 / ADC1`** | Y-Axis vertical analog input (0–65535) |
| **`SW`** | Pin 5 | **Pico Physical Pin 29** | **`GP22`** | Thumbstick center click button (Active LOW) |

#### Action Buttons (Button A & Button B)

The project uses two action buttons: **Button A** (`GP15`) and **Button B** (`GP14`).
Because the Hosyond 45-in-1 kit contains 1x Button Module (`KY-004`), you can combine the module with one bare 4-pin tactile button from your breadboard starter kit (or use two bare tactile buttons).

Both pins use the RP2040's internal pull-up resistor (`Pin.PULL_UP`), so **no external resistors are required**. Pressing either button pulls the GPIO line to Ground (`0V`).

##### Option 1: 1x KY-004 Module (Button A) + 1x Bare Tactile Button (Button B) — Recommended

| Component | Physical Pin / Leg | Connects To | Pico W Pin Details | Function |
| :--- | :--- | :--- | :--- | :--- |
| **Button A (KY-004 Module)** | Signal (`S`) | **Pico Physical Pin 20** | **`GP15`** | Primary Action (Fire / Select) |
| **Button A (KY-004 Module)** | Ground (`-`) | Breadboard Blue (-) Rail | `Common GND` | Ground return |
| **Button A (KY-004 Module)** | Middle pin | *Leave unconnected* | -- | Not needed |
| **Button B (Bare 4-Pin Button)** | Top Leg (Side 1) | **Pico Physical Pin 19** | **`GP14`** | Secondary Action (Jump / Back) |
| **Button B (Bare 4-Pin Button)** | Bottom Leg (Side 2) | Breadboard Blue (-) Rail | `Common GND` | Ground return |

##### How to Wire the Bare 4-Pin Tactile Button on an 830-Point Breadboard:
1. **Mounting:** Push the 4-pin button so it **straddles the center divider (trough)** between row `e` and row `f` of your breadboard. Two legs sit on the top side of the trough, and two legs sit on the bottom side.
2. **Signal Wire:** Plug a jumper wire into the breadboard hole directly next to one of the top legs, and connect it to **Pico Pin 20 (`GP15`)** or **Pico Pin 19 (`GP14`)**.
3. **Ground Wire:** Plug a second jumper wire into the hole directly next to one of the bottom legs (across the trough), and connect it to the **Breadboard Blue (-) GND Rail**.
4. When pressed, the internal metal dome bridges the top and bottom contacts, pulling the GPIO to 0V.

##### Option 2: Using Two Bare 4-Pin Tactile Buttons
If you prefer matching buttons on your breadboard:
- Mount both buttons straddling the center trough.
- Button A: One leg to **`GP15` (Pin 20)**, opposite leg to **Blue (-) GND Rail**.
- Button B: One leg to **`GP14` (Pin 19)**, opposite leg to **Blue (-) GND Rail**.

---

### 3. Circuit Wiring Summary

| Module | Pin Label | Breadboard / Pico W Connection | Physical Pin # | GPIO / Function |
| :--- | :--- | :--- | :--- | :--- |
| **Pico W** | `3V3 OUT` | Breadboard Red (+) Rail | Pin 36 | 3.3V Power Bus |
| **Pico W** | `GND` | Breadboard Blue (-) Rail | Pin 38 | System Ground |
| **Joystick** | `GND` | Breadboard Blue (-) Rail | -- | Ground |
| **Joystick** | `+5V` | Breadboard Red (+) Rail | -- | 3.3V Reference |
| **Joystick** | `VRx` | Pico Pin 31 | Pin 31 | `GP26 / ADC0` |
| **Joystick** | `VRy` | Pico Pin 32 | Pin 32 | `GP27 / ADC1` |
| **Joystick** | `SW` | Pico Pin 29 | Pin 29 | `GP22` (Thumb click) |
| **Button A** | `S` / Leg 1 | Pico Pin 20 | Pin 20 | `GP15` (Action A) |
| **Button B** | `S` / Leg 1 | Pico Pin 19 | Pin 19 | `GP14` (Action B) |

---

## How It Works

1. **Dual 16-Bit Analog Sampling:**  
   The RP2040 analog-to-digital converter reads voltage levels from `0V` to `3.3V` as a 16-bit integer (`0` to `65535`) on `GP26` (X) and `GP27` (Y).
2. **Normalized Coordinates (-100 to +100):**  
   The raw values are mapped so that the resting center sits at `(0, 0)`. Moving the stick pushed fully left/down yields `-100`, while fully right/up yields `+100`.
3. **Deadzone Filtering:**  
   Potentiometers naturally suffer from tiny mechanical fluctuations around center. A configurable 6% deadzone filter zeroes out jitter when the stick is untouched.
4. **Boot-Time Resting State Calibration:**  
   The firmware auto-detects button resting states at boot time, ensuring reliable trigger detection whether your buttons switch to GND or 3.3V.
5. **Real-Time 2D Radar Canvas:**  
   The web dashboard utilizes an HTML5 canvas element with smooth guide rings, crosshairs, and dynamic glow shadows that track stick movements at 60FPS.

---

## How to Run

### 1. Configure Secrets
Ensure your Wi-Fi credentials are set in `secrets.py` at the root of the repository:
```python
WIFI_SSID = "YOUR_WIFI_NAME"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"
```
*(If no Wi-Fi credentials are provided, the script automatically falls back to an offline serial console mode, streaming coordinates directly to your terminal).*

### 2. Upload and Run
1. Connect your Pico W to your computer using a micro-USB cable.
2. In VS Code, verify the **MicroPico** extension reports `Pico Connected`.
3. Open [`05-ble-game-controller/main.py`](./main.py) and press **`Ctrl+F5`** (or click **Run current file** in MicroPico).
4. The terminal will output the local IP address:
   ```
   Connecting to Wi-Fi: YourNetwork ...
   Dashboard ready at http://192.168.1.xxx
   ```
5. Open `http://192.168.1.xxx` in your browser to view the live radar stick telemetry and button triggers.

---

## Troubleshooting

- **Stick drift or off-center resting values:**  
  If the visualizer dot rests slightly off-center when untouched, increase the deadzone threshold in `main.py` from `6` to `10`:
  ```python
  if abs(norm_x) < 10: norm_x = 0
  if abs(norm_y) < 10: norm_y = 0
  ```
- **Inverted X or Y Axis:**  
  Depending on physical joystick orientation on your breadboard, swap `norm_x = -norm_x` or `norm_y = -norm_y` in `read_inputs()`.
- **Button not registering:**  
  Verify that the button's ground wire connects to the Blue (-) Rail.
