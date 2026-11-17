"""
Project 2: Security & Intrusion Alarm System
Raspberry Pi Pico W + PIR / Vibration Sensor + Buzzer + Arming Button + LEDs
"""

import time
import network
import socket
import json
import urequests
from machine import Pin

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

# Sensor input (PIR or Vibration sensor)
sensor_pin = Pin(14, Pin.IN, Pin.PULL_DOWN)

# Active Buzzer Module (Active-High: 1 = sound, 0 = silent)
BUZZER_ACTIVE_LOW = False
buzzer = Pin(15, Pin.OUT)

def set_alarm_buzzer(sound_on):
    if BUZZER_ACTIVE_LOW:
        buzzer.value(0 if sound_on else 1)
    else:
        buzzer.value(1 if sound_on else 0)

set_alarm_buzzer(False)

# Physical Arm/Disarm Button (Internal pull-up; works with both KY-004 and discrete buttons)
button = Pin(16, Pin.IN, Pin.PULL_UP)
button_idle_state = button.value()
button_prev_pressed = False

# Status LEDs
led_green = Pin(17, Pin.OUT) # Disarmed = Solid ON
led_red = Pin(18, Pin.OUT)   # Armed = Slow Blink, Alarm = Rapid Flashing

# ----------------- SYSTEM STATE -----------------
STATE_DISARMED = "DISARMED"
STATE_ARMED = "ARMED"
STATE_ALARM = "ALARM_TRIGGERED"

current_state = STATE_DISARMED
last_button_time = 0
last_state_change = time.time()
event_logs = []

def log_event(message):
    timestamp = time.localtime()
    time_str = "{:02d}:{:02d}:{:02d}".format(timestamp[3], timestamp[4], timestamp[5])
    entry = "[{}] {}".format(time_str, message)
    event_logs.insert(0, entry)
    if len(event_logs) > 15:
        event_logs.pop()
    print(entry)

def send_webhook_alert(msg):
    """Optional webhook notification to Discord or Telegram."""
    if hasattr(secrets, 'DISCORD_WEBHOOK_URL') and secrets.DISCORD_WEBHOOK_URL.startswith("http"):
        try:
            urequests.post(secrets.DISCORD_WEBHOOK_URL, json={"content": "[ALERT] Pico W Security Node: " + msg})
        except:
            pass

def set_state(new_state):
    global current_state, last_state_change
    current_state = new_state
    last_state_change = time.ticks_ms()
    
    if new_state == STATE_DISARMED:
        set_alarm_buzzer(False)
        led_green.value(1)
        led_red.value(0)
        log_event("System DISARMED.")
    elif new_state == STATE_ARMED:
        set_alarm_buzzer(False)
        led_green.value(0)
        led_red.value(1)
        log_event("System ARMED and watching.")
    elif new_state == STATE_ALARM:
        led_green.value(0)
        log_event("INTRUSION DETECTED! Alarm sounding!")
        send_webhook_alert("Motion / Intrusion detected on Pico W security node!")

# Initialize state
set_state(STATE_DISARMED)

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
        return ip
    raise RuntimeError("Wi-Fi connection failed")

