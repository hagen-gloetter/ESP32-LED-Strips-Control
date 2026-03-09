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
# Custom Includes
from class_debug import debug_init, debug, get_debug_msg
from class_rotary_encoder import RotaryIRQ
from class_pwm import LEDStrip
from class_debounce import debounced_Button
from class_humidity_sensor import HumiditySensor
from web_html import web_page, debug_web_page, web_css
import class_wifi_connection

try:
    import usocket as socket
except:
    import socket

debug_init()
DebugLevel = 4  # 0=none 1=error 2=warn 3=nicetosee 4=whatever
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
Brightness = 1024
ColorRGB = [0, 0, 0]
ColorSollwerte = [0, 0, 0]
Fade_speed = 16

# init LED Stripes
# TODO  Listen übergeben
Strip1 = LEDStrip(ColorRGB[0], ColorRGB[1], ColorRGB[2], PIN_STRIP_1R, PIN_STRIP_1G, PIN_STRIP_1B)
Strip2 = LEDStrip(ColorRGB[0], ColorRGB[1], ColorRGB[2], PIN_STRIP_2R, PIN_STRIP_2G, PIN_STRIP_2B)
Strip3 = LEDStrip(ColorRGB[0], ColorRGB[1], ColorRGB[2], PIN_STRIP_3R, PIN_STRIP_3G, PIN_STRIP_3B)
Strip1.SetColor(ColorRGB[0], ColorRGB[1], ColorRGB[2])
Strip2.SetColor(ColorRGB[0], ColorRGB[1], ColorRGB[2])
Strip3.SetColor(ColorRGB[0], ColorRGB[1], ColorRGB[2])

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
isRotaryEncoder = True

# rotary encoder init end

temperature_sensor = HumiditySensor(PIN_DHT)

# Webserver start
WS_initstage = 0
websocket = ""

# setup Wifi
global wifi
wifi = class_wifi_connection.WifiConnect()
(wifi_status, wifi_ssid, wifi_ip) = wifi.connect()
debug(4, __name__, "Wifi connection established")


def get_websocket():
    """
    Create and bind the TCP server socket on port 80.

    Sets SO_REUSEADDR so the port is immediately available after a reboot.
    Stores the socket in the global ``websocket`` variable.
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
    for RGB colour, red/white toggle, and JSON/CSS/debug endpoints.

    Args:
        delay (int): Unused legacy parameter.
        name (str): Thread name used in debug messages.
    """
    global run_webserver
    while run_webserver == True:
        global web_page
        global debug_web_page
        global web_css
        global JSONdata
        global websocket
        global Light_W
        global Light_R
        global ColorSollwerte
        global temperature
        global humidity
        #    debug(4, __name__, f'Running thread {name}' )
        #    while True:
        #    sleep_ms(100)
        #   Init Websocket
        conn = None
        try:
            # print webpage =========================================================================================================
            #        debug(4, __name__, 'Before accept')
            conn, addr = websocket.accept()
            #        debug(4, __name__, 'Got a connection from %s' % str(addr))
            request = conn.recv(1024)
            request = str(request)
            machine.idle()

            (temperature, humidity) = temperature_sensor.get_humidity_and_temperature()

            # LED Control: Parse GET Parameters for RGB
            r_index = request.find('/?r=')
            g_index = request.find('&g=')
            b_index = request.find('&b=')
            if r_index != -1 and g_index != -1 and b_index != -1:
                # Extract RGB values from the URL
                try:
                    r_value = int(request[r_index+4 : g_index])
                    g_value = int(request[g_index+3 : b_index])
                    b_value = int(request[b_index+3 : len(request)])

                    # Validate if the values are in the range of 0 to 255
                    if 0 <= r_value <= 255 and 0 <= g_value <= 255 and 0 <= b_value <= 255:
                        debug(4, __name__, f"Received valid RGB values: R={r_value}, G={g_value}, B={b_value}")
                        ColorSollwerte = [r_value, g_value, b_value]  # Set the color for the LED Strip

                        # Update the LED strip with the new color
                        Strip1.SetColor(ColorSollwerte[0], ColorSollwerte[1], ColorSollwerte[2])
                        Strip2.SetColor(ColorSollwerte[0], ColorSollwerte[1], ColorSollwerte[2])
                    else:
                        debug(4, __name__, "Invalid RGB values received. Ignoring request.")
                except ValueError:
                    debug(4, __name__, "Invalid RGB input detected. Could not convert to integers.")

            # Handle LED toggling (existing logic for red, white, and test LEDs)
            #    debug(4, __name__, 'Content = %s' % request)
            led_on = request.find("/?led=on")
            if led_on == 6:
                # debug(4, __name__, 'LED ON')
                led.value(1)
            led_off = request.find("/?led=off")
            if led_off == 6:
                # debug(4, __name__, 'LED OFF')
                led.value(0)
            # red
            red_on = request.find("/?red=on")
            if red_on == 6:
                Light_R = "ON"
                Light_W = "OFF"
                debug(4, __name__, "Web RED ON")
                ColorSollwerte = [Brightness, 0, 0]
            red_off = request.find("/?red=off")
            if red_off == 6:
                Light_R = "OFF"
                debug(4, __name__, "Web RED OFF")
                ColorSollwerte = [0, 0, 0]
            # white
            white_on = request.find("/?white=on")
            if white_on == 6:
                Light_W = "ON"
                Light_R = "OFF"
                debug(4, __name__, "Web white ON")
                ColorSollwerte = [Brightness, Brightness, Brightness]
            white_off = request.find("/?white=off")
            if white_off == 6:
                Light_W = "OFF"
                debug(4, __name__, "Web white OFF")
                ColorSollwerte = [0, 0, 0]
            set_JSON(Light_W, Light_R)
            jsonrequest = request.find("data.json")
            cssrequest = request.find("web.css")
            debugrequest = request.find("debug.html")
            debugsubrequest = request.find("debugsub.html")
            #debug(4, __name__, "## " + debugrequest + " " + debugsubrequest) # DEBUG
            if jsonrequest > 0:  # JSON
                response = JSONdata
                conn.send(b"HTTP/1.1 200 OK\n")
                conn.send(b"Content-Type: application/json\n")
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
            elif debugsubrequest > 0:  # Main debug page
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


