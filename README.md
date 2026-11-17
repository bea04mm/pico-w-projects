# Raspberry Pi Pico W Projects

A hands-on collection of MicroPython projects for the **Raspberry Pi Pico W**, an **830-point Breadboard Starter Kit**, and the **Hosyond 45-in-1 Sensor Kit V2.0**.

Projects are documented, tested, and published one at a time.

---

## Published Projects

| # | Folder | Project Name | Kit Hardware Used | Description |
| :-: | :--- | :--- | :--- | :--- |
| **01** | [`01-wifi-climate-station`](./01-wifi-climate-station/) | **Wi-Fi Climate Station** | DHT11 Temp/Humidity, Photoresistor (KY-018), RGB LED (KY-016/009) | Interactive live web dashboard with temperature, humidity, ambient light %, and color-coded status. |
| **02** | [`02-security-alarm-system`](./02-security-alarm-system/) | **Security Alarm System** | PIR (HC-SR501) / Shock (KY-002), Active Buzzer (KY-012), Button (KY-004), LEDs | Physical & web arming/disarming, siren alarms, event logs, and optional Discord webhooks. |

*(More projects will be added incrementally).*

---

## Raspberry Pi Pico W Pinout Reference

> **Pro Tip:** In MicroPython, always reference the **GPIO number** (e.g., `machine.Pin(14)` for `GP14`), not the physical board pin number (Pin 19).

