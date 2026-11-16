# Raspberry Pi Pico W Projects

A hands-on collection of MicroPython projects for the **Raspberry Pi Pico W**, an **830-point Breadboard Starter Kit**, and the **Hosyond 45-in-1 Sensor Kit V2.0**.

Projects are documented, tested, and published one at a time.

---

## Published Projects

| # | Folder | Project Name | Kit Hardware Used | Description |
| :-: | :--- | :--- | :--- | :--- |
| **01** | [`01-wifi-climate-station`](./01-wifi-climate-station/) | **Wi-Fi Climate Station** | DHT11 Temp/Humidity, Photoresistor (KY-018), RGB LED (KY-016/009) | Interactive live web dashboard with temperature, humidity, ambient light %, and color-coded status. |

*(More projects will be added incrementally).*

---

## Hardware Modules Used in This Release

- **Temp and Humidity** (`DHT11`, Card Row 2, #13): Digital temperature & humidity sensor. Connects to Pico GP15.
- **Photoresistor** (`KY-018`, Card Row 3, #22): Light-dependent resistor (LDR) for ambient light level measurement. Connects to Pico GP26 (ADC0).
- **RGB LED** (`KY-016` / `KY-009`, Card Row 5, #41 / #39): Status feedback indicator. Connects to GP16 (Red), GP17 (Green), GP18 (Blue).

---

## Raspberry Pi Pico W Pinout Reference

> **Pro Tip:** In MicroPython, always reference the **GPIO number** (e.g., `machine.Pin(15)` for `GP15`), not the physical board pin number (Pin 20).

![Raspberry Pi Pico W Pinout](https://www.raspberrypi.com/documentation/microcontrollers/images/picow-pinout.svg)

- 📖 [Official Raspberry Pi Pico Documentation](https://www.raspberrypi.com/documentation/microcontrollers/raspberry-pi-pico.html)
- 📄 [Download High-Resolution Printable Pinout PDF](https://datasheets.raspberrypi.com/picow/PicoW-A4-Pinout.pdf)


---

## Quick Start Guide

### 1. Configure Secrets
1. Copy [`secrets.example.py`](./secrets.example.py) to a new file named `secrets.py`.
2. Fill in your Wi-Fi credentials (`WIFI_SSID` and `WIFI_PASSWORD`).
3. Upload `secrets.py` to your Pico W using VS Code (**MicroPico** extension -> right-click `secrets.py` -> **Upload file to Pico**).
   *(Note: `secrets.py` is ignored by Git to protect your private credentials).*

### 2. Run with VS Code & MicroPico
1. Plug your Raspberry Pi Pico W into your computer via a micro-USB data cable.
2. Ensure the **MicroPico** extension is connected (status bar indicates `Pico Connected`).
3. Open [`01-wifi-climate-station/main.py`](./01-wifi-climate-station/main.py) and press **`Ctrl+F5`** (or click **Run current file**).
4. The Pico will connect to your Wi-Fi network and print its IP address in the terminal. Open that IP address in any browser on the same Wi-Fi network!
