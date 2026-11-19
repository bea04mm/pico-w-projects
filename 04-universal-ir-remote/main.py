"""
Project 04: Universal Smart IR Remote with Web Interface
Raspberry Pi Pico W + IR Receiver (VS1838B) + IR Transmitter (KY-005)
Uses 38kHz PWM Carrier Modulation to record and blast infrared signals.
"""

import time
import network
import socket
import json
from machine import Pin, PWM

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
onboard_led.value(0)

# IR Receiver: Active LOW (VS1838B outputs HIGH when idle, LOW when detecting 38kHz bursts)
ir_rx = Pin(15, Pin.IN, Pin.PULL_UP)

# IR Transmitter: Hardware PWM configured at 38kHz carrier
ir_tx_pin = Pin(16, Pin.OUT)
ir_pwm = PWM(ir_tx_pin)
ir_pwm.freq(38000)
ir_pwm.duty_u16(0)  # Start carrier OFF

# ----------------- CODE PERSISTENCE -----------------
CODES_FILE = "ir_codes.json"

DEFAULT_CODES = {
    "NEC Sample Power": [
        9000, 4500, 560, 560, 560, 1690, 560, 560, 560, 560,
        560, 560, 560, 560, 560, 560, 560, 1690, 560, 1690,
        560, 1690, 560, 1690, 560, 1690, 560, 1690, 560, 1690,
        560, 1690, 560, 560, 560, 560, 560, 560, 560, 560,
        560, 560, 560, 560, 560, 560, 560, 560, 560, 1690,
        560, 1690, 560, 1690, 560, 1690, 560, 1690, 560, 1690,
        560, 1690, 560, 1690, 560
    ]
}

def load_codes():
    try:
        with open(CODES_FILE, "r") as f:
            data = json.load(f)
            if isinstance(data, dict) and len(data) > 0:
                return data
    except Exception:
        pass
    return dict(DEFAULT_CODES)

def save_codes(codes_dict):
    try:
        with open(CODES_FILE, "w") as f:
            json.dump(codes_dict, f)
    except Exception as e:
        print("Failed to save codes to flash:", e)

saved_codes = load_codes()

# ----------------- IR CAPTURE & TRANSMISSION -----------------
def capture_ir_raw(timeout_ms=5000):
    """Wait for incoming IR signal and capture pulse durations in microseconds."""
    pulses = []
    start_wait = time.ticks_ms()

    # Visual cue: LED on while actively waiting for remote signal
    onboard_led.value(1)

    # Wait for the first falling edge (IR leader mark start)
    while ir_rx.value() == 1:
        if time.ticks_diff(time.ticks_ms(), start_wait) > timeout_ms:
            onboard_led.value(0)
            return None  # Timed out without detecting signal

    # Record marks and spaces
    t_last = time.ticks_us()
    current_level = 0
    while True:
        t_start = time.ticks_us()
        while ir_rx.value() == current_level:
            # 25ms silence indicates the transmission frame has ended
            if time.ticks_diff(time.ticks_us(), t_start) > 25000:
                onboard_led.value(0)
                return pulses

        now = time.ticks_us()
        duration = time.ticks_diff(now, t_last)
        pulses.append(duration)
        t_last = now
        current_level = 1 - current_level
        if len(pulses) >= 200:
            break

    onboard_led.value(0)
    return pulses

def transmit_ir_raw(pulses):
    """Blast raw IR pulses using 38kHz PWM carrier."""
    onboard_led.value(1)
    is_mark = True
    for dur in pulses:
        if is_mark:
            ir_pwm.duty_u16(21845)  # 33.3% duty cycle for clean 38kHz carrier
        else:
            ir_pwm.duty_u16(0)
        time.sleep_us(dur)
        is_mark = not is_mark
    ir_pwm.duty_u16(0)
    onboard_led.value(0)

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

