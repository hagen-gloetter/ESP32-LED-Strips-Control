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
      </div>
      <div class="links">
        <a href="logs.html">Logs</a>
        <a href="debug.html">Debug</a>
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
  </script>
</body>
</html>
"""
    return html

def debug_web_page():
    """
    Return the debug log viewer as an HTML string.

    Uses jQuery to poll ``debugsub.html`` every 4 seconds and append
    new log lines to a ``<pre>`` element with auto-scroll.

    Returns:
        str: Full HTML document.
    """
    debug = """
<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>body{background:#0d1117;margin:1rem}pre{font-family:monospace;color:#3fb950;font-size:13px;white-space:pre-wrap}</style>
</head><body><pre id="log"></pre>
<script>
setInterval(function(){
  var atBottom=window.innerHeight+window.scrollY>=document.body.offsetHeight-30;
  fetch('debugsub.html').then(function(r){return r.text()}).then(function(t){
    document.getElementById('log').insertAdjacentText('beforeend',t);
    if(atBottom)window.scrollTo(0,document.body.scrollHeight);
  });
},4000);
</script></body></html>
"""
    return debug

def logs_web_page():
    """
    Return a separate logs viewer as an HTML string.

    Polls /logs.json for the full debug buffer and displays it.

    Returns:
        str: Full HTML document.
    """
    logs = """
<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>body{background:#0d1117;margin:1rem;color:#e6edf3}h2{color:#58a6ff;font-family:sans-serif}pre{font-family:monospace;color:#3fb950;font-size:12px;white-space:pre-wrap}</style>
</head><body><h2>System Logs</h2><pre id="log"></pre>
<script>
setInterval(function(){
  fetch('logs.json').then(function(r){return r.text()}).then(function(t){
    document.getElementById('log').textContent=t;
  });
},5000);
</script></body></html>
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
"""
    return css
