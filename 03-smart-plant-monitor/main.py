"""
Project 3: Smart Plant Monitor with Web Calibration Threshold
Raspberry Pi Pico W + Hosyond Water Lever Detection Sensor Module + LEDs + Buzzer
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
        raise RuntimeError(
            "Could not find secrets.py on the Pico!\n"
            "In VS Code Explorer, right-click secrets.py and click 'Upload file to Pico'."
        )

# ----------------- HARDWARE PINS -----------------
onboard_led = Pin("LED", Pin.OUT)

# ADC0 (GP26) for Soil Moisture Sensor
soil_adc = ADC(Pin(26))

# LEDs
led_green = Pin(16, Pin.OUT)  # Wet / Healthy
led_yellow = Pin(17, Pin.OUT) # Normal / Moderate
led_red = Pin(18, Pin.OUT)    # Dry / Alert

# Buzzer Module Configuration (Active-High: 1 = sound, 0 = silent)
BUZZER_ACTIVE_LOW = False
buzzer = Pin(19, Pin.OUT)
buzzer.value(0)

def chirp(duration_ms=40):
    buzzer.value(1)
    time.sleep_ms(duration_ms)
    buzzer.value(0)

# Current readings and calibration constants
# In dry air, typical raw ADC is ~500 to 1000.
# In a cup of tap water, typical raw ADC at 3.3V is ~22000 to 26000.
CAL_DRY = 800
CAL_WET = 25000

current_raw_adc = 0
current_moisture_pct = 0.0
current_threshold_pct = 30.0

def read_sensors():
    global current_moisture_pct, current_threshold_pct, current_raw_adc, CAL_WET
    
    current_raw_adc = soil_adc.read_u16()
    
    # Auto-adjust wet ceiling if higher conductivity water is detected
    if current_raw_adc > CAL_WET:
        CAL_WET = current_raw_adc

    clamped = max(CAL_DRY, min(CAL_WET, current_raw_adc))
    moisture = ((clamped - CAL_DRY) / (CAL_WET - CAL_DRY)) * 100.0
    current_moisture_pct = round(moisture, 1)

    # LED and Buzzer decision
    if current_moisture_pct < current_threshold_pct:
        # Critically dry
        led_green.value(0)
        led_yellow.value(0)
        led_red.value(1)
        # Short chirp
        chirp(40)
    elif current_moisture_pct < (current_threshold_pct + 20):
        # Getting low
        led_green.value(0)
        led_yellow.value(1)
        led_red.value(0)
    else:
        # Healthy
        led_green.value(1)
        led_yellow.value(0)
        led_red.value(0)

# ----------------- WI-FI CONNECTION -----------------
def connect_wifi():
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
        onboard_led.value(1)
        ip = wlan.ifconfig()[0]
        print("Plant Monitor online at http://%s" % ip)
        return ip
    raise RuntimeError("Wi-Fi failed")

# ----------------- WEB DASHBOARD -----------------
HTML_PAGE = """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Pico Plant Hydration Monitor</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    body { font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif; }
    .num { font-feature-settings: "tnum"; font-variant-numeric: tabular-nums; font-family: 'JetBrains Mono', monospace; }
    /* Modern sleek custom dark scrollbar */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #27272a; border-radius: 9999px; }
    ::-webkit-scrollbar-thumb:hover { background: #3f3f46; }
    * { scrollbar-width: thin; scrollbar-color: #27272a transparent; }
  </style>
</head>
<body class="bg-[#09090b] text-[#f4f4f5] min-h-screen flex items-center justify-center p-4 antialiased">
  <div class="w-full max-w-md space-y-3.5">
    <!-- Header -->
    <header class="flex items-center justify-between px-1">
      <div class="flex items-center space-x-2.5">
        <div class="w-8 h-8 rounded-lg bg-[#18181b] border border-[#27272a] flex items-center justify-center text-zinc-400">
          <svg class="w-4 h-4 text-green-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/></svg>
        </div>
        <div>
          <h1 class="text-xs font-semibold uppercase tracking-wider text-zinc-200">Flora Hydration</h1>
          <p class="text-[11px] text-zinc-500 font-mono">ADC0 &bull; GP26</p>
        </div>
      </div>
      <div id="status-pill" class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-green-500/10 border border-green-500/25 text-green-400 text-[11px] font-medium font-mono">
        <span class="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse"></span>
        <span id="plant-state">HYDRATED</span>
      </div>
    </header>

    <!-- Main Moisture Metric -->
    <div class="bg-[#121215] border border-[#27272a] rounded-2xl p-6 relative overflow-hidden">
      <div class="flex justify-between items-start mb-4">
        <div>
          <span class="text-[11px] font-semibold uppercase tracking-widest text-zinc-400">Soil Moisture</span>
          <p class="text-xs text-zinc-500 mt-0.5 font-mono">Raw ADC: <span id="raw-val">--</span> &bull; Calibrated</p>
        </div>
        <span id="delta-pill" class="px-2 py-0.5 rounded text-[11px] font-medium font-mono bg-green-500/10 text-green-400 border border-green-500/25">+12% over thresh</span>
      </div>

      <div class="flex items-baseline gap-1 my-2">
        <span id="moist-val" class="num text-6xl font-light tracking-tight text-white">--</span>
        <span class="text-2xl font-light text-zinc-500">%</span>
      </div>

      <div class="mt-6 pt-4 border-t border-zinc-800/60">
        <div class="flex justify-between text-[10px] font-mono text-zinc-500 mb-1.5">
          <span>Dry (0%)</span>
          <span id="bar-midpoint">Threshold</span>
          <span>Saturated (100%)</span>
        </div>
        <div class="h-2 bg-zinc-800 rounded-full overflow-hidden relative">
          <div id="thresh-line" class="absolute top-0 bottom-0 w-0.5 bg-amber-400 z-10" style="left: 30%;"></div>
          <div id="moist-bar" class="h-full bg-gradient-to-r from-green-500 to-cyan-400 rounded-full transition-all duration-500" style="width: 50%;"></div>
        </div>
      </div>
    </div>

    <!-- Threshold Adjustment Card -->
    <div class="bg-[#121215] border border-[#27272a] rounded-2xl p-5">
      <div class="flex items-center justify-between mb-3">
        <div class="flex items-center gap-2">
          <svg class="w-4 h-4 text-amber-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
          <span class="text-[11px] font-semibold uppercase tracking-wider text-zinc-400">Moisture Threshold</span>
        </div>
        <span id="thresh-val" class="num text-sm font-medium text-amber-400 font-mono">30%</span>
      </div>
      <input id="thresh-slider" type="range" min="10" max="80" value="30" oninput="setThreshold(this.value)" class="w-full accent-amber-400 bg-zinc-800 rounded-lg cursor-pointer h-2">
      <div class="flex justify-between text-[10px] font-mono text-zinc-500 mt-2">
        <span>Dry (10%)</span>
        <span>Default (30%)</span>
        <span>Wet (80%)</span>
      </div>
    </div>
  </div>

  <script>
    let isUserSliding = false;
    async function setThreshold(val) {
      isUserSliding = true;
      document.getElementById('thresh-val').innerText = val + '%';
      document.getElementById('thresh-line').style.left = val + '%';
      await fetch('/api/threshold?val=' + val);
      setTimeout(() => { isUserSliding = false; }, 2000);
    }

    async function update() {
      try {
        const r = await fetch('/api/data');
        const d = await r.json();
        document.getElementById('moist-val').innerText = d.moisture;
        document.getElementById('thresh-val').innerText = d.threshold + '%';
        if (d.raw !== undefined) {
          document.getElementById('raw-val').innerText = d.raw;
        }
        if (!isUserSliding) {
          document.getElementById('thresh-slider').value = d.threshold;
        }
        document.getElementById('moist-bar').style.width = Math.min(100, Math.max(0, d.moisture)) + '%';
        document.getElementById('thresh-line').style.left = Math.min(100, Math.max(0, d.threshold)) + '%';
        
        const pill = document.getElementById('status-pill');
        const stateText = document.getElementById('plant-state');
        const delta = document.getElementById('delta-pill');
        const diff = (d.moisture - d.threshold).toFixed(1);

        if (d.moisture < d.threshold) {
          stateText.innerText = 'NEEDS WATER';
          pill.className = 'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-rose-500/10 border border-rose-500/20 text-rose-400 text-[11px] font-medium font-mono';
          delta.innerText = Math.abs(diff) + '% below thresh';
          delta.className = 'px-2 py-0.5 rounded text-[11px] font-medium font-mono bg-rose-500/10 text-rose-400 border border-rose-500/20';
        } else {
          stateText.innerText = 'HYDRATED';
          pill.className = 'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-green-500/10 border border-green-500/25 text-green-400 text-[11px] font-medium font-mono';
          delta.innerText = '+' + diff + '% over thresh';
          delta.className = 'px-2 py-0.5 rounded text-[11px] font-medium font-mono bg-green-500/10 text-green-400 border border-green-500/25';
        }
      } catch (e) {}
    }
    setInterval(update, 1500);
    update();
  </script>
</body>
</html>
"""

# ----------------- HTTP RESPONSE HELPERS -----------------
def send_html(client, html):
    try:
        client.sendall(b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n")
        data = html.encode('utf-8')
        for i in range(0, len(data), 1024):
            client.sendall(data[i:i + 1024])
    except:
        pass

def send_json(client, obj):
    try:
        body = json.dumps(obj).encode('utf-8')
        client.sendall(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nConnection: close\r\n\r\n" + body)
    except:
        pass

def start_server(ip):
    global current_threshold_pct
    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', 80))
    server.listen(3)
    server.settimeout(0.5)

    last_sensor_time = 0
    read_sensors()

    while True:
        now = time.ticks_ms()
        if time.ticks_diff(now, last_sensor_time) > 1000:
            last_sensor_time = now
            read_sensors()

        try:
            cl, _ = server.accept()
            cl.settimeout(3.0)
            try:
                req = cl.recv(1024).decode('utf-8')
                if "GET /api/data" in req:
                    send_json(cl, {
                        "moisture": current_moisture_pct,
                        "threshold": current_threshold_pct,
                        "raw": current_raw_adc
                    })
                elif "GET /api/threshold?val=" in req:
                    try:
                        val = float(req.split("val=")[1].split(" ")[0])
                        current_threshold_pct = max(5.0, min(95.0, val))
                    except:
                        pass
                    send_json(cl, {"ok": True, "threshold": current_threshold_pct})
                else:
                    send_html(cl, HTML_PAGE)
            finally:
                cl.close()
        except OSError:
            pass

if __name__ == "__main__":
    ip = connect_wifi()
    start_server(ip)