![Raspberry Pi Pico W Pinout](https://www.raspberrypi.com/documentation/microcontrollers/images/picow-pinout.svg)

- [Official Raspberry Pi Pico Documentation](https://www.raspberrypi.com/documentation/microcontrollers/raspberry-pi-pico.html)
- [Download High-Resolution Printable Pinout PDF](https://datasheets.raspberrypi.com/picow/PicoW-A4-Pinout.pdf)

---

## Hosyond Kit Pin Conventions (How to Read Module Pins)

Most modules in the Hosyond 45-in-1 kit use standardized 3-pin or 4-pin headers stamped with these markings:

| Pin Marking | Pin Name | Connects To | Usage & Notes |
| :--- | :--- | :--- | :--- |
| **`S`** / `OUT` | Signal / Data | Pico GPIO Pin (e.g. `GP14`, `GP15`) | Digital sensor input, button trigger, or actuator control |
| **`+`** / `VCC` | Power Supply | Breadboard Red Rail (`3.3V`) | 3.3V power bus. ***Exception:*** *HC-SR501 PIR and Relays require 5V from Pico Pin 40 (`VBUS`).* |
| **`-`** / `G` | Ground | Breadboard Blue Rail (`GND`) | Circuit ground reference |
| **`AO`** | Analog Output | Pico ADC Pins (`GP26`, `GP27`, `GP28`) | Continuous analog voltage measurement (0–3.3V) |
| **`DO`** | Digital Output | Any Pico GPIO Pin | High/Low trigger from onboard potentiometer comparator |

---

## Published Projects Pin Connections Summary

| Project | Module / Component | Module Pin Label | Pico W Physical Pin # | Pico W GPIO / Rail | Function |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **01** | DHT11 Temp & Humidity | `S` (Signal) | Pin 20 | `GP15` | Digital temperature & humidity reading |
| **01** | DHT11 Temp & Humidity | `+` (VCC) / `-` (GND) | Pins 36 / 38 | `3V3 OUT` / `GND` | Module power |
| **01** | KY-018 Photoresistor | `S` (Signal) | Pin 31 | `GP26 / ADC0` | Ambient light level analog input |
| **01** | KY-016 / 009 RGB LED | `R`, `G`, `B` | Pins 21, 22, 24 | `GP16`, `GP17`, `GP18` | Status visual feedback |
| **02** | HC-SR501 PIR Motion | `VCC` (Left pin) | Pin 40 | `VBUS (5V USB)` | 5V Power for PIR onboard regulator |
| **02** | HC-SR501 PIR Motion | `OUT` (Center pin) | Pin 19 | `GP14` | Motion detection trigger (3.3V logic) |
| **02** | HC-SR501 PIR Motion | `GND` (Right pin) | Pin 38 | `GND` | Sensor ground |
| **02** | KY-002 Shock Sensor | `S` (Signal) | Pin 19 | `GP14` | Alternative vibration trigger |
| **02** | KY-012 Active Buzzer | `S` (Signal) | Pin 20 | `GP15` | Alarm siren control (HIGH = ON) |
| **02** | KY-004 Push Button | `S` (Signal) | Pin 21 | `GP16` | Hardware arm/disarm toggle |
| **02** | Status LEDs (Green/Red)| Anodes (+) | Pins 22, 24 | `GP17`, `GP18` | Disarmed (Green) / Armed (Red) |

---

## Hosyond 45-in-1 Sensor Kit V2.0 Component Index

This hardware reference documents the sensors, pinouts, and capabilities across the kit. *(Projects will be linked as they are released).*

### Row 1 (Modules 1 – 9)
1. **Linear Hall** (`KY-024`): 4 pins (`AO`, `G`, `+`, `DO`). Measures magnetic field intensity. 3.3V power.
2. **Big Sound**: 4 pins (`AO`, `G`, `+`, `DO`). High sensitivity microphone with onboard LM393 comparator and analog sound envelope.
3. **Magnetic Spring**: 4 pins (`AO`, `G`, `+`, `DO`). Reed switch module triggered by external magnetic fields.
4. **Metal Touch** (`KY-036`): 4 pins (`AO`, `G`, `+`, `DO`). Senses skin touch capacitance.
5. **Digital Temperature** (`KY-028`): 4 pins (`AO`, `G`, `+`, `DO`). NTC thermistor with potentiometer comparator threshold.
6. **Flame** (`KY-026`): 4 pins (`AO`, `G`, `+`, `DO`). 760nm–1100nm infrared flame detector for fire sensing.
7. **Small Sound**: 4 pins (`AO`, `G`, `+`, `DO`). Compact microphone module with adjustable sensitivity threshold.
8. **LCD1602 IIC**: 4 pins (`GND`, `VCC`, `SDA`, `SCL`). 16x2 character alphanumeric LCD with I2C backpack. Connects to GP0 (SDA) and GP1 (SCL).
9. **Water Level Sensor Module**: 3 pins (`+` [3.3V], `-` [GND], `S` [Signal]). Analog immersion and water depth sensor.

### Row 2 (Modules 10 – 18)
10. **Joystick**: 5 pins (`GND`, `+5V` [connect to 3.3V on Pico], `VRX`, `VRY`, `SW`). Dual-axis analog thumbstick with tactile center button.
11. **Relay**: 3 pins (`GND`, `VCC` [Connect to Pin 40 / 5V VBUS], `IN`). 1-channel relay for switching external appliances.
12. **Rotary Encoders** (`KY-040`): 5 pins (`CLK`, `DT`, `SW`, `+`, `GND`). Infinite 360° rotary knob with push button.
13. **Temp and Humidity** (`DHT11`): 3 pins (`+` [3.3V], `out`/`S` [Signal], `-` [GND]). Digital temperature & humidity sensor. *Used in [`01-wifi-climate-station`](./01-wifi-climate-station/)*.
14. **Tracking**: 3 pins (`VCC`, `GND`, `OUT`). Infrared reflectance sensor for black/white line following.
15. **Light Blocking** (`KY-010`): 3 pins (`S`, middle pin, `-`). Slotted optical photo-interrupter.
16. **IR Receiver** (`VS1838B`): 3 pins (`-`, `+`, `S`). Receives 38kHz infrared remote control signals.
17. **Ultrasonic Module** (`HC-SR04`): 4 pins (`VCC` [5V], `Trig`, `Echo` [use voltage divider to 3.3V], `GND`). Distance sensor.
18. **Power Supply Module**: Dual 3.3V / 5V breadboard power regulator module with DC barrel jack and USB port.

### Row 3 (Modules 19 – 27)
19. **Avoidance**: 3/4 pins (`VCC`, `GND`, `OUT`). Active infrared obstacle avoidance sensor.
20. **Analog Temp** (`KY-013`): 3 pins (`S` [Analog], `+` [3.3V], `-` [GND]). NTC thermistor analog bridge.
21. **IR Emission** (`KY-005`): 3 pins (`S` [Signal], middle pin [empty], `-` [GND]). Infrared 38kHz emitter LED.
22. **Photoresistor** (`KY-018`): 3 pins (`S` [Signal], `+` [3.3V], `-` [GND]). Light-dependent resistor (LDR). *Used in [`01-wifi-climate-station`](./01-wifi-climate-station/)*.
23. **7 Color Flash** (`KY-034`): 3 pins (`S`, middle pin, `-`). Auto-cycling color changing LED.
24. **18B20 Temp** (`DS18B20`): 3 pins (`S` [1-Wire Data], `+` [3.3V], `-` [GND]). High-accuracy digital 1-wire thermometer.
25. **Analog Hall** (`KY-035`): 3 pins (`S`, `+`, `-`). Linear analog magnetic field sensor.
26. **Membrane Switch**: 8-pin flat ribbon 4x4 keypad matrix (16 keys).
27. **HC-SR501**: 3 pins (`VCC` [Connect to Pin 40 / 5V VBUS!], `OUT` [3.3V logic], `GND`). Dual-potentiometer PIR pyroelectric motion detector. *Used in [`02-security-alarm-system`](./02-security-alarm-system/)*.

### Row 4 (Modules 28 – 36)
28. **Mini Two-Color** (`KY-029`): 3 pins (`G`, common `-`, `R`). 3mm Red/Green LED. *Used in [`02-security-alarm-system`](./02-security-alarm-system/)*.
29. **Two-Color** (`KY-011`): 3 pins (`G`, common `-`, `R`). 5mm Red/Green LED. *Used in [`02-security-alarm-system`](./02-security-alarm-system/)*.
30. **Light Cup** (`KY-027`): 4 pins (`GND`, `+5V`, `S`, `L`). Magic tilt light cup with mercury switch and LED.
31. **Hydrargyrum-Switch** (`KY-017`): 3 pins (`S`, middle, `-`). Mercury tilt orientation switch.
32. **Mini Reed Switch** (`KY-021`): 3 pins (`S`, middle, `-`). Miniature magnetic reed switch.
33. **Laser Emission** (`KY-008`): 3 pins (`S` [3.3V], middle, `-` [GND]). 650nm red dot laser diode.
34. **Shock** (`KY-002`): 3 pins (`S` [Signal], `+` [3.3V], `-` [GND]). Spring vibration/impact sensor. *Used in [`02-security-alarm-system`](./02-security-alarm-system/)*.
35. **DS3231 RTC Module**: 6 pins (`32K`, `SQW`, `SCL`, `SDA`, `VCC`, `GND`). High-precision real-time clock with battery backup.
36. **GY-521** (`MPU-6050`): 8 pins (`VCC`, `GND`, `SCL`, `SDA`, `XDA`, `XCL`, `AD0`, `INT`). 6-axis accelerometer & gyroscope on I2C.

### Row 5 (Modules 37 – 45)
37. **Button** (`KY-004`): 3 pins (`S` [Signal], `+` [3.3V], `-` [GND]). Tactile push button module. *Used in [`02-security-alarm-system`](./02-security-alarm-system/)*.
38. **Pulse Rate Monitor** (`KY-039`): 3 pins (`S` [Analog], `+`, `-`). Optical photoplethysmogram pulse sensor.
39. **SMD RGB** (`KY-009`): 4 pins (`-` [GND], `R`, `G`, `B`). 5050 SMD full-color LED. *Compatible with [`01-wifi-climate-station`](./01-wifi-climate-station/)*.
40. **TAP Module** (`KY-031`): 3 pins (`S`, middle, `-`). Mechanical tap/knock sensor.
41. **RGB LED** (`KY-016`): 4 pins (`-` [GND], `R`, `G`, `B`). 5mm through-hole full-color LED. *Used in [`01-wifi-climate-station`](./01-wifi-climate-station/)*.
42. **Hall Magnetic** (`KY-003`): 3 pins (`S`, middle, `-`). Digital Hall switch.
43. **Active Buzzer** (`KY-012`): 3 pins (`S`, middle, `-` [GND]). Has internal oscillator (black epoxy base). Makes a constant tone when Pin is HIGH. *Used in [`02-security-alarm-system`](./02-security-alarm-system/)*.
44. **Tilt-Switch** (`KY-020`): 3 pins (`S`, middle, `-`). Metal ball tilt sensor.
45. **Passive Buzzer** (`KY-006`): 3 pins (`S`, middle, `-` [GND]). Has exposed green PCB underside. Requires PWM signal to produce musical tones.

---

## Quick Start Guide

### 1. Configure Secrets
1. Copy [`secrets.example.py`](./secrets.example.py) to a new file named `secrets.py`.
2. Fill in your Wi-Fi credentials (`WIFI_SSID` and `WIFI_PASSWORD`).
3. *(Optional for Project 02)*: Add a `DISCORD_WEBHOOK_URL` if you want instant intrusion alert notifications pushed to Discord (leave empty `""` to run in local-only mode).
4. Upload `secrets.py` to your Pico W using VS Code (**MicroPico** extension -> right-click `secrets.py` -> **Upload file to Pico**).
   *(Note: `secrets.py` is ignored by Git to protect your private credentials).*

### 2. Run with VS Code & MicroPico
1. Plug your Raspberry Pi Pico W into your computer via a micro-USB data cable.
2. Ensure the **MicroPico** extension is connected (status bar indicates `Pico Connected`).
3. Open either project's `main.py` (e.g., [`01-wifi-climate-station/main.py`](./01-wifi-climate-station/main.py) or [`02-security-alarm-system/main.py`](./02-security-alarm-system/main.py)) and press **`Ctrl+F5`** (or click **Run current file**).
4. The Pico will connect to your Wi-Fi network and print its IP address in the terminal. Open that IP address in any browser on the same Wi-Fi network!
