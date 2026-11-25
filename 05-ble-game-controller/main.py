"""
Project 05: Wireless Gamepad & Media Controller
Raspberry Pi Pico W + Dual-Axis Joystick + Dual Action Buttons
Real-time 2D radar stick positioning, button trigger visualizer, and telemetry hub.
"""

import time
import network
import socket
import json
from machine import Pin, ADC

# Try importing secrets from local directory or Pico root filesystem
try:
    import secrets
except ImportError:
    import sys
    for path in ('', '/', '..'):
        if path not in sys.path:
            sys.path.append(path)
    try:
        import secrets
    except ImportError:
        secrets = None

# ----------------- HARDWARE PINS & CONFIGURATION -----------------
onboard_led = Pin("LED", Pin.OUT)
onboard_led.value(0)

# Hardware Configuration & Inversion Flags
INVERT_X = False      # Set True if X axis is inverted
INVERT_Y = True       # Inverted to match standard forward/up joystick orientation
INVERT_BTN_A = False  # Standard Active-Low (0 = pressed, 1 = released)
INVERT_BTN_B = False  # Set True ONLY if button B is Active-High (1 = pressed, 0 = released)

# 1. Analog Joystick (Row 2, #10)
joy_x = ADC(Pin(26))  # VRx -> GP26 / ADC0 (Pin 31)
joy_y = ADC(Pin(27))  # VRy -> GP27 / ADC1 (Pin 32)
joy_sw = Pin(22, Pin.IN, Pin.PULL_UP)  # SW -> GP22 (Pin 29, Active LOW click)

# 2. Action Buttons (Row 5, #37 / Tactile Buttons)
# Internal pull-up resistors ensure 3.3V (1) at rest and 0V (0) when pressed to GND
btn_a = Pin(15, Pin.IN, Pin.PULL_UP)  # Button A -> GP15 (Pin 20)
btn_b = Pin(14, Pin.IN, Pin.PULL_UP)  # Button B -> GP14 (Pin 19)

time.sleep_ms(50)
print("\n--- Pico W Hardware Pin Diagnostics ---")
print("  Joystick SW (GP22) :", joy_sw.value())
print("  Button A    (GP15) :", btn_a.value())
print("  Button B    (GP14) :", btn_b.value())
print("----------------------------------------\n")

def read_inputs():
    raw_x = joy_x.read_u16()
    raw_y = joy_y.read_u16()

    # Map raw 16-bit ADC (0 - 65535) to normalized -100 to +100
    norm_x = int(((raw_x / 65535.0) * 200.0) - 100.0)
    norm_y = int(((raw_y / 65535.0) * 200.0) - 100.0)

    # Invert axes if flagged
    if INVERT_X:
        norm_x = -norm_x
    if INVERT_Y:
        norm_y = -norm_y

    # Deadzone filter (+/- 6% around center to eliminate analog stick jitter)
    if abs(norm_x) < 6:
        norm_x = 0
    if abs(norm_y) < 6:
        norm_y = 0

    val_sw = joy_sw.value()
    val_a = btn_a.value()
    val_b = btn_b.value()

    # Direct digital logic: Active-Low (0 = pressed, 1 = released)
    sw_clicked = (val_sw == 0)
    btn_a_pressed = (val_a == 1) if INVERT_BTN_A else (val_a == 0)
    btn_b_pressed = (val_b == 1) if INVERT_BTN_B else (val_b == 0)

    # Toggle onboard LED when any input is active
    onboard_led.value(1 if (sw_clicked or btn_a_pressed or btn_b_pressed or norm_x != 0 or norm_y != 0) else 0)

    return {
        "x": norm_x,
        "y": norm_y,
        "sw": sw_clicked,
        "btn_a": btn_a_pressed,
        "btn_b": btn_b_pressed,
        "raw_b": val_b
    }

