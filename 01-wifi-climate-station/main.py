"""
Project 1: Wi-Fi Climate Station with Web Dashboard
Raspberry Pi Pico W + DHT11 + LDR + RGB LED
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

# ----------------- HARDWARE SETUP -----------------
# Onboard LED on Pico W
onboard_led = Pin("LED", Pin.OUT)

# DHT11 Temperature & Humidity Sensor (GP15 / Physical Pin 20)
import dht
dht_pin = Pin(15, Pin.IN, Pin.PULL_UP)
dht_sensor = dht.DHT11(dht_pin)

# Photoresistor / Light Sensor Module (GP26 / ADC0 / Physical Pin 31)
ldr_adc = ADC(Pin(26))

# LDR Calibration Settings:
# Set LDR_PULL_UP = True for standard KY-018 (higher raw ADC in dark, lower in light)
# Set LDR_PULL_UP = False if your sensor outputs higher voltage in light
LDR_PULL_UP = True

# Dynamic auto-ranging state for LDR
ldr_min_seen = None
ldr_max_seen = None

def get_calibrated_light(raw_val):
    """Dynamically calibrate light percentage based on observed min and max."""
    global ldr_min_seen, ldr_max_seen
    
    if ldr_min_seen is None or raw_val < ldr_min_seen:
        ldr_min_seen = raw_val
    if ldr_max_seen is None or raw_val > ldr_max_seen:
        ldr_max_seen = raw_val
        
    span = ldr_max_seen - ldr_min_seen
    if span < 150:
        # Not enough range observed yet, default to mid-scale
        return 50.0
        
    if LDR_PULL_UP:
        # Pull-up: max raw = darkest (0%), min raw = brightest (100%)
        pct = ((ldr_max_seen - raw_val) / span) * 100.0
    else:
        # Pull-down: min raw = darkest (0%), max raw = brightest (100%)
        pct = ((raw_val - ldr_min_seen) / span) * 100.0
        
    return round(max(0.0, min(100.0, pct)), 1)

# RGB LED Pins (GP16, GP17, GP18)
red_pin = Pin(16, Pin.OUT)
green_pin = Pin(17, Pin.OUT)
blue_pin = Pin(18, Pin.OUT)

def set_rgb(r, g, b):
    """Set RGB LED values (1 = ON, 0 = OFF)."""
    red_pin.value(1 if r else 0)
    green_pin.value(1 if g else 0)
    blue_pin.value(1 if b else 0)

# Start with LEDs off
set_rgb(0, 0, 0)

# Cached readings
current_temp = None
current_humidity = None
current_light_pct = 0.0
dht_ok = False
last_sensor_read = 0

def update_sensors():
    """Read DHT11 and LDR sensors safely."""
    global current_temp, current_humidity, current_light_pct, dht_ok, last_sensor_read
    
    # Read at most once every 2.0 seconds (DHT11 datasheet requirement)
    now = time.ticks_ms()
    if time.ticks_diff(now, last_sensor_read) < 2000 and last_sensor_read != 0:
        return
    last_sensor_read = now

    # 1. Read DHT11
    try:
        if hasattr(dht_sensor, 'measure'):
            dht_sensor.measure()
        
        # Compatibility fix: depending on MicroPython build,
        # temperature and humidity may be attributes/properties (floats) or methods
        t = dht_sensor.temperature() if callable(dht_sensor.temperature) else dht_sensor.temperature
        h = dht_sensor.humidity() if callable(dht_sensor.humidity) else dht_sensor.humidity
        
        current_temp = float(t)
        current_humidity = float(h)
        dht_ok = True
    except Exception as e:
        # If we had a prior valid reading, keep it; if never read, dht_ok remains False
        if current_temp is None:
            dht_ok = False

    # 2. Read LDR (16-bit ADC: 0 to 65535)
    raw_val = ldr_adc.read_u16()
    current_light_pct = get_calibrated_light(raw_val)

    # 3. Update RGB LED based on temperature (only if DHT11 is working)
    if dht_ok and current_temp is not None:
        if current_temp < 19:
            set_rgb(0, 0, 1)  # Blue = Cold
        elif current_temp <= 27:
            set_rgb(0, 1, 0)  # Green = Comfortable
        else:
            set_rgb(1, 0, 0)  # Red = Hot
    else:
        set_rgb(0, 0, 0)      # Keep off if sensor is offline

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
            print(".", end="")
        print()

    if wlan.isconnected():
        onboard_led.value(1)
        ip = wlan.ifconfig()[0]
        return ip
    else:
        onboard_led.value(0)
        raise RuntimeError("Failed to connect to Wi-Fi. Check SSID/Password.")

# ----------------- WEB SERVER HTML -----------------
HTML_PAGE = """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Pico W Climate Monitor</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    body { font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif; }
    .num { font-feature-settings: "tnum"; font-variant-numeric: tabular-nums; font-family: 'JetBrains Mono', monospace; }
  </style>
