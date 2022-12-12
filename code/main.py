# For more details and step by step guide visit: Microcontrollerslab.com

from rotary_encoder_class_2 import RotaryIRQ
from web_html import web_css
from web_html import web_page
from pwm_class import LEDStrip
from class_debounce import debounced_Button
from web_html import web_page, web_css
from time import sleep_ms
from machine import Pin
from machine import Timer
import _thread
import time
import machine
import gc
import network
import class_wifi_connection

try:
    import usocket as socket
except:
    import socket
print("main.py start")

DebugLevel = 4  # 0=none 1=error 2=warn 3=nicetosee 4=whatever
# setup LED
led = machine.Pin(2, machine.Pin.OUT)
CPU_Speed = machine.freq()
# machine.freq(int(CPU_Speed / 2)) # Brown Out Protection
# print(f"machine.freq={CPU_Speed}")
# Buttons
Button_W_PIN = const(13)
Button_R_PIN = const(10)
Button_W_Status = "OFF"
Button_R_Status = "OFF"
Button_Counter = 0
Light_W = "OFF"  # white
Light_R = "OFF"  # red
run_webserver = True


# setup LED Stripes
Brightness = 1024
ColorRGB = [0, 0, 0]
ColorSollwerte = [0, 0, 0]
Fade_speed = 16

# init LED Stripes
# TODO  Listen übergeben
Strip1 = LEDStrip(ColorRGB[0], ColorRGB[1], ColorRGB[2], 27, 25, 32)
Strip2 = LEDStrip(ColorRGB[0], ColorRGB[1], ColorRGB[2], 17, 21, 22)
Strip1.SetColor(ColorRGB[0], ColorRGB[1], ColorRGB[2])
Strip2.SetColor(ColorRGB[0], ColorRGB[1], ColorRGB[2])

r = RotaryIRQ(
    pin_num_clk=33,
    pin_num_dt=34,
    min_val=0,
    max_val=10,
    reverse=True,
    range_mode=RotaryIRQ.RANGE_BOUNDED,
)
rotarySwitch = Pin(14, Pin.IN)
rotary_val_old = r.value()
isRotaryEncoder = True

# rotary encoder init end

# Webserver start
WS_initstage = 0
websocket = ""

# setup Wifi
global wifi
wifi = class_wifi_connection.WifiConnect()
(wifi_status, wifi_ssid, wifi_ip) = wifi.connect()


def get_websocket():
    global websocket
    print("Websocket init")
    websocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    websocket.bind(("", 80))
    websocket.listen(5)
    sleep_ms(500)
    print("Websocket done")


def thread_webserver(delay, name):
    global run_webserver
    while run_webserver == True:
        global web_page
        global web_css
        global JSONdata
        global websocket
        global Light_W
        global Light_R
        global ColorSollwerte
        #    print(f'Running thread {name}' )
        #    while True:
        #    sleep_ms(100)
        #   Init Websocket
        # print webpage =========================================================================================================
        #        print('Before accept')
        conn, addr = websocket.accept()
        #        print('Got a connection from %s' % str(addr))
        try:
            request = conn.recv(1024)
            request = str(request)
            machine.idle()
            #    print('Content = %s' % request)
            led_on = request.find("/?led=on")
            if led_on == 6:
                # print('LED ON')
                led.value(1)
            led_off = request.find("/?led=off")
            if led_off == 6:
                # print('LED OFF')
                led.value(0)
            # red
            red_on = request.find("/?red=on")
            if red_on == 6:
                Light_R = "ON"
                Light_W = "OFF"
                print("Web RED ON")
                ColorSollwerte = [Brightness, 0, 0]
            red_off = request.find("/?red=off")
            if red_off == 6:
                Light_R = "OFF"
                print("Web RED OFF")
                ColorSollwerte = [0, 0, 0]
            # white
            white_on = request.find("/?white=on")
            if white_on == 6:
                Light_W = "ON"
                Light_R = "OFF"
                print("Web white ON")
                ColorSollwerte = [Brightness, Brightness, Brightness]
            white_off = request.find("/?white=off")
            if white_off == 6:
                Light_W = "OFF"
                print("Web white OFF")
                ColorSollwerte = [0, 0, 0]
            set_JSON(Light_W, Light_R)
            jsonrequest = request.find("data.json")
            cssrequest = request.find("web.css")
            if jsonrequest > 4:  # JSON
                response = JSONdata
                conn.send("HTTP/1.1 200 OK\n")
                conn.send("Content-Type: application/json\n")
                conn.send("Connection: close\n\n")
                conn.sendall(response)
                conn.close()
            elif cssrequest > 4:  # CSS
                response = web_css()
                conn.send("HTTP/1.1 200 OK\n")
                conn.send("Content-Type: text/css\n")
                conn.send("Connection: close\n\n")
                conn.sendall(response)
                conn.close()
            else:  # HTML
                response = web_page()
                conn.send("HTTP/1.1 200 OK\n")
                conn.send("Content-Type: text/html\n")
                conn.send("Connection: close\n\n")
                conn.sendall(response)
                conn.close()
        except:
            conn.close()


