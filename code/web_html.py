"""
HTML, CSS and debug-page templates for the ESP32 web interface.

All three functions return plain strings that are encoded to bytes
before being written to the socket in ``main.py``.

Functions:
    web_page()        — main control UI
    debug_web_page()  — live debug log viewer (auto-scrolling)
    web_css()         — shared stylesheet
"""
# web_html.py

def web_page():
    """
    Return the main control UI as an HTML string.

    The page polls ``data.json`` every 4 seconds via fetch to update
    button states, RGB values, temperature, humidity and network info.

    Returns:
        str: Full HTML document.
    """
    html = """
<!DOCTYPE html>
<html lang="en">
<head>
  <title>Sternwarte Huettenlicht</title>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="web.css">
</head>
<body>
  <header>
    <h1>&#9733; Sternwarte H&uuml;ttenlicht</h1>
  </header>
  <main>
    <!-- Light Control Card -->
    <section class="card">
      <h2>Lichtsteuerung</h2>
      <div class="light-row">
        <span class="label">Licht Rot</span>
        <span class="state" id="button_red">--</span>
        <div class="btn-group">
          <button class="btn btn-on" id="btn_red_on" onclick="sendCmd('/?red=on')">ON</button>
          <button class="btn btn-off" id="btn_red_off" onclick="sendCmd('/?red=off')">OFF</button>
        </div>
      </div>
      <div class="light-row">
        <span class="label">Licht Wei&szlig;</span>
        <span class="state" id="button_white">--</span>
        <div class="btn-group">
          <button class="btn btn-on" id="btn_white_on" onclick="sendCmd('/?white=on')">ON</button>
          <button class="btn btn-off" id="btn_white_off" onclick="sendCmd('/?white=off')">OFF</button>
        </div>
      </div>
    </section>

    <!-- Color Picker Card -->
    <section class="card">
      <h2>Farbwahl</h2>
      <div class="color-section">
        <div class="color-picker-wrap">
          <input type="color" id="colorpicker" value="#ff0000" oninput="onPickerChange(this.value)">
          <div class="preview" id="preview"></div>
        </div>
        <div class="rgb-inputs">
          <div class="rgb-field"><label>R</label><input type="number" id="red" min="0" max="255" value="0"></div>
          <div class="rgb-field"><label>G</label><input type="number" id="green" min="0" max="255" value="0"></div>
          <div class="rgb-field"><label>B</label><input type="number" id="blue" min="0" max="255" value="0"></div>
          <button class="btn btn-send" onclick="setColor()">Senden</button>
        </div>
      </div>
      <div class="brightness-row">
        <span>Helligkeit:</span><span id="LED_brightness">100</span>%
      </div>
    </section>

    <!-- Presets Card -->
    <section class="card">
      <h2>Presets</h2>
      <div class="presets-grid">
        <button class="btn preset" style="--c:#ff0000" onclick="setPreset(255,0,0)">Rot</button>
        <button class="btn preset" style="--c:#00ff00" onclick="setPreset(0,255,0)">Gr&uuml;n</button>
        <button class="btn preset" style="--c:#0000ff" onclick="setPreset(0,0,255)">Blau</button>
        <button class="btn preset" style="--c:#ffffff" onclick="setPreset(255,255,255)">Wei&szlig;</button>
        <button class="btn preset" style="--c:#ffff00" onclick="setPreset(255,255,0)">Gelb</button>
        <button class="btn preset" style="--c:#ff00ff" onclick="setPreset(255,0,255)">Lila</button>
        <button class="btn preset" style="--c:#00ffff" onclick="setPreset(0,255,255)">Cyan</button>
        <button class="btn preset" style="--c:#ffa500" onclick="setPreset(255,165,0)">Orange</button>
      </div>
    </section>

    <!-- Sensor Card -->
    <section class="card">
      <h2>Umgebung</h2>
      <div class="sensor-grid">
        <div class="sensor-item"><span class="sensor-icon">&#127777;</span><span id="temperature">--</span> &deg;C</div>
        <div class="sensor-item"><span class="sensor-icon">&#128167;</span><span id="humidity">--</span> %</div>
      </div>
    </section>

    <!-- System Info Card -->
    <section class="card">
      <h2>System</h2>
      <div class="info-grid">
        <div class="info-row"><span>IP:</span><span id="ip_address">--</span></div>
        <div class="info-row"><span>WLAN:</span><span id="ssid">--</span></div>
        <div class="info-row"><span>Auto-Off:</span><span id="auto_off">--</span> min</div>
        <div class="info-row"><span>Easter Egg:</span><span id="easter_egg">OFF</span></div>
      </div>
      <div class="links">
        <a href="config.html">&#9881; Einstellungen</a>
        <a href="logs.html">&#128220; Logs</a>
        <a href="debug.html">&#128736; Debug</a>
      </div>
    </section>

    <!-- Easter Egg Card (hidden) -->
    <section class="card easteregg" id="easteregg_card" style="display:none">
      <h2>&#127881; Secret Mode</h2>
      <div class="ee-buttons">
        <button class="btn ee-rainbow" onclick="sendCmd('/?easter=rainbow')">&#127752; Rainbow</button>
        <button class="btn ee-random" onclick="sendCmd('/?easter=random')">&#127922; Random</button>
        <button class="btn ee-stop" onclick="sendCmd('/?easter=off')">&#9724; Stop</button>
      </div>
    </section>
  </main>

  <script>
  function sendCmd(url){
    fetch(url).then(function(){setTimeout(poll,500)});
  }
  function setColor(){
    var r=document.getElementById('red').value||0;
    var g=document.getElementById('green').value||0;
    var b=document.getElementById('blue').value||0;
    updatePreview(r,g,b);
    sendCmd('/?r='+r+'&g='+g+'&b='+b);
  }
  function setPreset(r,g,b){
    document.getElementById('red').value=r;
    document.getElementById('green').value=g;
    document.getElementById('blue').value=b;
    updatePreview(r,g,b);
    sendCmd('/?r='+r+'&g='+g+'&b='+b);
  }
  function onPickerChange(hex){
    var r=parseInt(hex.substr(1,2),16);
    var g=parseInt(hex.substr(3,2),16);
    var b=parseInt(hex.substr(5,2),16);
    document.getElementById('red').value=r;
    document.getElementById('green').value=g;
    document.getElementById('blue').value=b;
    updatePreview(r,g,b);
    setColor();
  }
  function updatePreview(r,g,b){
    var c='rgb('+r+','+g+','+b+')';
    document.getElementById('preview').style.background=c;
    document.getElementById('colorpicker').value='#'+hex(r)+hex(g)+hex(b);
  }
  function hex(v){v=parseInt(v);return(v<16?'0':'')+v.toString(16)}
  function poll(){
    fetch('data.json').then(function(r){return r.json()}).then(function(d){
      document.getElementById('button_red').innerText=d.button_red;
      document.getElementById('button_white').innerText=d.button_white;
      document.getElementById('LED_brightness').innerText=d.LED_brightness;
      document.getElementById('temperature').innerText=d.temperature;
      document.getElementById('humidity').innerText=d.humidity;
      document.getElementById('ip_address').innerText=d.network_ip;
      document.getElementById('ssid').innerText=d.network_ssid;
      document.getElementById('auto_off').innerText=d.auto_off_minutes;
      document.getElementById('easter_egg').innerText=d.easter_egg;
      updatePreview(d.red,d.green,d.blue);
      // highlight active states
      var ro=d.button_red==='ON';
      document.getElementById('btn_red_on').classList.toggle('active',ro);
      document.getElementById('btn_red_off').classList.toggle('active',!ro);
      var wo=d.button_white==='ON';
      document.getElementById('btn_white_on').classList.toggle('active',wo);
      document.getElementById('btn_white_off').classList.toggle('active',!wo);
    }).catch(function(){});
  }
  poll();
  setInterval(poll,4000);
  // Easter Egg: 10 clicks on title within 6 seconds
  (function(){
    var eeCount=0,eeTimer=null;
    document.querySelector('h1').addEventListener('click',function(){
      eeCount++;
      if(eeTimer)clearTimeout(eeTimer);
      eeTimer=setTimeout(function(){eeCount=0},6000);
      if(eeCount>=10){
        document.getElementById('easteregg_card').style.display='block';
        eeCount=0;
      }
    });
  })();
  </script>
</body>
</html>
"""
    return html

