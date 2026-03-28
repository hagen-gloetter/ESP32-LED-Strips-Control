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

    The page polls ``data.json`` every 4 seconds via XHR to update
    button states, RGB values, temperature, humidity and network info.

    Returns:
        str: Full HTML document.
    """
    html = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <title>Sternwarte Huettenlicht</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <link rel="stylesheet" href="web.css">
    <style>
      .loading {
        display: none;
        font-size: 1.2rem;
        color: #333;
      }
    </style>
  </head>
  <body>
    <h1>ESP Web Server</h1>
    <p class="loading" id="loading">Loading...</p>
    <table>
      <tr>
        <td><p>Licht Rot</p></td>
        <td><p id="button_red"></p></td>
        <td><p><a href="/?red=on"><button class="button">ON</button></a><a href="/?red=off"><button class="button button2">OFF</button></a></p></td>
      </tr>
      <tr>
        <td><p>Licht Weiss</p></td>
        <td><p id="button_white"></p></td>
        <td><p><a href="/?white=on"><button class="button">ON</button></a><a href="/?white=off"><button class="button button2">OFF</button></a></p></td>
      </tr>
      <tr>
        <td><p>Rot (R)</p></td>
        <td><input type="number" id="red" placeholder="0-255" min="0" max="255" /></td>
        <td><button class="button" onclick="setPreset(255,0,0)">Rot Preset</button></td>
      </tr>
      <tr>
        <td><p>Grün (G)</p></td>
        <td><input type="number" id="green" placeholder="0-255" min="0" max="255" /></td>
        <td><button class="button" onclick="setPreset(0,255,0)">Grün Preset</button></td>
      </tr>
      <tr>
        <td><p>Blau (B)</p></td>
        <td><input type="number" id="blue" placeholder="0-255" min="0" max="255" /></td>
        <td><button class="button" onclick="setPreset(0,0,255)">Blau Preset</button></td>
      </tr>
      <tr>
        <td><p>Set Color</p></td>
        <td><button class="button" onclick="setColor()">Set RGB</button></td>
        <td><button class="button" onclick="setPreset(255,255,255)">Weiß Preset</button></td>
      </tr>
      <tr>
        <td><p>Zusätzliche Presets</p></td>
        <td><button class="button" onclick="setPreset(255,255,0)">Gelb</button></td>
        <td><button class="button" onclick="setPreset(255,0,255)">Lila</button></td>
      </tr>
      <tr>
        <td></td>
        <td><button class="button" onclick="setPreset(0,255,255)">Cyan</button></td>
        <td><button class="button" onclick="setPreset(255,165,0)">Orange</button></td>
      </tr>
      <tr>
        <td colspan="2"><p>Aktuelle RGB Werte</p></td>
        <td colspan="2"><p id="current_rgb">R: 0, G: 0, B: 0</p><br><p id="LED_brightness">100</p></td>
      </tr>
      <tr>
        <td colspan="3"><a href="logs.html">System Logs anzeigen</a></td>
      </tr>
      <tr>
        <td colspan="2" rowspan="4"><p>Umgebung</p></td>
      </tr>
      <tr>
        <td>Temperatur</td><td><span id="temperature">99</span> &deg;C</td>
      </tr>
      <tr>
        <td>Feuchtigkeit</td><td><span id="humidity">0</span> %</td>
      </tr>
      <tr>
        <td>IP</td><td><span id="ip_address">xxx.xxx.xxx.xxx</span></td>
      </tr>
      <tr>
        <td>WLAN:</td><td><span id="ssid"></span></td>
      </tr>
    </table>
    <a href="debug.html">Debug</a>

    <script>
      function get_HW_Infos() {
        const xhr = new XMLHttpRequest();
        xhr.open("GET", "data.json", true);
        xhr.onreadystatechange = function () {
          if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
            var data = JSON.parse(xhr.responseText);
            document.getElementById("button_red").innerText = data.button_red;
            document.getElementById("button_white").innerText = data.button_white;
            document.getElementById("LED_brightness").innerText = data.LED_brightness;
            document.getElementById("current_rgb").innerText = `R: ${data.red}, G: ${data.green}, B: ${data.blue}`;
            document.getElementById("temperature").innerText = `${data.temperature}`;
            document.getElementById("humidity").innerText = `${data.humidity}`;
            document.getElementById("ip_address").innerText = `${data.network_ip}`;
            document.getElementById("ssid").innerText = `${data.network_ssid}`;
          }
        };
        xhr.send();
      }

      function setColor() {
        const red = document.getElementById("red").value;
        const green = document.getElementById("green").value;
        const blue = document.getElementById("blue").value;
        const xhr = new XMLHttpRequest();
        xhr.open("GET", `/?r=${red}&g=${green}&b=${blue}`, true);
        xhr.send();
      }

      function setPreset(r, g, b) {
        document.getElementById("red").value = r;
        document.getElementById("green").value = g;
        document.getElementById("blue").value = b;
        setColor();
      }

      setInterval(get_HW_Infos, 4000);
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
<html>
	<head>
		<script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
		<script type="text/javascript">
			$(document).ready(function(){
				setInterval(function(){
					y=$(document).height()-window.pageYOffset-window.innerHeight;
					$.get("debugsub.html",function(d){
						$("pre").append(d);
						if(y<30)$("html,body").animate({scrollTop:$(document).height()},"slow")
					})},4000)
			})
		</script>
		<style type="text/css">
			body{background:#010}
			pre{font-family:Arial,Helvetica,sans-serif;color:#0d0}
		</style>
	</head>
	<body><pre></pre></body>
</html>
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
<html>
	<head>
		<script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
		<script type="text/javascript">
			$(document).ready(function(){
				setInterval(function(){
					$.get("logs.json",function(d){
						$("pre").text(d);
					})},5000)
			})
		</script>
		<style type="text/css">
			body{background:#000}
			pre{font-family:monospace;color:#0f0;font-size:12px;white-space:pre-wrap}
		</style>
	</head>
	<body><h2>System Logs</h2><pre></pre></body>
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
html {
    font-family: Helvetica;
    display: inline-block;
    margin: 0px auto;
    text-align: center;
}

h1 {
    color: #0f3376;
    padding: 1vh;
}

table {
    margin-left: auto;
    margin-right: auto;
    text-align: left;
}

td {
    padding: 4px;
    border: 1px solid;
}

p {
    font-size: 1.5rem;
}

.button {
    display: inline-block;
    background-color: rgb(85, 231, 59);
    border: none;
    border-radius: 4px;
    color: white;
    padding: 16px 40px;
    text-decoration: none;
    font-size: 30px;
    margin: 2px;
    cursor: pointer;
}

.button2 {
    background-color: #f44242;
}

"""
    return css