JSONdata = """
{
    "button_red": "-x-",
    "button_white": "-x-",
    "LED_brightness": "-x-",
    "LED_roof": "-x-"
}
"""


def set_JSON(status1, status2):
    global JSONdata
    global Brightness
    s1 = '{\n"button_red":"' + str(Light_R) + '",\n'
    s2 = '"button_white":"' + str(Light_W) + '",\n'
    s3 = '"LED_brightness":"' + str(Brightness) + '",\n'
    s4 = '"LED_roof":"' + "NA" + '"\n}\n'
    JSONdata = s1 + s2 + s3 + s4


# Webserver end =========================================================================================================

def do_a_blink(status):
    led.value(status)
#    sleep_ms(200)
#    led.value(0)


def debug(level, cnt, text):
    global DebugLevel
    if level <= DebugLevel:
        print(f"{str(cnt)} {str(text)}")


def strips_update_Brightness():
    global ColorSollwerte
    global ColorRGB
    global Brightness
    global Fade_speed
    if Light_W == "ON":
        # set Brightness to Sollwerte
        ColorSollwerte = [Brightness, Brightness, Brightness]
        # print(f"Brightness White Changed: {Brightness}")
    elif Light_R == "ON":
        ColorSollwerte = [Brightness, 0, 0]
        # print(f"Brightness Red Changed: {Brightness}") # set Brightness to Sollwerte

    for i in range(len(ColorRGB)):
        # print ("rgb:{} rgb:{}",str(ColorRGB[i]),str(ColorSollwerte[i]))
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
    debug(2, Button_Counter, txt)
    set_JSON(Light_W, Light_R)


def Button_R_switch():
    global Light_W
    global Light_R
    global ColorSollwerte
    global Brightness
    global Button_Counter
    txt = Button_R_switch
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
    debug(2, Button_Counter, txt)
    set_JSON(Light_W, Light_R)


# init callback function and iterrupts
Button_W = debounced_Button(13)
Button_R = debounced_Button(10)

# button part end =========================================================================================================


def RotaryController():
    global Light_W
    global Light_R
    global rotary_val_old
    global rotarySwitch
    global Brightness
    if Light_W == "ON" or Light_R == "ON":  # only if at least one switch is on
        r_value = r.get_rotary_encoder(rotarySwitch, rotary_val_old)
        if r_value != None:  # somehow zero means None ?
            Brightness = (
                2**r_value
            )  # tranlate 16 steps to 255 color-steps and set limits
        else:
            pass
        # print(f"Brightness update ={Brightness} = {r_value}")


def LEDfadeTimer(timer0):
    strips_update_Brightness()


def RotaryControllerTimer(timer1):
    RotaryController()

def ButtonDebounceTimer(timer0):
    global Button_W
    global Button_R
    global Button_W_Status
    global Button_R_Status
    b3 = Button_W.get_oldstatus()
    b4 = Button_R.get_oldstatus()
    b1 = Button_W.get_status()
    b2 = Button_R.get_status()
    if b3 != b1 :
        print(f"Button_W_Status={Button_W_Status}, Button_R_Status={Button_R_Status}")
        Button_W_Status=b1
        Button_W_switch()
    if  b4 != b2:
        print(f"Button_W_Status={Button_W_Status}, Button_R_Status={Button_R_Status}")
        Button_R_Status=b2
        Button_R_switch()


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
print("Start Fade Timer")
timer0 = Timer(0)
timer0.init(period=53, mode=Timer.PERIODIC, callback=LEDfadeTimer)

print("Start RotaryController Timer")
timer1 = Timer(1)
timer1.init(period=59, mode=Timer.PERIODIC, callback=RotaryControllerTimer)

print("Start Button Debounce Timer")
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
print("entering mainloop")

Strip1.SetColor(0, 1023, 0)  # give me some green light that init is done ;-)
sleep_ms(1500)
Strip1.SetColor(0, 0, 0)

# while True:

i = 0
while i == 0:
    list = wifi.check_connection()
    for item in list:
        if DebugLevel > 2:
            print(item)
    sleep_ms(60000) # check connection every 60s