JSONdata = """
{
    "button_red": "-x-",
    "button_white": "-x-",
    "LED_brightness": "-x-",
    "LED_roof": "-x-",
    "red":"0",
    "green":"0",
    "blue":"0",
    "temperature":"0",
    "humidity":"0"
}
"""


def set_JSON(status1, status2):
    """
    Build the global ``JSONdata`` string from current system state.

    Args:
        status1 (str): Current Light_W state ("ON"/"OFF").
        status2 (str): Current Light_R state ("ON"/"OFF").
    """
    global JSONdata
    global Light_R
    global Light_W
    global wifi_status
    global wifi_ssid
    global wifi_ip
    global Brightness
    global ColorSollwerte
    global temperature
    global humidity
    s0 = '{\n'
    s1 = '"button_red":"' + str(Light_R) + '",\n'
    s2 = '"button_white":"' + str(Light_W) + '",\n'
    s3 = '"LED_brightness":"' + str(Brightness) + '",\n'
    s4 = '"network_ip":"' + str(wifi_ip) + '",\n'
    s5 = '"network_ssid":"' + str(wifi_ssid) + " " + str(wifi_status) + '",\n'
    s6 = '"LED_roof":"' + "NA" + '",\n'
    s7 = '"red":"' + str(ColorSollwerte[0]) + '",\n'
    s8 = '"green":"' + str(ColorSollwerte[1]) + '",\n'
    s9 = '"blue":"' + str(ColorSollwerte[2]) + '",\n'
    s10 = '"temperature":"' + str(temperature) + '",\n'
    s11 = '"humidity":"' + str(humidity) + '"\n'
    s12=  '\n}\n'

    JSONdata = s0 + s1 + s2 + s3 + s4 + s5 + s6 + s7 + s8 + s9 + s10 + s11 + s12


# Webserver end =========================================================================================================

