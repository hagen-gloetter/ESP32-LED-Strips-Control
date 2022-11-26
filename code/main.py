# For more details and step by step guide visit: Microcontrollerslab.com

from rotary_encoder_class_2 import RotaryIRQ
from web_html import web_css
from web_html import web_page
from pwm_class import LEDStrip
from debounce_class import Button
from web_html import web_page, web_css
from time import sleep_ms
from machine import Pin
import _thread
import time
import machine
import gc
import network

try:
    import usocket as socket
except:
    import socket
print("main.py start")


# setup LED
led = machine.Pin(2, machine.Pin.OUT)
CPU_Speed = machine.freq()
machine.freq(int(CPU_Speed / 2))
print(f"machine.freq={CPU_Speed}")
# Buttons
Button_W_PIN = const(13)
Button_R_PIN = const(10)
Button_W_Status = "OFF"
Button_R_Status = "OFF"
Button_W_cnt = 0
Button_R_cnt = 0
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

# button part start =========================================================================================================


def Button_W_switch():
    global Light_W
    global Light_R
    global ColorSollwerte
    global Brightness
    if Light_W == "OFF" and Light_R == "OFF":
        Light_W = "ON"
        print("White ON")
        ColorSollwerte = [Brightness, Brightness, Brightness]
    elif Light_W == "ON" and Light_R == "OFF":
        Light_W = "OFF"
        print("White OFF")
        ColorSollwerte = [0, 0, 0]
    set_JSON(Light_W, Light_R)


def Button_R_switch():
    global Light_W
    global Light_R
    global ColorSollwerte
    global Brightness
    if Light_R == "OFF" and Light_W == "OFF":
        Light_R = "ON"
        print("Red ON")
        ColorSollwerte = [Brightness, 0, 0]
    elif Light_R == "OFF" and Light_W == "ON":
        Light_W = "OFF"
        Light_R = "ON"
        print("Red over White ON")
        ColorSollwerte = [Brightness, 0, 0]  # TODO check if this is right
    else:
        Light_R = "OFF"
        print("Red OFF")
        ColorSollwerte = [0, 0, 0]
    set_JSON(Light_W, Light_R)


def Button_W_callback(pin):
    global Button_W_cnt
    global Button_W_Status
    if pin.value() == 1:
        if Button_W_cnt % 2 == 0:
            Button_W_cnt = 0
            if Button_W_Status == "ON":
                Button_W_Status = "OFF"
            else:
                Button_W_Status = "ON"
            print(f"Button A (%s) cnt:{Button_W_cnt} status:{Button_W_Status}" % pin)
            Button_W_switch()
        else:
            pass
        Button_W_cnt += 1


def Button_R_callback(pin):
    global Button_R_cnt
    global Button_R_Status
    if pin.value() == 1:
        if Button_R_cnt % 2 == 0:
            Button_R_cnt = 0
            if Button_R_Status == "ON":
                Button_R_Status = "OFF"
            else:
                Button_R_Status = "ON"
            print(f"Button B (%s) cnt:{Button_R_cnt} status:{Button_R_Status}" % pin)
            Button_R_switch()
        else:
            pass
        Button_R_cnt += 1

def do_a_blink(status):
    led.value(status)
#    sleep_ms(200)
#    led.value(0)

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


# init callback function and iterrupts
Button_W = Button(
    pin=Pin(Button_W_PIN, mode=Pin.IN, pull=Pin.PULL_UP),
    trigger=Pin.IRQ_RISING,
    callback=Button_W_callback
)

Button_R = Button(
    pin=Pin(Button_R_PIN, mode=Pin.IN, pull=Pin.PULL_UP),
    trigger=Pin.IRQ_RISING,
    callback=Button_R_callback
)

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


def LEDfadeTimer(timer1):
    strips_update_Brightness()


def RotaryControllerTimer(timer2):
    RotaryController()

def stop_all():
    Strip1.SetColor(0, 1023, 0)  # give me some light that init is done ;-)
    sleep_ms(500)
    Strip1.SetColor(0, 1023, 1023)
    sleep_ms(500)
    Strip1.SetColor(0, 0, 0)
    # shut it down
    global run_webserver
    run_webserver = False
    timer2.deinit()
    timer1.deinit()
    import get_wifi_connection

    global wifi
    get_wifi_connection.disconnect_wifi()




# Run LED Fading via timer interrupt (smoother than MainLoop)
print("Start Fade Timer")
timer1 = machine.Timer(0)
timer1.init(period=53, mode=machine.Timer.PERIODIC, callback=LEDfadeTimer)

print("Start RotaryController Timer")
timer2 = machine.Timer(1)
timer2.init(period=59, mode=machine.Timer.PERIODIC, callback=RotaryControllerTimer)


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
import time

Strip1.SetColor(0, 1023, 0)  # give me some green light that init is done ;-)
sleep_ms(200)
Strip1.SetColor(0, 0, 0)

while True:
#    led.value(toggle)
#    do_a_blink(toggle)
#    sleep_ms(200)
#    led.value(0)

#    sleep_ms(10)

#    cnt += 1
#    machine.idle()
#    time1=time.time()
#    thread_webserver(4,"webserver")
#    print ("RUNTIME: " , str( (time.time() - time1) ))
#    if cnt == 60000:
#        print ("main loop")
#        cnt = 0
#       if toggle == 0:
#            toggle = 1
#        else:
#            toggle = 0
#            gc.collect()
    do_a_blink(0)
    print ("colorwheel R")
    Strip1.SetColor(1023,0,0)
    sleep_ms(1000)
    do_a_blink(1)
    print ("colorwheel G")
    Strip1.SetColor(0,1023,0)
    sleep_ms(1000)
    do_a_blink(0)
    print ("colorwheel B")
    Strip1.SetColor(0,0,1023)
    sleep_ms(1000)
    print ("colorwheel White")
    Strip1.SetColor(1023,1023,1023)
    sleep_ms(1000)
    print ("colorwheel Black")
    Strip1.SetColor(1023,1023,1023)
    sleep_ms(1000)
    print ("colorwheel White")
    Strip1.SetColor(1023,1023,1023)
    sleep_ms(1000)
    print ("colorwheel Black")
    Strip1.SetColor(1023,1023,1023)
    sleep_ms(1000)