def debug_web_page():
    """
    Return the debug log viewer as an HTML string.

    Uses shared CSS, polls debugsub.html every 4 seconds with auto-scroll.

    Returns:
        str: Full HTML document.
    """
    debug = """
<!DOCTYPE html>
<html lang="en">
<head>
  <title>Debug - Sternwarte</title>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="web.css">
</head>
<body>
  <header>
    <h1>&#128736; Debug Live-Log</h1>
  </header>
  <main>
    <section class="card">
      <h2>Live Debug Output</h2>
      <div class="log-output" id="log"></div>
    </section>
    <section class="card">
      <div class="links">
        <a href="/">&#9733; Startseite</a>
        <a href="logs.html">&#128220; Logs</a>
        <a href="config.html">&#9881; Einstellungen</a>
      </div>
    </section>
  </main>
  <script>
  var logEl=document.getElementById('log');
  setInterval(function(){
    var atBottom=logEl.scrollTop+logEl.clientHeight>=logEl.scrollHeight-30;
    fetch('debugsub.html').then(function(r){return r.text()}).then(function(t){
      if(t.length>0){
        logEl.insertAdjacentText('beforeend',t);
        if(atBottom)logEl.scrollTop=logEl.scrollHeight;
      }
    });
  },4000);
  </script>
</body>
</html>
"""
    return debug

