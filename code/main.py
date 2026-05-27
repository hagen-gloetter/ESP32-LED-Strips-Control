"""
Main application for ESP32 LED-Strip Observatory Lighting control.

Controls three RGB LED strips for the Sternwarte Höfingen observatory via PWM.
Provides a web interface (port 80), hardware buttons, and a rotary encoder
for brightness and colour control. A DHT11 sensor reports ambient temperature
and humidity on the web UI.

Hardware:
    - ESP32 (AZ-Delivery D1 Mini or compatible)
    - 3× RGB LED strip (common-cathode, PWM-driven)
    - 2× push button (white/red light toggle)
    - 1× rotary encoder with push button (brightness)
    - 1× DHT11 temperature/humidity sensor
    - Built-in LED on GPIO 2

Pin mapping (see constants below):
    PIN_DHT       = 0   DHT11 data
    PIN_STRIP_1R  = 27  Strip 1 Red
    PIN_STRIP_1G  = 25  Strip 1 Green
    PIN_STRIP_1B  = 32  Strip 1 Blue
    PIN_STRIP_2R  = 22  Strip 2 Red
    PIN_STRIP_2G  = 21  Strip 2 Green
    PIN_STRIP_2B  = 17  Strip 2 Blue
    PIN_STRIP_3R  = 19  Strip 3 Red
    PIN_STRIP_3G  = 18  Strip 3 Green
    PIN_STRIP_3B  = 26  Strip 3 Blue
    PIN_BUTTON_W  = 13  White-light button
    PIN_BUTTON_R  = 10  Red-light button
    PIN_BUTTON_D  = 14  Rotary encoder push button
    PIN_CLK       = 33  Rotary encoder CLK
    PIN_DT        = 34  Rotary encoder DT
"""
# Lighting for our Observatory with LED-Stripes
# Observatory: https://www.sternwarte-hoefingen.de
# Code by Hagen and Ramona Glötter
# Source and Docs: https://github.com/hagen-gloetter/LED-Strips-ESP32

# GPIO Pins:
PIN_DHT = 0 # Humidity sensor
PIN_STRIP_1R = 27
PIN_STRIP_1G = 25
PIN_STRIP_1B = 32
PIN_STRIP_2R = 22
PIN_STRIP_2G = 21
PIN_STRIP_2B = 17
PIN_STRIP_3R = 19
PIN_STRIP_3G = 18
PIN_STRIP_3B = 26
PIN_BUTTON_W = 13 # T1
PIN_BUTTON_R = 10 # T2
# Rotary
PIN_BUTTON_D = 14 # Switch
PIN_CLK = 33
PIN_DT = 34

# System Includes
from time import sleep_ms
from machine import Pin, Timer
import _thread
import time
import machine
import gc
import network
import urandom
# Custom Includes
from class_debug import debug_init, debug, get_debug_msg
from class_rotary_encoder import RotaryIRQ
from class_pwm import LEDStrip
from class_debounce import debounced_Button
from class_humidity_sensor import HumiditySensor
from web_html import web_page, debug_web_page, logs_web_page, web_css, config_web_page
import class_wifi_connection
import ujson

try:
    import usocket as socket
except:
    import socket

debug_init()

# Load configuration
try:
    with open("config.json", "r") as f:
        config = ujson.load(f)
    Brightness = config.get("Brightness", 1024)
    Fade_speed = config.get("Fade_speed", 16)
    DebugLevel = config.get("DebugLevel", 4)
    LOOP_MS = config.get("LOOP_MS", 100)
    WIFI_CHECK_TICKS = config.get("WIFI_CHECK_TICKS", 300)
    auto_off_minutes = config.get("auto_off_minutes", 120)
    hostname = config.get("hostname", "ESP32-Huettenlicht")
    rotary_encoder_enabled = 1 if config.get("rotary_encoder_enabled", 0) else 0
    debug(3, __name__, "Configuration loaded from config.json")
except Exception as e:
    debug(2, __name__, f"Failed to load config.json: {e}, using defaults")
    Brightness = 1024
    Fade_speed = 16
    DebugLevel = 4
    LOOP_MS = 100
    WIFI_CHECK_TICKS = 300
    auto_off_minutes = 120
    hostname = "ESP32-Huettenlicht"
    rotary_encoder_enabled = 0

debug(4, __name__, "main.py start")

# setup LED
led = machine.Pin(2, machine.Pin.OUT)
CPU_Speed = machine.freq()
# machine.freq(int(CPU_Speed / 2)) # Brown Out Protection
# debug(4, __name__, f"machine.freq={CPU_Speed}")
# Buttons
Button_W_PIN = PIN_BUTTON_W
Button_R_PIN = PIN_BUTTON_R
Button_D_PIN = PIN_BUTTON_D
Button_W_Status = "OFF"
Button_R_Status = "OFF"
Button_D_Status = "OFF"
Button_Counter = 0
Light_W = "OFF"  # white
Light_R = "OFF"  # red
run_webserver = True
# wifi variables
wifi_status = None
wifi_ssid = None
wifi_ip = None
temperature = 0
humidity = 0