def do_a_blink(status):
    """Set the built-in LED to *status* (0=off, 1=on)."""
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
    """
    global ColorSollwerte
    global ColorRGB
    global Brightness
    global Fade_speed
    if Light_W == "ON":
        # set Brightness to Sollwerte
        ColorSollwerte = [Brightness, Brightness, Brightness]
        # debug(4, __name__, f"Brightness White Changed: {Brightness}")
    elif Light_R == "ON":
        ColorSollwerte = [Brightness, 0, 0]
        # debug(4, __name__, f"Brightness Red Changed: {Brightness}") # set Brightness to Sollwerte

    for i in range(len(ColorRGB)):
        # debug(4, __name__, "rgb:{} rgb:{}",str(ColorRGB[i]),str(ColorSollwerte[i]))
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
    Strip1.SetColor(ColorRGB[0], ColorRGB[1], ColorRGB[2])
    # TODO: LIST as Parameter
    Strip2.SetColor(ColorRGB[0], ColorRGB[1], ColorRGB[2])
    set_JSON(Light_W, Light_R)


# button part start =========================================================================================================


def Button_W_switch():
    """
    Toggle the white-light state.

    Red light takes priority: if red is ON the white button is ignored.
    Sets ``ColorSollwerte`` accordingly and updates the JSON state.
    """
    global Light_W
    global Light_R
    global ColorSollwerte
    global Brightness
    global Button_Counter
    txt = "Button_W_switch"
    if Light_R == "ON":
        Light_W = "OFF"
        Button_Counter += 1
        txt = "Button_W_switch: White IGNORE - Red over White"
    elif Light_W == "OFF" and Light_R == "OFF":
        Light_W = "ON"
        Button_Counter += 1
        txt = "Button_W_switch: White ON"
        ColorSollwerte = [Brightness, Brightness, Brightness]
    elif Light_W == "ON" and Light_R == "OFF":
        Light_W = "OFF"
        Button_Counter += 1
        txt = "Button_W_switch: White OFF"
        ColorSollwerte = [0, 0, 0]
    else:
        txt = "Button_W_switch: Else Case ERROR Red=" + Light_R + " white="+Light_W
    debug(2, __name__ + str(Button_Counter), txt)
    set_JSON(Light_W, Light_R)


def Button_R_switch():
    """
    Toggle the red-light state.

    Red light overrides white: pressing the red button while white is ON
    switches to red mode. Sets ``ColorSollwerte`` accordingly and updates
    the JSON state.
    """
    global Light_W
    global Light_R
    global ColorSollwerte
    global Brightness
    global Button_Counter
    txt = "Button_R_switch"
    if Light_R == "OFF" and Light_W == "OFF":
        Light_R = "ON"
        Light_W = "OFF"  # just 2b sure
        Button_Counter += 1
        txt = "Button_R_switch: Red ON"
        ColorSollwerte = [Brightness, 0, 0]
    elif Light_R == "OFF" and Light_W == "ON":
        Light_R = "ON"
        Light_W = "OFF"
        Button_Counter += 1
        txt = "Button_R_switch: Red over White ON"
        ColorSollwerte = [Brightness, 0, 0]  # TODO check if this is right
    elif Light_R == "ON":
        Light_R = "OFF"
        Button_Counter += 1
        txt = "Button_R_switch: Red OFF"
        ColorSollwerte = [0, 0, 0]
    else:
        txt = "Button_R_switch: Else Case ERROR Red=" + Light_R + " white="+Light_W
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
            pass
        # debug(4, __name__, f"Brightness update ={Brightness} = {r_value}")


def LEDfadeTimer(timer0):
    strips_update_Brightness()


def RotaryControllerTimer(timer1):
    RotaryController()


def ButtonDebounceTimer(timer0):
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

    # Get current and old statuses of the buttons
    b1_old = Button_W.get_oldstatus() # Achtung ERST alten Status abfragen !!!
    b2_old = Button_R.get_oldstatus()
    b3_old = Button_D.get_oldstatus()
    b1_new = Button_W.get_status()
    b2_new = Button_R.get_status()
    b3_new = Button_D.get_status()

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
    if Button_W.get_longpress() > 0:  # Reset to full white Light
        debug(4, __name__, "Button_W longpress -  # Reset to full white Light")
        Light_W = "ON"
        Light_R = "OFF"
        Brightness = 1023
        ColorSollwerte = [Brightness, Brightness, Brightness]
    if Button_R.get_longpress() > 0:  # Reset to full red Light
        debug(4, __name__, "Button_R longpress -  # Reset to full red Light")
        Light_R = "ON"
        Light_W = "OFF"
        Brightness = 1023
        ColorSollwerte = [Brightness, 0, 0]


    # Handle button press for Button_D (Rotary Encoder Button)
    if b3_old != b3_new:
        debug(4, __name__, f"Button_D pressed: {b3_new}")
        if b3_new == "ON":
            debug(4, __name__, "Rotary Encoder Button ON")
        else:
            debug(4, __name__, "Rotary Encoder Button OFF")


def stop_all():
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

# Loop and WDT constants
LOOP_MS          = 100   # Main loop interval ms → 10 Hz
WIFI_CHECK_TICKS = 600   # WiFi check every 600 * 100ms = 60 s

# Activate Hardware Watchdog AFTER all init is complete.
# Timeout > WiFi connect timeout (10s) to allow reconnect attempts.
wdt = machine.WDT(timeout=15000)  # 15 s

_loop_count = 0
while True:
    wdt.feed()
    _loop_count += 1
    if _loop_count % WIFI_CHECK_TICKS == 0:
        (wifi_status, wifi_ssid, wifi_ip) = wifi.check_connection()
        debug(2, __name__, wifi_status)
        debug(2, __name__, wifi_ssid)
        debug(2, __name__, wifi_ip)
        gc.collect()
    sleep_ms(LOOP_MS)