</head>
<body class="bg-[#09090b] text-[#f4f4f5] min-h-screen flex items-center justify-center p-4 antialiased">
  <div class="w-full max-w-md space-y-3.5">
    <!-- Header -->
    <header class="flex items-center justify-between px-1">
      <div class="flex items-center space-x-2.5">
        <div class="w-8 h-8 rounded-lg bg-[#18181b] border border-[#27272a] flex items-center justify-center text-zinc-400">
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z"/></svg>
        </div>
        <div>
          <h1 class="text-xs font-semibold uppercase tracking-wider text-zinc-200">Climate Station</h1>
          <p class="text-[11px] text-zinc-500 font-mono">RP2040 &bull; CYW43439</p>
        </div>
      </div>
      <div class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[11px] font-medium font-mono">
        <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
        <span id="sync-time">LIVE</span>
      </div>
    </header>

    <!-- Main Hero: Temperature -->
    <div class="bg-[#121215] border border-[#27272a] rounded-2xl p-6 relative overflow-hidden">
      <div class="flex justify-between items-start mb-6">
        <div>
          <span class="text-[11px] font-semibold uppercase tracking-widest text-zinc-400">Ambient Temperature</span>
          <p class="text-xs text-zinc-500 mt-0.5">DHT11 Sensor &bull; GP15</p>
        </div>
        <span id="temp-badge" class="px-2 py-0.5 rounded text-[11px] font-medium font-mono bg-zinc-800 text-zinc-300 border border-zinc-700/50">Optimal</span>
      </div>

      <div class="flex items-baseline gap-1">
        <span id="temp" class="num text-6xl font-light tracking-tight text-white">--</span>
        <span class="text-2xl font-light text-zinc-500">&deg;C</span>
      </div>

      <!-- Precision Range Bar -->
      <div class="mt-6 pt-4 border-t border-zinc-800/60">
        <div class="flex justify-between text-[10px] font-mono text-zinc-500 mb-1.5">
          <span>0&deg;C</span>
          <span>Target 21&deg;C</span>
          <span>45&deg;C</span>
        </div>
        <div class="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
          <div id="temp-bar" class="h-full bg-gradient-to-r from-blue-400 via-emerald-400 to-amber-500 rounded-full transition-all duration-500" style="width: 50%;"></div>
        </div>
      </div>
    </div>

    <!-- 2-Column Grid: Humidity & Light -->
    <div class="grid grid-cols-2 gap-3">
      <!-- Humidity Card -->
      <div class="bg-[#121215] border border-[#27272a] rounded-2xl p-5 flex flex-col justify-between">
        <div>
          <div class="flex items-center justify-between text-zinc-400 mb-3">
            <span class="text-[11px] font-semibold uppercase tracking-wider text-zinc-400">Humidity</span>
            <svg class="w-4 h-4 text-blue-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"/></svg>
          </div>
          <div class="flex items-baseline gap-1">
            <span id="humidity" class="num text-3xl font-light text-white">--</span>
            <span class="text-sm text-zinc-500">%</span>
          </div>
        </div>
        <div class="mt-4 pt-3 border-t border-zinc-800/60">
          <div class="h-1 bg-zinc-800 rounded-full overflow-hidden">
            <div id="hum-bar" class="h-full bg-blue-400 rounded-full transition-all duration-500" style="width: 50%;"></div>
          </div>
        </div>
      </div>

      <!-- Light Card -->
      <div class="bg-[#121215] border border-[#27272a] rounded-2xl p-5 flex flex-col justify-between">
        <div>
          <div class="flex items-center justify-between text-zinc-400 mb-3">
            <span class="text-[11px] font-semibold uppercase tracking-wider text-zinc-400">Luminance</span>
            <svg class="w-4 h-4 text-amber-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
          </div>
          <div class="flex items-baseline gap-1">
            <span id="light" class="num text-3xl font-light text-white">--</span>
            <span class="text-sm text-zinc-500">%</span>
          </div>
        </div>
        <div class="mt-4 pt-3 border-t border-zinc-800/60">
          <div id="light-bar" class="h-1 bg-zinc-800 rounded-full overflow-hidden">
            <div id="light-bar-fill" class="h-full bg-amber-400 rounded-full transition-all duration-500" style="width: 50%;"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer metadata -->
    <footer class="flex items-center justify-between px-1 text-[11px] text-zinc-500 font-mono">
      <span>POLL: 2000MS</span>
      <span id="status-label">STATUS: CONNECTED</span>
    </footer>
  </div>

  <script>
    async function refreshData() {
      try {
        const res = await fetch('/api/data');
        const data = await res.json();
        
        const tempEl = document.getElementById('temp');
        const humEl = document.getElementById('humidity');
        const tempBar = document.getElementById('temp-bar');
        const humBar = document.getElementById('hum-bar');
        const badge = document.getElementById('temp-badge');

        if (data.dht_ok && data.temp !== null && data.temp !== undefined) {
          tempEl.innerText = Number(data.temp).toFixed(1);
          humEl.innerText = Math.round(data.humidity);
          tempBar.style.width = Math.min(100, Math.max(0, (data.temp / 45) * 100)) + '%';
          humBar.style.width = Math.min(100, Math.max(0, data.humidity)) + '%';

          if (data.temp < 19) {
            badge.innerText = 'Cold';
            badge.className = 'px-2 py-0.5 rounded text-[11px] font-medium font-mono bg-blue-500/10 text-blue-400 border border-blue-500/20';
          } else if (data.temp <= 26) {
            badge.innerText = 'Optimal';
            badge.className = 'px-2 py-0.5 rounded text-[11px] font-medium font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20';
          } else {
            badge.innerText = 'Warm';
            badge.className = 'px-2 py-0.5 rounded text-[11px] font-medium font-mono bg-amber-500/10 text-amber-400 border border-amber-500/20';
          }
        } else {
          tempEl.innerText = '--';
          humEl.innerText = '--';
          tempBar.style.width = '0%';
          humBar.style.width = '0%';
          badge.innerText = 'Sensor Offline';
          badge.className = 'px-2 py-0.5 rounded text-[11px] font-medium font-mono bg-red-500/10 text-red-400 border border-red-500/20';
        }

        document.getElementById('light').innerText = data.light;
        document.getElementById('light-bar-fill').style.width = Math.min(100, Math.max(0, data.light)) + '%';
        
        const now = new Date();
        document.getElementById('sync-time').innerText = now.toTimeString().split(' ')[0];
        document.getElementById('status-label').innerText = 'STATUS: CONNECTED';
      } catch (err) {
        document.getElementById('status-label').innerText = 'STATUS: RECONNECTING';
      }
    }
    setInterval(refreshData, 2000);
    refreshData();
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
        client.sendall(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nAccess-Control-Allow-Origin: *\r\nConnection: close\r\n\r\n" + body)
    except:
        pass

# ----------------- MAIN SERVER LOOP -----------------
def start_server(ip):
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(4)
    print("Dashboard ready at http://%s" % ip)

    while True:
        try:
            cl, client_addr = s.accept()
            cl.settimeout(3.0)
            try:
                req = cl.recv(1024).decode('utf-8')
                update_sensors()

                if "GET /api/data" in req:
                    send_json(cl, {
                        "temp": current_temp,
                        "humidity": current_humidity,
                        "light": current_light_pct,
                        "dht_ok": dht_ok
                    })
                else:
                    send_html(cl, HTML_PAGE)
            finally:
                cl.close()
        except Exception as e:
            pass

if __name__ == "__main__":
    ip = connect_wifi()
    start_server(ip)