# setup LED Stripes
ColorRGB = [0, 0, 0]
ColorSollwerte = [0, 0, 0]

# Easter Egg and rapid-press state
EasterEgg_Mode = None  # None / "rainbow" / "random"
_ee_hue = 0  # current hue for rainbow mode (0-359)
_btn_w_rapid_count = 0
_btn_w_rapid_start = 0
_btn_r_rapid_count = 0
_btn_r_rapid_start = 0
RAPID_WINDOW_SHORT = 2000  # ms for 2x/4x brightness presets
RAPID_WINDOW_LONG = 6000   # ms for 10x easter egg
_auto_off_start = 0  # ticks_ms when light turned on, 0 = inactive

# init LED Stripes
# TODO  Listen übergeben
Strip1 = LEDStrip(ColorRGB[0], ColorRGB[1], ColorRGB[2], PIN_STRIP_1R, PIN_STRIP_1G, PIN_STRIP_1B)
Strip2 = LEDStrip(ColorRGB[0], ColorRGB[1], ColorRGB[2], PIN_STRIP_2R, PIN_STRIP_2G, PIN_STRIP_2B)
Strip3 = LEDStrip(ColorRGB[0], ColorRGB[1], ColorRGB[2], PIN_STRIP_3R, PIN_STRIP_3G, PIN_STRIP_3B)
Strip1.SetColor(ColorRGB[0], ColorRGB[1], ColorRGB[2])
Strip2.SetColor(ColorRGB[0], ColorRGB[1], ColorRGB[2])
Strip3.SetColor(ColorRGB[0], ColorRGB[1], ColorRGB[2])

def update_all_strips(r, g, b):
    """
    Update all three LED strips with the given RGB values.

    Args:
        r (int): Red duty cycle (0–1023).
        g (int): Green duty cycle (0–1023).
        b (int): Blue duty cycle (0–1023).

    Returns:
        None
    """
    Strip1.SetColor(r, g, b)
    Strip2.SetColor(r, g, b)
    Strip3.SetColor(r, g, b)


def hsv_to_rgb_1023(h):
    """
    Convert HSV hue to RGB with full saturation and value at 10-bit scale.

    Integer-only arithmetic for MicroPython performance.

    Args:
        h (int): Hue angle 0–359.

    Returns:
        list: [R, G, B] each 0–1023.
    """
    # Sector 0-5, each 60 degrees
    sector = h // 60
    remainder = h - (sector * 60)  # 0-59
    # fractional part scaled to 0-1023
    f = (remainder * 1023) // 60
    nf = 1023 - f

    if sector == 0:
        return [1023, f, 0]
    elif sector == 1:
        return [nf, 1023, 0]
    elif sector == 2:
        return [0, 1023, f]
    elif sector == 3:
        return [0, nf, 1023]
    elif sector == 4:
        return [f, 0, 1023]
    else:
        return [1023, 0, nf]

r = RotaryIRQ(
    pin_num_clk=PIN_CLK,
    pin_num_dt=PIN_DT,
    min_val=0,
    max_val=10,
    reverse=True,
    range_mode=RotaryIRQ.RANGE_BOUNDED,
)
rotarySwitch = Pin(PIN_BUTTON_D, Pin.IN)
rotary_val_old = r.value()
isRotaryEncoder = rotary_encoder_enabled == 1
r.set_enabled(isRotaryEncoder)

# rotary encoder init end

temperature_sensor = HumiditySensor(PIN_DHT)

# Webserver start
WS_initstage = 0
websocket = ""

# setup Wifi
global wifi
wifi = class_wifi_connection.WifiConnect()
wifi.set_hostname(hostname)
(wifi_status, wifi_ssid, wifi_ip) = wifi.connect()
debug(4, __name__, "Wifi connection established")


def get_websocket():
    """
    Create and bind the TCP server socket on port 80.

    Sets SO_REUSEADDR so the port is immediately available after a reboot.
    Stores the socket in the global ``websocket`` variable.

    Returns:
        None
    """
    global websocket
    debug(4, __name__, "Websocket init")
    websocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    websocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    websocket.bind(("", 80))
    websocket.listen(5)
    sleep_ms(500)
    debug(4, __name__, "Websocket done")