# ----------------- WEB DASHBOARD -----------------
HTML_PAGE = """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Pico Wireless Gamepad Telemetry</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    body { font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif; }
    .mono { font-family: 'JetBrains Mono', monospace; }
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: #09090b; }
    ::-webkit-scrollbar-thumb { background: #27272a; border-radius: 9999px; }
    ::-webkit-scrollbar-thumb:hover { background: #3f3f46; }
    * { scrollbar-width: thin; scrollbar-color: #27272a #09090b; }
  </style>
</head>
<body class="bg-[#09090b] text-[#f4f4f5] min-h-screen flex items-center justify-center p-4 antialiased">
  <div class="w-full max-w-md space-y-3.5">
    
    <!-- Header -->
    <header class="flex items-center justify-between px-1">
      <div class="flex items-center space-x-2.5">
        <div class="w-8 h-8 rounded-lg bg-[#18181b] border border-[#27272a] flex items-center justify-center text-zinc-400">
          <svg class="w-4 h-4 text-violet-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="6" y1="12" x2="10" y2="12"/><line x1="8" y1="10" x2="8" y2="14"/>
            <line x1="15" y1="13" x2="15.01" y2="13"/><line x1="18" y1="11" x2="18.01" y2="11"/>
            <rect x="2" y="6" width="20" height="12" rx="2"/>
          </svg>
        </div>
        <div>
          <h1 class="text-xs font-semibold uppercase tracking-wider text-zinc-200">Gamepad Telemetry</h1>
          <p class="text-[11px] text-zinc-500 font-mono">Pico W &bull; Dual-Axis ADC Hub</p>
        </div>
      </div>
      <div class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-violet-500/10 border border-violet-500/25 text-violet-400 text-[11px] font-medium font-mono">
        <span class="w-1.5 h-1.5 rounded-full bg-violet-400 animate-pulse"></span>
        <span>LIVE TELEMETRY</span>
      </div>
    </header>

    <!-- Radar Stick Canvas Card -->
    <div class="bg-[#121215] border border-[#27272a] rounded-2xl p-6 text-center shadow-xl">
      <div class="flex justify-between items-center text-zinc-400 mb-2">
        <span class="text-[11px] font-semibold uppercase tracking-wider">Analog Stick Vector</span>
        <span id="coords" class="text-[11px] font-mono text-zinc-400 font-semibold">X: 0 | Y: 0</span>
      </div>
      
      <canvas id="canvas" width="220" height="220" class="mx-auto block rounded-full my-3 border border-zinc-800 shadow-inner"></canvas>

      <!-- Action Buttons Status -->
      <div class="flex justify-center gap-2 pt-3">
        <span id="btn-sw" class="px-3 py-1.5 rounded-xl text-xs font-mono border transition-all bg-[#18181b] border-zinc-800 text-zinc-500">Thumb Click</span>
        <span id="btn-a" class="px-3 py-1.5 rounded-xl text-xs font-mono border transition-all bg-[#18181b] border-zinc-800 text-zinc-500">Button A (GP15)</span>
        <span id="btn-b" class="px-3 py-1.5 rounded-xl text-xs font-mono border transition-all bg-[#18181b] border-zinc-800 text-zinc-500">Button B (GP14)</span>
      </div>
      <div class="mt-2.5">
        <button type="button" onclick="toggleBInvert()" class="text-[11px] font-mono text-zinc-500 hover:text-zinc-300 transition-colors">
          Button B Mode: <span id="b-mode-text" class="text-violet-400">Active-Low (Pin=0)</span> &bull; <span class="underline">Click to Flip</span>
        </button>
      </div>
    </div>

    <!-- Pinout Quick Reference Footer -->
    <footer class="px-2 pt-1 pb-2 text-[11px] text-zinc-500 flex justify-between items-center font-mono">
      <span>X: GP26 &bull; Y: GP27</span>
      <span>SW: GP22 &bull; A: GP15 &bull; B: GP14</span>
    </footer>

  </div>

  <script>
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');
    const center = 110;
    const maxRadius = 88;
    let isFetching = false;
    let bInverted = false;

    function toggleBInvert() {
      bInverted = !bInverted;
      document.getElementById('b-mode-text').innerText = bInverted ? 'Active-High (Pin=1)' : 'Active-Low (Pin=0)';
    }

    async function pollInputs() {
      if (isFetching) return;
      isFetching = true;
      try {
        const res = await fetch('/api/inputs');
        const d = await res.json();

        // Clear canvas background
        ctx.fillStyle = '#18181b';
        ctx.fillRect(0, 0, 220, 220);
        
        // Concentric guide rings
        ctx.strokeStyle = '#27272a';
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.arc(center, center, maxRadius, 0, Math.PI * 2);
        ctx.stroke();

        ctx.strokeStyle = '#222226';
        ctx.beginPath();
        ctx.arc(center, center, maxRadius * 0.5, 0, Math.PI * 2);
        ctx.stroke();

        // Crosshairs
        ctx.strokeStyle = '#27272a';
        ctx.beginPath();
        ctx.moveTo(center, 22); ctx.lineTo(center, 198);
        ctx.moveTo(22, center); ctx.lineTo(198, center);
        ctx.stroke();

        // Target thumb position
        const posX = center + (d.x / 100) * maxRadius;
        const posY = center - (d.y / 100) * maxRadius;

        // Stick head
        const activeColor = d.sw ? '#ef4444' : '#8b5cf6';
        ctx.fillStyle = activeColor;
        ctx.shadowColor = activeColor;
        ctx.shadowBlur = d.sw ? 16 : 8;
        ctx.beginPath();
        ctx.arc(posX, posY, 13, 0, Math.PI * 2);
        ctx.fill();
        ctx.shadowBlur = 0;

        // Numeric coordinates
        document.getElementById('coords').innerText = 'X: ' + d.x + ' | Y: ' + d.y;

        // Button Badges
        const btnSw = document.getElementById('btn-sw');
        btnSw.className = d.sw 
          ? 'px-3 py-1.5 rounded-xl text-xs font-mono border bg-rose-500/10 border-rose-500/30 text-rose-400 font-semibold' 
          : 'px-3 py-1.5 rounded-xl text-xs font-mono border bg-[#18181b] border-zinc-800 text-zinc-500';

        const btnA = document.getElementById('btn-a');
        btnA.className = d.btn_a 
          ? 'px-3 py-1.5 rounded-xl text-xs font-mono border bg-green-500/10 border-green-500/30 text-green-400 font-semibold' 
          : 'px-3 py-1.5 rounded-xl text-xs font-mono border bg-[#18181b] border-zinc-800 text-zinc-500';

        const isBActive = bInverted ? (d.raw_b === 1) : (d.raw_b === 0);
        const btnB = document.getElementById('btn-b');
        btnB.innerText = 'Button B (GP14) [' + d.raw_b + ']';
        btnB.className = isBActive 
          ? 'px-3 py-1.5 rounded-xl text-xs font-mono border bg-violet-500/10 border-violet-500/30 text-violet-400 font-semibold' 
          : 'px-3 py-1.5 rounded-xl text-xs font-mono border bg-[#18181b] border-zinc-800 text-zinc-500';

      } catch (e) {
      } finally {
        isFetching = false;
      }
    }

      } catch (e) {
      } finally {
        isFetching = false;
      }
    }

    setInterval(pollInputs, 80);
  </script>
</body>
</html>
"""