# ----------------- WEB DASHBOARD -----------------
HTML_PAGE = """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Universal Smart IR Remote</title>
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
    
    <!-- Top Header -->
    <header class="flex items-center justify-between px-1">
      <div class="flex items-center space-x-2.5">
        <div class="w-8 h-8 rounded-lg bg-[#18181b] border border-[#27272a] flex items-center justify-center text-zinc-400">
          <svg class="w-4 h-4 text-cyan-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M4.9 19.1C1 15.2 1 8.8 4.9 4.9"/><path d="M7.8 16.2c-2.3-2.3-2.3-6.1 0-8.5"/>
            <circle cx="12" cy="12" r="2"/><path d="M16.2 7.8c2.3 2.3 2.3 6.1 0 8.5"/>
            <path d="M19.1 4.9C23 8.8 23 15.1 19.1 19.1"/>
          </svg>
        </div>
        <div>
          <h1 class="text-xs font-semibold uppercase tracking-wider text-zinc-200">Universal IR Remote</h1>
          <p class="text-[11px] text-zinc-500 font-mono">Pico W &bull; 38kHz PWM Blaster</p>
        </div>
      </div>
      <div class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-green-500/10 border border-green-500/25 text-green-400 text-[11px] font-medium font-mono">
        <span class="w-1.5 h-1.5 rounded-full bg-green-400"></span>
        <span>ONLINE</span>
      </div>
    </header>

    <!-- Signal Capture Card -->
    <div class="bg-[#121215] border border-[#27272a] rounded-2xl p-5 shadow-xl">
      <div class="flex justify-between items-start mb-3">
        <div>
          <span class="text-[11px] font-semibold uppercase tracking-widest text-zinc-400">Capture New Signal</span>
          <p class="text-xs text-zinc-500 mt-0.5">Point your remote at receiver (GP15) and record</p>
        </div>
      </div>
      
      <div class="space-y-2.5">
        <div class="flex gap-2">
          <input id="btn-name" type="text" placeholder="Command name (e.g. TV_Power)"
            class="flex-1 bg-[#18181b] border border-zinc-800 focus:border-cyan-500/60 rounded-xl px-3.5 py-2.5 text-xs text-zinc-200 font-mono placeholder:text-zinc-600 outline-none transition-all">
          <button id="record-btn" onclick="recordCode()"
            class="flex items-center gap-1.5 py-2.5 px-4 rounded-xl font-medium text-xs tracking-wider uppercase bg-[#18181b] hover:bg-zinc-800 border border-zinc-800 hover:border-cyan-500/40 text-cyan-400 transition-all active:scale-[0.98]">
            <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="3"/>
            </svg>
            Record
          </button>
        </div>
        <div id="status-banner" class="text-[11px] font-mono text-zinc-400 text-center min-h-[16px] py-0.5"></div>
      </div>
    </div>

    <!-- Saved Commands Card -->
    <div class="bg-[#121215] border border-[#27272a] rounded-2xl p-5 shadow-xl">
      <div class="flex items-center justify-between mb-3 text-zinc-400">
        <span class="text-[11px] font-semibold uppercase tracking-wider">Stored Remote Commands</span>
        <span id="code-count" class="text-[10px] font-mono text-zinc-500">-- COMMANDS</span>
      </div>
      <div id="codes-list" class="space-y-2 max-h-[360px] overflow-y-auto pr-1"></div>
    </div>

    <!-- Quick Tips Footer -->
    <footer class="px-2 pt-1 pb-2 text-[11px] text-zinc-500 flex justify-between items-center font-mono">
      <span>TX Pin: GP16 (38kHz)</span>
      <span>RX Pin: GP15</span>
    </footer>

  </div>

  <script>
    async function loadCodes() {
      try {
        const res = await fetch('/api/list');
        const list = await res.json();
        const container = document.getElementById('codes-list');
        const countSpan = document.getElementById('code-count');
        
        countSpan.innerText = list.length + ' COMMAND' + (list.length === 1 ? '' : 'S');
        
        if (list.length === 0) {
          container.innerHTML = '<div class="text-xs text-zinc-500 py-6 text-center font-mono">No commands stored yet. Record one above.</div>';
          return;
        }

        container.innerHTML = list.map(item => `
          <div class="flex items-center justify-between p-3 rounded-xl bg-[#18181b] border border-zinc-800/80 hover:border-zinc-700 transition-all">
            <div>
              <div class="text-xs font-medium text-zinc-200 font-mono">${item.name}</div>
              <div class="text-[10px] text-zinc-500 font-mono mt-0.5">${item.pulses} pulses</div>
            </div>
            <div class="flex items-center gap-1.5">
              <button onclick="blastCode('${item.name}')" 
                class="px-3 py-1.5 rounded-lg bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 border border-cyan-500/25 text-xs font-mono font-medium transition-all active:scale-95 flex items-center gap-1">
                <svg class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
                </svg>
                Send
              </button>
              <button onclick="deleteCode('${item.name}')" 
                title="Delete command"
                class="p-1.5 rounded-lg text-zinc-500 hover:text-red-400 hover:bg-red-500/10 border border-transparent hover:border-red-500/20 transition-all active:scale-95">
                <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/>
                </svg>
              </button>
            </div>
          </div>
        `).join('');
      } catch (err) {
        console.error(err);
      }
    }

    async function blastCode(name) {
      const banner = document.getElementById('status-banner');
      banner.className = 'text-[11px] font-mono text-cyan-400 text-center min-h-[16px] py-0.5';
      banner.innerText = 'Transmitting: ' + name + '...';
      try {
        await fetch('/api/blast?name=' + encodeURIComponent(name));
        setTimeout(() => { banner.innerText = ''; }, 1200);
      } catch (err) {
        banner.className = 'text-[11px] font-mono text-red-400 text-center min-h-[16px] py-0.5';
        banner.innerText = 'Transmission error';
      }
    }

    async function recordCode() {
      const input = document.getElementById('btn-name');
      const name = input.value.trim();
      const banner = document.getElementById('status-banner');
      const recordBtn = document.getElementById('record-btn');

      if (!name) {
        banner.className = 'text-[11px] font-mono text-amber-400 text-center min-h-[16px] py-0.5';
        banner.innerText = 'Please enter a command name first';
        input.focus();
        return;
      }

      banner.className = 'text-[11px] font-mono text-cyan-400 text-center min-h-[16px] py-0.5 animate-pulse';
      banner.innerText = 'Listening for remote button (5s)...';
      recordBtn.disabled = true;

      try {
        const res = await fetch('/api/learn?name=' + encodeURIComponent(name));
        const result = await res.json();
        if (result.ok) {
          banner.className = 'text-[11px] font-mono text-green-400 text-center min-h-[16px] py-0.5';
          banner.innerText = 'Saved "' + name + '" (' + result.pulses + ' pulses)';
          input.value = '';
          loadCodes();
        } else {
          banner.className = 'text-[11px] font-mono text-amber-400 text-center min-h-[16px] py-0.5';
          banner.innerText = 'Timeout: No IR signal detected';
        }
      } catch (err) {
        banner.className = 'text-[11px] font-mono text-red-400 text-center min-h-[16px] py-0.5';
        banner.innerText = 'Connection error during capture';
      } finally {
        recordBtn.disabled = false;
        setTimeout(() => {
          if (banner.innerText.includes('Saved') || banner.innerText.includes('Timeout')) {
            banner.innerText = '';
          }
        }, 3500);
      }
    }

    async function deleteCode(name) {
      if (!confirm('Delete command "' + name + '"?')) return;
      try {
        await fetch('/api/delete?name=' + encodeURIComponent(name));
        loadCodes();
      } catch (err) {
        console.error(err);
      }
    }

    loadCodes();
  </script>
</body>
</html>
"""