def thread_webserver(delay, name):
    """
    Webserver thread: accept HTTP requests and serve the control UI.

    Runs until ``run_webserver`` is set to False. Parses GET parameters
    for RGB colour, red/white toggle, Easter Eggs, config writes,
    reset requests, and JSON/CSS/debug endpoints.

    Args:
        delay (int): Unused legacy parameter.
        name (str): Thread name used in debug messages.

    Returns:
        None
    """
    global run_webserver
    while run_webserver == True:
        global JSONdata
        global websocket
        global Light_W
        global Light_R
        global ColorSollwerte
        global EasterEgg_Mode
        global _auto_off_start
        global _ee_hue
        global _btn_w_rapid_count
        global _btn_r_rapid_count
        global Fade_speed
        global auto_off_minutes
        global DebugLevel
        global hostname
        global isRotaryEncoder
        global rotary_val_old
        global temperature
        global humidity
        conn = None
        try:
            conn, addr = websocket.accept()
            request = conn.recv(1024)
            request = str(request)
            machine.idle()

            # Refresh sensor data opportunistically on web traffic so the UI
            # stays current without a dedicated sensor polling thread.
            (temperature, humidity) = temperature_sensor.get_humidity_and_temperature()

            # Parse the request directly from the first line. This keeps the
            # socket handling simple and predictable on MicroPython.
            r_index = request.find('/?r=')
            g_index = request.find('&g=')
            b_index = request.find('&b=')
            if r_index != -1 and g_index != -1 and b_index != -1:
                # Extract RGB values from the URL
                try:
                    r_value = int(request[r_index+4 : g_index])
                    g_value = int(request[g_index+3 : b_index])
                    # find end of blue value (space or & terminates)
                    b_end = request.find(" ", b_index+3)
                    if b_end == -1:
                        b_end = request.find("&", b_index+3)
                    if b_end == -1:
                        b_end = len(request)
                    b_value = int(request[b_index+3 : b_end])

                    # Validate if the values are in the range of 0 to 255
                    if 0 <= r_value <= 255 and 0 <= g_value <= 255 and 0 <= b_value <= 255:
                        debug(4, __name__, f"Received valid RGB values: R={r_value}, G={g_value}, B={b_value}")
                        # Scale from 0-255 to 0-1023 for internal PWM resolution
                        ColorSollwerte = [r_value * 1023 // 255, g_value * 1023 // 255, b_value * 1023 // 255]
                        # Custom color: disable white/red mode so timer doesn't override
                        Light_W = "OFF"
                        Light_R = "OFF"
                        EasterEgg_Mode = None
                        _auto_off_start = 0
                        # Update the LED strips with the new color
                        update_all_strips(ColorSollwerte[0], ColorSollwerte[1], ColorSollwerte[2])
                    else:
                        debug(4, __name__, "Invalid RGB values received. Ignoring request.")
                except ValueError:
                    debug(4, __name__, "Invalid RGB input detected. Could not convert to integers.")

            # Keep the route handling flat. On MicroPython this is usually more
            # predictable and cheaper than building a generic router layer.
            led_on = request.find("/?led=on")
            if led_on == 6:
                led.value(1)
            led_off = request.find("/?led=off")
            if led_off == 6:
                led.value(0)
            # red
            red_on = request.find("/?red=on")
            if red_on == 6:
                Light_R = "ON"
                Light_W = "OFF"
                EasterEgg_Mode = None
                _auto_off_start = time.ticks_ms()
                debug(4, __name__, "Web RED ON")
                ColorSollwerte = [Brightness, 0, 0]
            red_off = request.find("/?red=off")
            if red_off == 6:
                Light_R = "OFF"
                _auto_off_start = 0
                debug(4, __name__, "Web RED OFF")
                ColorSollwerte = [0, 0, 0]
            # white
            white_on = request.find("/?white=on")
            if white_on == 6:
                Light_W = "ON"
                Light_R = "OFF"
                EasterEgg_Mode = None
                _auto_off_start = time.ticks_ms()
                debug(4, __name__, "Web white ON")
                ColorSollwerte = [Brightness, Brightness, Brightness]
            white_off = request.find("/?white=off")
            if white_off == 6:
                Light_W = "OFF"
                _auto_off_start = 0
                debug(4, __name__, "Web white OFF")
                ColorSollwerte = [0, 0, 0]
            # Easter Egg endpoints
            easter_rainbow = request.find("/?easter=rainbow")
            if easter_rainbow == 6:
                EasterEgg_Mode = "rainbow"
                Light_W = "OFF"
                Light_R = "OFF"
                _auto_off_start = time.ticks_ms()
                debug(2, __name__, "Web Easter Egg RAINBOW activated")
            easter_random = request.find("/?easter=random")
            if easter_random == 6:
                EasterEgg_Mode = "random"
                Light_W = "OFF"
                Light_R = "OFF"
                _auto_off_start = time.ticks_ms()
                debug(2, __name__, "Web Easter Egg RANDOM activated")
            easter_off = request.find("/?easter=off")
            if easter_off == 6:
                EasterEgg_Mode = None
                _ee_hue = 0
                _btn_w_rapid_count = 0
                _btn_r_rapid_count = 0
                Light_W = "OFF"
                Light_R = "OFF"
                _auto_off_start = 0
                ColorSollwerte = [0, 0, 0]
                debug(2, __name__, "Web Easter Egg stopped")
            # Config is written immediately so changes survive the next reset.
            config_save = request.find("/?config_save")
            if config_save == 6:
                try:
                    fade_idx = request.find("&fade=")
                    autooff_idx = request.find("&autooff=")
                    dbg_idx = request.find("&debug=")
                    if fade_idx != -1 and autooff_idx != -1 and dbg_idx != -1:
                        new_fade = int(request[fade_idx+6:autooff_idx])
                        new_autooff = int(request[autooff_idx+9:dbg_idx])
                        # find end of debug value (& or space terminates)
                        dbg_end = request.find("&", dbg_idx+7)
                        if dbg_end == -1:
                            dbg_end = request.find(" ", dbg_idx+7)
                        if dbg_end == -1:
                            dbg_end = len(request)
                        new_debug = int(request[dbg_idx+7:dbg_end])
                        rotary_idx = request.find("&rotary=")
                        # Validate ranges
                        new_fade = max(1, min(64, new_fade))
                        new_autooff = max(0, min(480, new_autooff))
                        new_debug = max(1, min(4, new_debug))
                        if rotary_idx != -1:
                            rotary_end = request.find("&", rotary_idx+8)
                            if rotary_end == -1:
                                rotary_end = request.find(" ", rotary_idx+8)
                            if rotary_end == -1:
                                rotary_end = len(request)
                            new_rotary = 1 if int(request[rotary_idx+8:rotary_end]) else 0
                        else:
                            new_rotary = 0
                        # Hostname is optional; keep the current value if the
                        # browser does not send the field.
                        host_idx = request.find("&host=")
                        if host_idx != -1:
                            host_end = request.find("&", host_idx+6)
                            if host_end == -1:
                                host_end = request.find(" ", host_idx+6)
                            if host_end == -1:
                                host_end = len(request)
                            new_hostname = request[host_idx+6:host_end]
                        else:
                            new_hostname = hostname
                        # Apply new runtime values before persisting them so the
                        # current session behaves exactly like the next reboot.
                        Fade_speed = new_fade
                        auto_off_minutes = new_autooff
                        DebugLevel = new_debug
                        hostname = new_hostname
                        isRotaryEncoder = new_rotary == 1
                        rotary_val_old = r.value()
                        r.set_enabled(isRotaryEncoder)
                        wifi.set_hostname(hostname)
                        # Save to config.json
                        cfg = {
                            "Brightness": Brightness,
                            "Fade_speed": Fade_speed,
                            "DebugLevel": DebugLevel,
                            "LOOP_MS": LOOP_MS,
                            "WIFI_CHECK_TICKS": WIFI_CHECK_TICKS,
                            "auto_off_minutes": auto_off_minutes,
                            "hostname": hostname,
                            "rotary_encoder_enabled": 1 if isRotaryEncoder else 0
                        }
                        with open("config.json", "w") as f:
                            ujson.dump(cfg, f)
                        debug(2, __name__, f"Config saved: fade={Fade_speed}, autooff={auto_off_minutes}, debug={DebugLevel}")
                except Exception as e:
                    debug(2, __name__, f"Config save error: {e}")
            set_JSON(Light_W, Light_R)
            jsonrequest = request.find("data.json")
            cssrequest = request.find("web.css")
            resetrequest = request.find("/?reset=1")
            configrequest = request.find("config.html")
            debugrequest = request.find("debug.html")
            debugsubrequest = request.find("debugsub.html")
            logsrequest = request.find("logs.html")
            logsjsonrequest = request.find("logs.json")
            # Build the current status snapshot once per request so every route
            # sees a consistent JSON view of the system state.
            if jsonrequest > 0:  # JSON
                response = JSONdata
                conn.send(b"HTTP/1.1 200 OK\n")
                conn.send(b"Content-Type: application/json\n")
                conn.send(b"Connection: close\n\n")
                conn.sendall(response.encode())
                conn.close()
            elif logsjsonrequest > 0:  # Logs JSON
                response = get_debug_msg()
                conn.send(b"HTTP/1.1 200 OK\n")
                conn.send(b"Content-Type: application/json\n")
                conn.send(b"Connection: close\n\n")
                conn.sendall(response.encode())
                conn.close()
            elif logsrequest > 0:  # Logs page
                response = logs_web_page()
                conn.send(b"HTTP/1.1 200 OK\n")
                conn.send(b"Content-Type: text/html\n")
                conn.send(b"Connection: close\n\n")
                conn.sendall(response.encode())
                conn.close()
            elif cssrequest > 0:  # CSS
                response = web_css()
                conn.send(b"HTTP/1.1 200 OK\n")
                conn.send(b"Content-Type: text/css\n")
                conn.send(b"Connection: close\n\n")
                conn.sendall(response.encode())
                conn.close()
            elif resetrequest == 6:  # Reset device
                # Send the HTTP response first so the browser can show a status
                # message before the ESP32 reboots.
                response = "ESP32 resetting"
                conn.send(b"HTTP/1.1 200 OK\n")
                conn.send(b"Content-Type: text/plain\n")
                conn.send(b"Connection: close\n\n")
                conn.sendall(response.encode())
                conn.close()
                debug(1, __name__, "Web reset requested")
                sleep_ms(300)
                machine.reset()
            elif configrequest > 0:  # Config page
                response = config_web_page(Fade_speed, auto_off_minutes, DebugLevel, hostname, isRotaryEncoder)
                conn.send(b"HTTP/1.1 200 OK\n")
                conn.send(b"Content-Type: text/html\n")
                conn.send(b"Connection: close\n\n")
                conn.sendall(response.encode())
                conn.close()
            elif debugsubrequest > 0:  # Debug sub data
                response = get_debug_msg()
                conn.send(b"HTTP/1.1 200 OK\n")
                conn.send(b"Content-Type: text/plain\n")
                conn.send(b"Connection: close\n\n")
                conn.sendall(response.encode())
                conn.close()
            elif debugrequest > 0:  # Main debug page
                response = debug_web_page()
                conn.send(b"HTTP/1.1 200 OK\n")
                conn.send(b"Content-Type: text/html\n")
                conn.send(b"Connection: close\n\n")
                conn.sendall(response.encode())
                conn.close()
            else:  # HTML
                response = web_page()
                conn.send(b"HTTP/1.1 200 OK\n")
                conn.send(b"Content-Type: text/html\n")
                conn.send(b"Connection: close\n\n")
                conn.sendall(response.encode())
                conn.close()
                print("default") # DEBUG
        except Exception as e:
            debug(4, __name__, f"webserver error: {e}")
            if conn is not None:
                conn.close()
        # Garbage collection nach jeder Anfrage
        gc.collect()  # Speicher freigeben


JSONdata = '{}'


def set_JSON(status1, status2):
    """
    Build the global ``JSONdata`` string from current system state.

    Uses ujson.dumps for memory-efficient JSON construction.
    Brightness is reported as percentage (0–100).

    Args:
        status1 (str): Legacy parameter for white-light status.
        status2 (str): Legacy parameter for red-light status.

    Returns:
        None
    """
    global JSONdata
    brightness_pct = (Brightness * 100) // 1023
    data = {
        "button_red": Light_R,
        "button_white": Light_W,
        "LED_brightness": str(brightness_pct),
        "LED_roof": "NA",
        "red": str(ColorSollwerte[0]),
        "green": str(ColorSollwerte[1]),
        "blue": str(ColorSollwerte[2]),
        "temperature": str(temperature),
        "humidity": str(humidity),
        "network_ip": str(wifi_ip),
        "network_ssid": str(wifi_ssid),
        "auto_off_minutes": str(auto_off_minutes),
        "easter_egg": str(EasterEgg_Mode) if EasterEgg_Mode else "OFF",
        "hostname": hostname
    }
    JSONdata = ujson.dumps(data)


# Webserver end =========================================================================================================

def do_a_blink(status):
    """
    Set the built-in LED to the requested state.

    Args:
        status (int): LED output state, usually ``0`` or ``1``.

    Returns:
        None
    """
    led.value(status)
#    sleep_ms(200)
#    led.value(0)



def strips_update_Brightness():
    """
    Apply brightness-scaled fade from ``ColorRGB`` toward ``ColorSollwerte``.

    Called by the LED-fade timer (timer0, 53 ms period). Advances each
    channel by ``Fade_speed`` per call and writes the result to all strips.
    When white or red mode is active, ``ColorSollwerte`` is first updated
    to reflect the current ``Brightness`` value.
    Handles Easter Egg modes (rainbow/random) by cycling target colors.

    Returns:
        None
    """
    global ColorSollwerte
    global ColorRGB
    global Brightness
    global Fade_speed
    global EasterEgg_Mode
    global _ee_hue

    # Easter Egg: Rainbow – direct HSV per tick, constant brightness
    if EasterEgg_Mode == "rainbow":
        _ee_hue = (_ee_hue + 1) % 360
        ColorRGB = hsv_to_rgb_1023(_ee_hue)
        ColorSollwerte = ColorRGB[:]
        update_all_strips(ColorRGB[0], ColorRGB[1], ColorRGB[2])
        set_JSON(Light_W, Light_R)
        return
    # Easter Egg: Random – vivid colors via HSV
    elif EasterEgg_Mode == "random":
        if ColorRGB[0] == ColorSollwerte[0] and ColorRGB[1] == ColorSollwerte[1] and ColorRGB[2] == ColorSollwerte[2]:
            ColorSollwerte = hsv_to_rgb_1023(urandom.getrandbits(9) % 360)
    else:
        # Normal operation
        if Light_W == "ON":
            ColorSollwerte = [Brightness, Brightness, Brightness]
        elif Light_R == "ON":
            ColorSollwerte = [Brightness, 0, 0]

    for i in range(len(ColorRGB)):
        if ColorRGB[i] < ColorSollwerte[i]:  # fade in
            ColorRGB[i] = ColorRGB[i] + Fade_speed
            if ColorRGB[i] >= ColorSollwerte[i]:  # no overshoot
                ColorRGB[i] = ColorSollwerte[i]
        elif ColorRGB[i] > ColorSollwerte[i]:  # fade out
            ColorRGB[i] = ColorRGB[i] - Fade_speed
            if ColorRGB[i] <= ColorSollwerte[i]:  # no overshoot
                ColorRGB[i] = ColorSollwerte[i]
        else:
            pass  # values are equal
    update_all_strips(ColorRGB[0], ColorRGB[1], ColorRGB[2])
    set_JSON(Light_W, Light_R)


# button part start =========================================================================================================


def Button_W_switch():
    """
    Toggle the white-light state with rapid-press detection.

    Red light takes priority: if red is ON the white button is ignored.
    Rapid presses: 2x=50%, 4x=25% brightness, 10x=Rainbow Easter Egg.
    Always starts at 100% brightness when turning ON.

    Returns:
        None
    """
    global Light_W
    global Light_R
    global ColorSollwerte
    global Brightness
    global Button_Counter
    global _btn_w_rapid_count
    global _btn_w_rapid_start
    global EasterEgg_Mode
    global _auto_off_start

    # Rapid-press tracking
    now = time.ticks_ms()
    if time.ticks_diff(now, _btn_w_rapid_start) < RAPID_WINDOW_LONG:
        _btn_w_rapid_count += 1
    else:
        _btn_w_rapid_count = 1
        _btn_w_rapid_start = now

    txt = "Button_W_switch"
    if Light_R == "ON":
        Light_W = "OFF"
        Button_Counter += 1
        txt = "Button_W_switch: White IGNORE - Red over White"
    elif Light_W == "OFF" and Light_R == "OFF":
        Light_W = "ON"
        Brightness = 1023  # always start at 100%
        _auto_off_start = now
        Button_Counter += 1
        txt = "Button_W_switch: White ON"
        ColorSollwerte = [Brightness, Brightness, Brightness]
    elif Light_W == "ON" and Light_R == "OFF":
        Light_W = "OFF"
        _auto_off_start = 0
        Button_Counter += 1
        txt = "Button_W_switch: White OFF"
        ColorSollwerte = [0, 0, 0]
    else:
        txt = "Button_W_switch: Else Case ERROR Red=" + Light_R + " white="+Light_W

    # Rapid-press brightness presets (only within short window)
    elapsed = time.ticks_diff(now, _btn_w_rapid_start)
    if _btn_w_rapid_count == 2 and elapsed < RAPID_WINDOW_SHORT:
        Brightness = 512
        Light_W = "ON"
        Light_R = "OFF"
        ColorSollwerte = [Brightness, Brightness, Brightness]
        txt = "Button_W_switch: Rapid 2x -> 50%"
    elif _btn_w_rapid_count == 4 and elapsed < RAPID_WINDOW_SHORT:
        Brightness = 256
        Light_W = "ON"
        Light_R = "OFF"
        ColorSollwerte = [Brightness, Brightness, Brightness]
        txt = "Button_W_switch: Rapid 4x -> 25%"
    elif _btn_w_rapid_count >= 10:
        EasterEgg_Mode = "rainbow"
        Light_W = "OFF"
        Light_R = "OFF"
        _btn_w_rapid_count = 0
        txt = "Button_W_switch: Easter Egg RAINBOW activated!"

    debug(2, __name__ + str(Button_Counter), txt)
    set_JSON(Light_W, Light_R)


def Button_R_switch():
    """
    Toggle the red-light state with rapid-press detection.

    Red light overrides white. Rapid presses: 2x=50%, 4x=25% brightness,
    10x=Random Easter Egg. Always starts at 100% brightness when turning ON.

    Returns:
        None
    """
    global Light_W
    global Light_R
    global ColorSollwerte
    global Brightness
    global Button_Counter
    global _btn_r_rapid_count
    global _btn_r_rapid_start
    global EasterEgg_Mode
    global _auto_off_start

    # Rapid-press tracking
    now = time.ticks_ms()
    if time.ticks_diff(now, _btn_r_rapid_start) < RAPID_WINDOW_LONG:
        _btn_r_rapid_count += 1
    else:
        _btn_r_rapid_count = 1
        _btn_r_rapid_start = now

    txt = "Button_R_switch"
    if Light_R == "OFF" and Light_W == "OFF":
        Light_R = "ON"
        Light_W = "OFF"
        Brightness = 1023  # always start at 100%
        _auto_off_start = now
        Button_Counter += 1
        txt = "Button_R_switch: Red ON"
        ColorSollwerte = [Brightness, 0, 0]
    elif Light_R == "OFF" and Light_W == "ON":
        Light_R = "ON"
        Light_W = "OFF"
        Brightness = 1023  # always start at 100%
        _auto_off_start = now
        Button_Counter += 1
        txt = "Button_R_switch: Red over White ON"
        ColorSollwerte = [Brightness, 0, 0]
    elif Light_R == "ON":
        Light_R = "OFF"
        _auto_off_start = 0
        Button_Counter += 1
        txt = "Button_R_switch: Red OFF"
        ColorSollwerte = [0, 0, 0]
    else:
        txt = "Button_R_switch: Else Case ERROR Red=" + Light_R + " white="+Light_W

    # Rapid-press brightness presets (only within short window)
    elapsed = time.ticks_diff(now, _btn_r_rapid_start)
    if _btn_r_rapid_count == 2 and elapsed < RAPID_WINDOW_SHORT:
        Brightness = 512
        Light_R = "ON"
        Light_W = "OFF"
        ColorSollwerte = [Brightness, 0, 0]
        txt = "Button_R_switch: Rapid 2x -> 50%"
    elif _btn_r_rapid_count == 4 and elapsed < RAPID_WINDOW_SHORT:
        Brightness = 256
        Light_R = "ON"
        Light_W = "OFF"
        ColorSollwerte = [Brightness, 0, 0]
        txt = "Button_R_switch: Rapid 4x -> 25%"
    elif _btn_r_rapid_count >= 10:
        EasterEgg_Mode = "random"
        Light_W = "OFF"
        Light_R = "OFF"
        _btn_r_rapid_count = 0
        txt = "Button_R_switch: Easter Egg RANDOM activated!"

    debug(2, __name__ + str(Button_Counter), txt)
    set_JSON(Light_W, Light_R)


# init callback function and iterrupts to Debounced Buttons
Button_W = debounced_Button(PIN_BUTTON_W)  # Weißer Lichtschalter
Button_R = debounced_Button(PIN_BUTTON_R)  # Roter Lichtschalter
Button_D = debounced_Button(PIN_BUTTON_D)  # Taster für den Rotary-Encoder (Drehgeber)

# button part end =========================================================================================================


def RotaryController():
    """
    Read the rotary encoder and update ``Brightness``.

    Only active when at least one light is ON. Brightness is set to
    2^encoder_value, mapping 0–10 steps to 1–1024. Called every 59 ms
    via timer1.

    Returns:
        None
    """
    global Light_W
    global Light_R
    global rotary_val_old
    global rotarySwitch
    global Brightness
    if Light_W == "ON" or Light_R == "ON":  # only if at least one switch is on
        r_value = r.get_rotary_encoder(rotarySwitch, rotary_val_old, isRotaryEncoder)
        if r_value is not None:
            rotary_val_old = r_value
            Brightness = (
                2**r_value
            )  # translate 16 steps to 255 color-steps and set limits
        else:
            debug(4, __name__, "Rotary encoder returned None (no change)")
        # debug(4, __name__, f"Brightness update ={Brightness} = {r_value}")


def LEDfadeTimer(timer0):
    """
    Timer callback for LED fading.

    Args:
        timer0 (Timer): Triggering timer instance.

    Returns:
        None
    """
    strips_update_Brightness()


def RotaryControllerTimer(timer1):
    """
    Timer callback for rotary encoder polling.

    Args:
        timer1 (Timer): Triggering timer instance.

    Returns:
        None
    """
    RotaryController()


def ButtonDebounceTimer(timer0):
    """
    Timer callback for debounced button handling and hold-to-dim logic.

    Args:
        timer0 (Timer): Triggering timer instance.

    Returns:
        None
    """
    global Button_W
    global Button_R
    global Button_D
    global Button_W_Status
    global Button_R_Status
    global Button_D_Status
    global Light_W
    global Light_R
    global ColorSollwerte
    global Brightness
    global EasterEgg_Mode
    global _ee_hue
    global _btn_w_rapid_count
    global _btn_w_rapid_start
    global _btn_r_rapid_count
    global _btn_r_rapid_start
    global _auto_off_start

    # Get current and old statuses of the buttons
    b1_old = Button_W.get_oldstatus() # Achtung ERST alten Status abfragen !!!
    b2_old = Button_R.get_oldstatus()
    b3_old = Button_D.get_oldstatus()
    b1_new = Button_W.get_status()
    b2_new = Button_R.get_status()
    b3_new = Button_D.get_status()

    # Easter Egg abort: any button press stops the effect
    if EasterEgg_Mode is not None:
        if b1_old != b1_new or b2_old != b2_new or b3_old != b3_new:
            debug(2, __name__, f"Easter Egg '{EasterEgg_Mode}' stopped by button press")
            EasterEgg_Mode = None
            _ee_hue = 0
            _btn_w_rapid_count = 0
            _btn_w_rapid_start = 0
            _btn_r_rapid_count = 0
            _btn_r_rapid_start = 0
            _auto_off_start = 0
            Light_W = "OFF"
            Light_R = "OFF"
            ColorSollwerte = [0, 0, 0]
            Button_W_Status = b1_new
            Button_R_Status = b2_new
            set_JSON(Light_W, Light_R)
        return  # skip normal button handling during Easter Egg

    if b1_old != b1_new:
        debug(4, __name__, 
            f"Button_W_Status={Button_W_Status}, Button_R_Status={Button_R_Status}")
        Button_W_Status = b1_new
        Button_W_switch()
    if b2_old != b2_new:
        debug(4, __name__, 
            f"Button_W_Status={Button_W_Status}, Button_R_Status={Button_R_Status}")
        Button_R_Status = b2_new
        Button_R_switch()

    # Hold-to-Dim: slowly reduce brightness while button is held (>500ms)
    if Light_W == "ON" and Button_W.get_holdcount() > 50:
        if Brightness > 50:
            Brightness -= 1
            ColorSollwerte = [Brightness, Brightness, Brightness]
    if Light_R == "ON" and Button_R.get_holdcount() > 50:
        if Brightness > 50:
            Brightness -= 1
            ColorSollwerte = [Brightness, 0, 0]

    # Handle button press for Button_D (Rotary Encoder Button)
    if b3_old != b3_new:
        debug(4, __name__, f"Button_D pressed: {b3_new}")
        if b3_new == "ON":
            debug(4, __name__, "Rotary Encoder Button ON")
        else:
            debug(4, __name__, "Rotary Encoder Button OFF")


def stop_all():
    """
    Stop timers, shut down the webserver, and disconnect WiFi.

    Returns:
        None
    """
    global wifi
    timer0.deinit()
    timer1.deinit()
    Strip1.SetColor(0, 1023, 0)  # give me some light that init is done ;-)
    sleep_ms(1500)
    Strip1.SetColor(0, 1023, 1023)
    sleep_ms(1500)
    Strip1.SetColor(0, 0, 0)
    # shut it down
    global run_webserver
    run_webserver = False
    wifi.disconnect()


# Run LED Fading via timer interrupt (smoother than MainLoop)
debug(4, __name__, "Start Fade Timer")
timer0 = Timer(0)
timer0.init(period=53, mode=Timer.PERIODIC, callback=LEDfadeTimer)

debug(4, __name__, "Start RotaryController Timer")
timer1 = Timer(1)
timer1.init(period=59, mode=Timer.PERIODIC, callback=RotaryControllerTimer)

debug(4, __name__, "Start Button Debounce Timer")
timer2 = Timer(2)
timer2.init(period=10, mode=Timer.PERIODIC, callback=ButtonDebounceTimer)


get_websocket()

# turn off LEDs
Strip1.SetColor(0, 0, 0)
Strip2.SetColor(0, 0, 0)
strips_update_Brightness()
set_JSON(Light_W, Light_R)

# debug no thread
_thread.start_new_thread(thread_webserver, (4, "webserver"))
led.value(1)
toggle = 1
cnt = 0
debug(4, __name__, "entering mainloop")

Strip1.SetColor(0, 1023, 0)  # give me some green light that init is done ;-)
sleep_ms(2000)
Strip1.SetColor(0, 0, 0)

# while True:

# Main loop

# Activate Hardware Watchdog AFTER all init is complete.
# Timeout > WiFi connect timeout (10s) to allow reconnect attempts.
wdt = machine.WDT(timeout=15000)  # 15 s

_loop_count = 0
while True:
    wdt.feed()
    _loop_count += 1
    if _loop_count % WIFI_CHECK_TICKS == 0:
        debug(3, __name__, "Performing WiFi health check")
        (wifi_status, wifi_ssid, wifi_ip) = wifi.check_connection()
        debug(2, __name__, f"WiFi status: {wifi_status}, SSID: {wifi_ssid}, IP: {wifi_ip}")
        gc.collect()
    # Auto-Off Timer: turn off lights after configured minutes
    if _auto_off_start > 0 and auto_off_minutes > 0:
        if time.ticks_diff(time.ticks_ms(), _auto_off_start) > auto_off_minutes * 60000:
            Light_W = "OFF"
            Light_R = "OFF"
            EasterEgg_Mode = None
            ColorSollwerte = [0, 0, 0]
            _auto_off_start = 0
            debug(2, __name__, f"Auto-Off: Lights turned off after {auto_off_minutes} min")
            set_JSON(Light_W, Light_R)
    sleep_ms(LOOP_MS)