def logs_web_page():
    """
    Return the logs viewer as an HTML string.

    Uses shared CSS, polls logs.json every 5 seconds for the full debug buffer.

    Returns:
        str: Full HTML document.
    """
    logs = """
<!DOCTYPE html>
<html lang="en">
<head>
  <title>Logs - Sternwarte</title>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="web.css">
</head>
<body>
  <header>
    <h1>&#128220; System Logs</h1>
  </header>
  <main>
    <section class="card">
      <h2>Log Buffer</h2>
      <div class="log-output" id="log"></div>
    </section>
    <section class="card">
      <div class="links">
        <a href="/">&#9733; Startseite</a>
        <a href="debug.html">&#128736; Debug</a>
        <a href="config.html">&#9881; Einstellungen</a>
      </div>
    </section>
  </main>
  <script>
  var logEl=document.getElementById('log');
  function pollLogs(){
    fetch('logs.json').then(function(r){return r.text()}).then(function(t){
      logEl.textContent=t;
      logEl.scrollTop=logEl.scrollHeight;
    });
  }
  pollLogs();
  setInterval(pollLogs,5000);
  </script>
</body>
</html>
"""
    return logs

def web_css():
    """
    Return the shared stylesheet as a CSS string.

    Returns:
        str: CSS rules for the web interface.
    """
    css = """
*{box-sizing:border-box;margin:0;padding:0}
html{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#0d1117;color:#e6edf3}
body{min-height:100vh;padding:1rem}
header{text-align:center;padding:1.5rem 0}
h1{color:#58a6ff;font-size:1.6rem;letter-spacing:.5px}
h2{color:#8b949e;font-size:1rem;margin-bottom:.8rem;border-bottom:1px solid #21262d;padding-bottom:.4rem}
main{max-width:600px;margin:0 auto;display:flex;flex-direction:column;gap:1rem}
.card{background:#161b22;border:1px solid #30363d;border-radius:12px;padding:1.2rem;box-shadow:0 2px 8px rgba(0,0,0,.4)}
.light-row{display:flex;align-items:center;gap:.8rem;margin-bottom:.6rem;flex-wrap:wrap}
.light-row .label{flex:1;font-size:.95rem}
.light-row .state{font-weight:bold;min-width:30px;text-align:center}
.btn-group{display:flex;gap:.4rem}
.btn{border:none;border-radius:8px;padding:.5rem 1.2rem;font-size:.9rem;cursor:pointer;transition:all .2s;color:#fff;background:#30363d}
.btn:hover{transform:scale(1.05)}
.btn-on{background:#238636}.btn-on.active{background:#2ea043;box-shadow:0 0 10px #2ea043}
.btn-off{background:#da3633}.btn-off.active{background:#f85149;box-shadow:0 0 10px #f85149}
.btn-send{background:#1f6feb;margin-top:.5rem;width:100%}
.btn-send:hover{background:#388bfd}
.color-section{display:flex;gap:1rem;align-items:flex-start;flex-wrap:wrap}
.color-picker-wrap{display:flex;flex-direction:column;align-items:center;gap:.6rem}
.color-picker-wrap input[type=color]{width:64px;height:64px;border:none;border-radius:8px;cursor:pointer;background:none}
.preview{width:64px;height:32px;border-radius:6px;border:1px solid #30363d;background:#000;transition:background .3s}
.rgb-inputs{flex:1;display:flex;flex-direction:column;gap:.4rem;min-width:140px}
.rgb-field{display:flex;align-items:center;gap:.5rem}
.rgb-field label{width:20px;font-weight:bold;color:#8b949e}
.rgb-field input{flex:1;background:#0d1117;border:1px solid #30363d;border-radius:6px;padding:.4rem;color:#e6edf3;font-size:.9rem}
.brightness-row{margin-top:.6rem;color:#8b949e;font-size:.85rem}
.presets-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:.5rem}
.preset{position:relative;background:var(--c);color:#fff;font-size:.8rem;padding:.6rem .3rem;text-shadow:0 1px 2px rgba(0,0,0,.7);border-radius:8px;border:2px solid transparent}
.preset:hover{border-color:#58a6ff;transform:scale(1.08)}
.sensor-grid{display:flex;gap:1.5rem;justify-content:center}
.sensor-item{font-size:1.1rem;display:flex;align-items:center;gap:.4rem}
.sensor-icon{font-size:1.4rem}
.info-grid{display:flex;flex-direction:column;gap:.3rem;font-size:.9rem}
.info-row{display:flex;justify-content:space-between}
.links{margin-top:.8rem;display:flex;gap:1rem;justify-content:center}
.links a{color:#58a6ff;text-decoration:none;font-size:.85rem}
.links a:hover{text-decoration:underline}
.easteregg{border:2px solid transparent;background-image:linear-gradient(#161b22,#161b22),linear-gradient(135deg,#ff0000,#ff8800,#ffff00,#00ff00,#0088ff,#8800ff,#ff0000);background-origin:border-box;background-clip:padding-box,border-box}
.ee-buttons{display:flex;gap:.6rem;justify-content:center;flex-wrap:wrap}
.ee-rainbow{background:linear-gradient(135deg,#ff0000,#ff8800,#ffff00,#00ff00,#0088ff,#8800ff);color:#fff;font-size:1rem;padding:.7rem 1.2rem}
.ee-random{background:linear-gradient(135deg,#ff00ff,#00ffff,#ffff00);color:#111;font-size:1rem;padding:.7rem 1.2rem}
.ee-stop{background:#6e7681;color:#fff;font-size:1rem;padding:.7rem 1.2rem}
.config-grid{display:flex;flex-direction:column;gap:.8rem}
.config-row{display:flex;align-items:center;justify-content:space-between;gap:.8rem}
.config-row label{flex:1;font-size:.95rem}
.config-row input,.config-row select{background:#0d1117;border:1px solid #30363d;border-radius:6px;padding:.5rem;color:#e6edf3;font-size:.9rem;width:100px;text-align:center}
.btn-save{background:#238636;width:100%;margin-top:.5rem}
.btn-save:hover{background:#2ea043}
.btn-danger{background:#da3633;width:100%;margin-top:.5rem}
.btn-danger:hover{background:#f85149}
.log-output{font-family:'Courier New',monospace;color:#3fb950;font-size:12px;white-space:pre-wrap;background:#0d1117;border-radius:8px;padding:1rem;max-height:70vh;overflow-y:auto;border:1px solid #30363d}
.status-badge{display:inline-block;padding:.2rem .6rem;border-radius:4px;font-size:.8rem;font-weight:bold}
.status-badge.saved{background:#238636;color:#fff}
"""
    return css