# ----------------- HTTP SERVER & API -----------------
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

def extract_param(req, key):
    try:
        part = req.split(key + "=")[1].split(" ")[0].split("&")[0]
        # Decode basic URL escapes
        return part.replace("%20", " ").replace("+", " ")
    except Exception:
        return ""

def start_server(ip):
    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', 80))
    server.listen(3)
    print("Dashboard ready at http://%s" % ip)

    while True:
        try:
            cl, _ = server.accept()
            cl.settimeout(10.0)
            try:
                req = cl.recv(1024).decode('utf-8')

                if "GET /api/list" in req:
                    items = [{"name": k, "pulses": len(v)} for k, v in saved_codes.items()]
                    send_json(cl, items)

                elif "GET /api/blast" in req:
                    name = extract_param(req, "name")
                    if name in saved_codes:
                        transmit_ir_raw(saved_codes[name])
                        send_json(cl, {"ok": True})
                    else:
                        send_json(cl, {"ok": False, "error": "Not found"})

                elif "GET /api/learn" in req:
                    name = extract_param(req, "name")
                    if name:
                        captured = capture_ir_raw(timeout_ms=5000)
                        if captured and len(captured) >= 4:
                            saved_codes[name] = captured
                            save_codes(saved_codes)
                            send_json(cl, {"ok": True, "pulses": len(captured)})
                        else:
                            send_json(cl, {"ok": False, "error": "No signal"})
                    else:
                        send_json(cl, {"ok": False, "error": "Missing name"})

                elif "GET /api/delete" in req:
                    name = extract_param(req, "name")
                    if name in saved_codes:
                        del saved_codes[name]
                        save_codes(saved_codes)
                        send_json(cl, {"ok": True})
                    else:
                        send_json(cl, {"ok": False, "error": "Not found"})

                else:
                    send_html(cl, HTML_PAGE)
            finally:
                cl.close()
        except Exception:
            pass

if __name__ == "__main__":
    ip = connect_wifi()
    start_server(ip)