# ----------------- HTTP SERVER & CLI -----------------
def send_html(client, html):
    try:
        client.sendall(b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n")
        data = html.encode('utf-8')
        for i in range(0, len(data), 1024):
            client.sendall(data[i:i + 1024])
    except Exception:
        pass

def send_json(client, obj):
    try:
        body = json.dumps(obj).encode('utf-8')
        client.sendall(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nConnection: close\r\n\r\n" + body)
    except Exception:
        pass

def start_visualizer():
    if not secrets or not hasattr(secrets, 'WIFI_SSID') or not secrets.WIFI_SSID:
        print("Running in offline console mode. Move joystick or press buttons to test:")
        while True:
            data = read_inputs()
            print("X: %4d | Y: %4d | Thumb: %d | Btn A: %d | Btn B: %d" % 
                  (data['x'], data['y'], data['sw'], data['btn_a'], data['btn_b']))
            time.sleep(0.1)

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to Wi-Fi: %s ..." % secrets.WIFI_SSID)
        wlan.connect(secrets.WIFI_SSID, secrets.WIFI_PASSWORD)
        timeout = 20
        while not wlan.isconnected() and timeout > 0:
            onboard_led.toggle()
            time.sleep(0.5)
            timeout -= 1
    
    if wlan.isconnected():
        ip = wlan.ifconfig()[0]
        print("Dashboard ready at http://%s" % ip)
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('0.0.0.0', 80))
        s.listen(3)

        while True:
            try:
                cl, _ = s.accept()
                cl.settimeout(2.0)
                try:
                    req = cl.recv(1024).decode('utf-8')
                    if "GET /api/inputs" in req:
                        send_json(cl, read_inputs())
                    else:
                        send_html(cl, HTML_PAGE)
                finally:
                    cl.close()
            except Exception:
                pass
    else:
        print("Wi-Fi connection failed. Falling back to offline console mode:")
        while True:
            data = read_inputs()
            print("X: %4d | Y: %4d | Thumb: %d | Btn A: %d | Btn B: %d" % 
                  (data['x'], data['y'], data['sw'], data['btn_a'], data['btn_b']))
            time.sleep(0.1)

if __name__ == "__main__":
    start_visualizer()