# ----------------- WEB INTERFACE -----------------
HTML_PAGE = """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Pico Security Panel</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    body { font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif; }
    .mono { font-family: 'JetBrains Mono', monospace; }
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
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
        </div>
        <div>
          <h1 class="text-xs font-semibold uppercase tracking-wider text-zinc-200">Security Node</h1>
          <p class="text-[11px] text-zinc-500 font-mono">PIR &bull; GP14</p>
        </div>
      </div>
      <div id="conn-pill" class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-green-500/10 border border-green-500/25 text-green-400 text-[11px] font-medium font-mono">
        <span class="w-1.5 h-1.5 rounded-full bg-green-400"></span>
        <span id="conn-text">SYNCED</span>
      </div>
    </header>

    <!-- Main Status Card -->
    <div id="status-card" class="bg-[#121215] border border-[#27272a] rounded-2xl p-6 text-center relative overflow-hidden transition-all duration-300">
      <div class="w-12 h-12 rounded-full mx-auto mb-3 flex items-center justify-center border transition-all" id="shield-icon-wrap">
        <svg id="shield-icon" class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
      </div>
      <span class="text-[11px] font-semibold uppercase tracking-widest text-zinc-400">System State</span>
      <div id="status-text" class="text-3xl font-light tracking-tight mt-1 mb-2 font-mono text-green-400">DISARMED</div>
      <p id="status-desc" class="text-xs text-zinc-500">PIR motion sensor idle. Ready to arm.</p>
    </div>

    <!-- Dual Action Controls -->
    <div class="grid grid-cols-2 gap-3">
      <button onclick="sendCommand('arm')" class="flex items-center justify-center gap-2 py-3 px-4 rounded-xl font-medium text-xs tracking-wider uppercase bg-[#18181b] hover:bg-zinc-800 border border-zinc-800 hover:border-amber-500/40 text-amber-300 transition-all active:scale-[0.98]">
        <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
        Arm System
      </button>
      <button onclick="sendCommand('disarm')" class="flex items-center justify-center gap-2 py-3 px-4 rounded-xl font-medium text-xs tracking-wider uppercase bg-[#18181b] hover:bg-zinc-800 border border-zinc-800 hover:border-green-500/40 text-green-400 transition-all active:scale-[0.98]">
        <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 9.9-1"/></svg>
        Disarm
      </button>
    </div>

    <!-- Event Log -->
    <div class="bg-[#121215] border border-[#27272a] rounded-2xl p-4">
      <div class="flex items-center justify-between mb-3 text-zinc-400">
        <span class="text-[11px] font-semibold uppercase tracking-wider">Activity Log</span>
        <span class="text-[10px] font-mono text-zinc-500">LAST 15 EVENTS</span>
      </div>
      <div id="log-list" class="space-y-1.5 font-mono text-xs max-h-48 overflow-y-auto text-zinc-400 pr-1"></div>
    </div>
  </div>

  <script>
    async function sendCommand(action) {
      await fetch('/api/' + action);
      updateStatus();
    }

    async function updateStatus() {
      try {
        const res = await fetch('/api/status');
        const data = await res.json();
        const card = document.getElementById('status-card');
        const text = document.getElementById('status-text');
        const desc = document.getElementById('status-desc');
        const iconWrap = document.getElementById('shield-icon-wrap');
        
        if (data.state === 'DISARMED') {
          text.innerText = 'DISARMED';
          text.className = 'text-3xl font-light tracking-tight mt-1 mb-2 font-mono text-green-400';
          desc.innerText = 'PIR sensor idle. No alerts active.';
          iconWrap.className = 'w-12 h-12 rounded-full mx-auto mb-3 flex items-center justify-center border bg-green-500/10 border-green-500/25 text-green-400';
          card.className = 'bg-[#121215] border border-[#27272a] rounded-2xl p-6 text-center relative overflow-hidden transition-all duration-300';
        } else if (data.state === 'ARMED') {
          text.innerText = 'ARMED';
          text.className = 'text-3xl font-light tracking-tight mt-1 mb-2 font-mono text-amber-400';
          desc.innerText = 'Motion sensor active. Watching for intrusion...';
          iconWrap.className = 'w-12 h-12 rounded-full mx-auto mb-3 flex items-center justify-center border bg-amber-500/10 border-amber-500/20 text-amber-400';
          card.className = 'bg-[#121215] border border-amber-500/30 rounded-2xl p-6 text-center relative overflow-hidden transition-all duration-300';
        } else if (data.state === 'ALARM_TRIGGERED') {
          text.innerText = 'INTRUSION!';
          text.className = 'text-3xl font-bold tracking-tight mt-1 mb-2 font-mono text-rose-500 animate-pulse';
          desc.innerText = 'Sensor tripped! Siren sounding!';
          iconWrap.className = 'w-12 h-12 rounded-full mx-auto mb-3 flex items-center justify-center border bg-rose-500/20 border-rose-500/40 text-rose-400 animate-bounce';
          card.className = 'bg-rose-950/20 border border-rose-500/50 rounded-2xl p-6 text-center relative overflow-hidden transition-all duration-300';
        }

        const list = document.getElementById('log-list');
        list.innerHTML = data.logs.map(l => '<div class="py-1 border-b border-zinc-800/40 last:border-0">' + l + '</div>').join('');
      } catch (e) {}
    }
    setInterval(updateStatus, 1500);
    updateStatus();
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

def main_loop(ip):
    global current_state, last_button_time
    
    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', 80))
    server.listen(2)
    server.settimeout(0.05) # 50ms polling timeout

    print("Security system active at http://%s" % ip)
    alarm_beep_toggle = 0
    last_alarm_tick = 0

    while True:
        now = time.ticks_ms()

        # 1. Handle physical push button with edge detection and debounce
        btn_val = button.value()
        is_pressed = (btn_val == 0) if button_idle_state == 1 else (btn_val == 1)
        if is_pressed and not button_prev_pressed and time.ticks_diff(now, last_button_time) > 250:
            last_button_time = now
            if current_state == STATE_DISARMED:
                set_state(STATE_ARMED)
            else:
                set_state(STATE_DISARMED)
        button_prev_pressed = is_pressed

        # 2. Handle sensor trigger when ARMED
        if current_state == STATE_ARMED and sensor_pin.value() == 1:
            set_state(STATE_ALARM)

        # 3. Handle Alarm Sound / Light sequence
        if current_state == STATE_ALARM:
            if time.ticks_diff(now, last_alarm_tick) > 250:
                last_alarm_tick = now
                alarm_beep_toggle = 1 - alarm_beep_toggle
                set_alarm_buzzer(alarm_beep_toggle)
                led_red.value(alarm_beep_toggle)

        # 4. Handle incoming HTTP web client requests
        try:
            cl, _ = server.accept()
            cl.settimeout(3.0) # 3-second timeout for browser read/write
            try:
                req = cl.recv(1024).decode('utf-8')
                if "GET /api/arm" in req:
                    set_state(STATE_ARMED)
                    send_json(cl, {"ok": True})
                elif "GET /api/disarm" in req:
                    set_state(STATE_DISARMED)
                    send_json(cl, {"ok": True})
                elif "GET /api/status" in req:
                    send_json(cl, {"state": current_state, "logs": event_logs})
                else:
                    send_html(cl, HTML_PAGE)
            finally:
                cl.close()
        except OSError:
            # Timeout when no browser is connecting; loop continues smoothly
            pass

if __name__ == "__main__":
    ip = connect_wifi()
    main_loop(ip)