def config_web_page(fade_speed, auto_off, debug_level, hostname, rotary_enabled):
    """
    Return the configuration page as an HTML string.

    Args:
        fade_speed (int): Current fade speed (1-64).
        auto_off (int): Current auto-off minutes (0-480).
        debug_level (int): Current debug level (1-4).
        hostname (str): Current WiFi hostname.
        rotary_enabled (bool): Current rotary encoder enabled state.

    Returns:
        str: Full HTML document with config-save and reset actions.
    """
    html = """
<!DOCTYPE html>
<html lang="en">
<head>
  <title>Einstellungen - Sternwarte</title>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="web.css">
</head>
<body>
  <header>
    <h1>&#9881; Einstellungen</h1>
  </header>
  <main>
    <section class="card">
      <h2>LED Konfiguration</h2>
      <div class="config-grid">
        <div class="config-row">
          <label>Fade Speed (1-64)</label>
          <input type="number" id="cfg_fade" min="1" max="64" value=\"""" + str(fade_speed) + """">
        </div>
        <div class="config-row">
          <label>Auto-Off (min, 0=aus)</label>
          <input type="number" id="cfg_autooff" min="0" max="480" value=\"""" + str(auto_off) + """">
        </div>
        <div class="config-row">
          <label>Debug Level (1-4)</label>
          <select id="cfg_debug">
            <option value="1\"""" + (' selected' if debug_level == 1 else '') + """>1 - Fehler</option>
            <option value="2\"""" + (' selected' if debug_level == 2 else '') + """>2 - Warnungen</option>
            <option value="3\"""" + (' selected' if debug_level == 3 else '') + """>3 - Info</option>
            <option value="4\"""" + (' selected' if debug_level == 4 else '') + """>4 - Verbose</option>
          </select>
        </div>
      </div>
    </section>
    <section class="card">
      <h2>WiFi</h2>
      <div class="config-grid">
        <div class="config-row">
          <label>Hostname</label>
          <input type="text" id="cfg_host" maxlength="32" value=\"""" + str(hostname) + """">
        </div>
        <div class="config-row">
          <label>Rotary Encoder</label>
          <select id="cfg_rotary">
            <option value="0\"""" + (' selected' if not rotary_enabled else '') + """>OFF</option>
            <option value="1\"""" + (' selected' if rotary_enabled else '') + """>ON</option>
          </select>
        </div>
      </div>
      <button class="btn btn-save" onclick="saveConfig()">&#128190; Speichern</button>
      <div id="save_status" style="text-align:center;margin-top:.5rem"></div>
    </section>
    <section class="card">
      <h2>System</h2>
      <button class="btn btn-danger" onclick="resetDevice()">&#8634; Reset</button>
      <div id="reset_status" style="text-align:center;margin-top:.5rem"></div>
    </section>
    <section class="card">
      <div class="links">
        <a href="/">&#9733; Startseite</a>
        <a href="logs.html">&#128220; Logs</a>
        <a href="debug.html">&#128736; Debug</a>
      </div>
    </section>
  </main>
  <script>
  function saveConfig(){
    var f=document.getElementById('cfg_fade').value;
    var a=document.getElementById('cfg_autooff').value;
    var d=document.getElementById('cfg_debug').value;
    var r=document.getElementById('cfg_rotary').value;
    // Keep the hostname router-friendly and within common DHCP limits.
    var h=document.getElementById('cfg_host').value.replace(/[^a-zA-Z0-9-]/g,'').substring(0,32)||'ESP32-Huettenlicht';
    document.getElementById('cfg_host').value=h;
    f=Math.max(1,Math.min(64,parseInt(f)||16));
    a=Math.max(0,Math.min(480,parseInt(a)||120));
    d=Math.max(1,Math.min(4,parseInt(d)||4));
    r=(parseInt(r)||0)?1:0;
    // GET keeps the ESP32 handler simple because the server only has to parse
    // the request line and does not need HTTP body handling.
    fetch('/?config_save&fade='+f+'&autooff='+a+'&debug='+d+'&host='+h+'&rotary='+r).then(function(){
      document.getElementById('save_status').innerHTML='<span class="status-badge saved">&#10003; Gespeichert!</span>';
      setTimeout(function(){document.getElementById('save_status').innerHTML=''},3000);
    });
  }
  function resetDevice(){
    if(!confirm('Sind Sie sicher? Das ESP32-Gerät wird sofort neu gestartet.')) return;
    document.getElementById('reset_status').innerHTML='<span class="status-badge saved">Gerät wird neu gestartet...</span>';
    // The request intentionally ignores the response body because the device
    // will reboot a moment later and close the connection itself.
    fetch('/?reset=1').catch(function(){});
  }
  </script>
</body>
</html>
"""
    return html
