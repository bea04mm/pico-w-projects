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

## Wiring Diagram

> **Important:** Always wire your sensors with the Pico W **unplugged from USB**.

```
Pico W (Physical Pin #)     ->   Module / Component Pin
----------------------------------------------------------------------------------
Pin 36 (3V3 OUT)            ->   Breadboard Red (+) Power Rail
Pin 38 (GND)                ->   Breadboard Blue (-) Ground Rail

Temp and Humidity Module (DHT11, Row 2, #13):
- 'S' / 'Out' (Signal)      ->   Pico Physical Pin 20 (GP15)
- '+' (Middle pin, VCC)     ->   Breadboard (+) Rail [3.3V]
- '-' (GND)                 ->   Breadboard (-) Rail [GND]

Photoresistor Module (KY-018, Row 3, #22):
- 'S' (Right pin, Signal)   ->   Pico Physical Pin 31 (GP26 / ADC0)
- '+' (Middle pin, VCC)     ->   Breadboard (+) Rail [3.3V]
- '-' (Left pin, GND)       ->   Breadboard (-) Rail [GND]

RGB LED Module (KY-016 Row 5, #41 or KY-009 Row 5, #39):
- '-' (GND)                 ->   Breadboard (-) Rail [GND]
- 'R' (Red)                 ->   Pico Physical Pin 21 (GP16)
- 'G' (Green)               ->   Pico Physical Pin 22 (GP17)
- 'B' (Blue)                ->   Pico Physical Pin 24 (GP18)
```

*(Note: If you use individual discrete LEDs from the starter kit instead of the module, place a 220Ω resistor between each Pico GPIO pin and the LED's longer anode leg, and connect all shorter cathode legs to GND).*

---

## How to Run

1. Open this folder in VS Code with the **MicroPico** extension installed.
2. Ensure your [`secrets.py`](../secrets.py) is configured with your 2.4 GHz Wi-Fi credentials (`WIFI_SSID` and `WIFI_PASSWORD`) and uploaded to the Pico.
3. Plug in your Pico W via USB.
4. Open [`main.py`](./main.py) and press **`Ctrl+F5`** (or click **MicroPico: Run current file** in the status bar).
5. The VS Code terminal will output the Pico's IP address:
   ```
   Connecting to Wi-Fi: MyHomeWiFi ...
   Dashboard ready at http://192.168.1.111
   ```
6. Open that URL in your phone or PC browser to view your live climate station dashboard.
