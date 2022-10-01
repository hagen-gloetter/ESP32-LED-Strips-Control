# For more details and step by step guide visit: Microcontrollerslab.com

from pwm_class import LEDStrip
from rotary_encoder_class_2 import RotaryIRQ
from debounce_class import Button
from web_html import web_page, web_css
from time import sleep_ms
from machine import Pin
import _thread
import time
import machine
import gc

print("main.py")

#from web_html import web_page
#from web_html import web_css

led = machine.Pin(2, machine.Pin.OUT)
Hue = 256
ColorR = 0
ColorG = 0
ColorB = 0
Strip1 = LEDStrip(ColorR, ColorG, ColorB, 27, 25, 32)
Strip1.SetColor(0, 0, 0)
Strip2 = LEDStrip(ColorR, ColorG, ColorB, 17, 21, 22)
Strip2.SetColor(0, 0, 0)

r = RotaryIRQ(pin_num_clk=33, pin_num_dt=34, min_val=0, max_val=16,
              reverse=True, range_mode=RotaryIRQ.RANGE_WRAP)
sw = Pin(14, Pin.IN)
val_old = r.value()
isRotaryEncoder = True

JSONdata="""
{
    "button_red": "-x-",
    "button_white": "-x-",
    "LED_brightness": "-x-",
    "LED_roof": "-x-"
}
"""
led.value(1)
sleep_ms(200)
led.value(0)

def strips_update_hue():
    if Light_A == "ON":
        Strip1.SetColor(Hue, Hue, Hue)
        Strip2.SetColor(Hue, Hue, Hue)
        print(f"Hue White Changed: {Hue}")
    elif Light_B == "ON":
        Strip1.SetColor(Hue, 0, 0)
        Strip2.SetColor(Hue, 0, 0)
        print(f"Hue Red Changed: {Hue}")
    set_JSON(Light_A,Light_B)
        
def set_JSON(status1, status2):
    global JSONdata
    global Hue
    s1='{\n"button_red":"'  +  str(Light_B) + '",\n'
    s2='"button_white":"'   +  str(Light_A) + '",\n'
#    s3='"LED_brightness":"' +  " R="+ str(ColorR) + " G="+ str(ColorG) + " B="+ str(ColorB) +'",\n'
    s3='"LED_brightness":"' +  str(Hue) + '",\n'
    s4='"LED_roof":"'       +  "NA" + '"\n}\n'
    JSONdata=s1+s2+s3+s4

def button_a_switch():
    global Light_A
    global Light_B
    if Light_A == "OFF" and Light_B == "OFF":
        Light_A = "ON"
        print("White ON")
        Strip1.SetColor(Hue, Hue, Hue)
        Strip2.SetColor(Hue, Hue, Hue)
    elif Light_A == "ON" and Light_B == "OFF":
        Light_A = "OFF"
        print("White OFF")
        Strip1.SetColor(0, 0, 0)
        Strip2.SetColor(0, 0, 0)
    set_JSON(Light_A,Light_B)

def button_b_switch():
    global Light_A
    global Light_B
    if Light_B == "OFF" and Light_A == "OFF":
        Light_B = "ON"
        print("Red ON")
        Strip1.SetColor(Hue, 0, 0)
        Strip2.SetColor(Hue, 0, 0)
    elif Light_B == "OFF" and Light_A == "ON":
        Light_A = "OFF"
        Light_B = "ON"
        print("Red over White ON")
        Strip1.SetColor(Hue, 0, 0)
        Strip2.SetColor(Hue, 0, 0)
    else:
        Light_B = "OFF"
        print("Red OFF")
        Strip1.SetColor(0, 0, 0)
        Strip2.SetColor(0, 0, 0)
    set_JSON(Light_A,Light_B)


def button_a_callback(pin):
    global Button_A_cnt
    global Button_A_Status
    if pin.value() == 1:
        if Button_A_cnt % 2 == 0:
            Button_A_cnt = 0
            if Button_A_Status == "ON":
                Button_A_Status = "OFF"
            else:
                Button_A_Status = "ON"
            print(
                f"Button A (%s) cnt:{Button_A_cnt} status:{Button_A_Status}" % pin)
            button_a_switch()
        else:
            pass
        Button_A_cnt += 1


def button_b_callback(pin):
    global Button_B_cnt
    global Button_B_Status
    if pin.value() == 1:
        Button_B_cnt %= 2
        if Button_B_cnt == 1:
            #            Button_B_cnt = 0
            if Button_B_Status == "ON":
                Button_B_Status = "OFF"
            else:
                Button_B_Status = "ON"
            print(
                f"Button B (%s) cnt:{Button_B_cnt} status:{Button_B_Status}" % pin)
            button_b_switch()
        else:
            pass
        Button_B_cnt += 1


BUTTON_A_PIN = const(13)
BUTTON_B_PIN = const(10)
Button_A_Status = "OFF"
Button_A_cnt = 0
Button_B_Status = "OFF"
Button_B_cnt = 0
Light_A = "OFF"  # white
Light_B = "OFF"  # red

button_a = Button(pin=Pin(BUTTON_A_PIN, mode=Pin.IN, pull=Pin.PULL_UP),
                  trigger=Pin.IRQ_RISING, callback=button_a_callback)
button_b = Button(pin=Pin(BUTTON_B_PIN, mode=Pin.IN, pull=Pin.PULL_UP),
                  trigger=Pin.IRQ_RISING, callback=button_b_callback)

# button part end =========================================================================================================


def thread_webserver(delay, name):
    time.sleep(delay) # slowstart webserver
    while True:
        sleep_ms(233)
        print(f'Running thread {name}' )
        # print webpage =========================================================================================================
        conn, addr = s.accept()
        #print('Got a connection from %s' % str(addr)) 
        request = conn.recv(1024)
        request = str(request)
        #print('Content = %s' % request)
        led_on = request.find('/?led=on')
        led_off = request.find('/?led=off')
        if led_on == 6:
            #print('LED ON')
            led.value(1)
        if led_off == 6:
            #print('LED OFF')
            led.value(0)
        jsonrequest = request.find('data.json')
        cssrequest = request.find('web.css')
        if jsonrequest > 4: 
            response = JSONdata
            conn.send('HTTP/1.1 200 OK\n')
            conn.send('Content-Type: application/json\n')
            conn.send('Connection: close\n\n')
            conn.sendall(response)
            conn.close()
        
        elif cssrequest > 4: 
            response = web_css()
            conn.send('HTTP/1.1 200 OK\n')
            conn.send('Content-Type: text/css\n')
            conn.send('Connection: close\n\n')
            conn.sendall(response)
            conn.close()
        else:
            response = web_page()
            conn.send('HTTP/1.1 200 OK\n')
            conn.send('Content-Type: text/html\n')
            conn.send('Connection: close\n\n')
            conn.sendall(response)
            conn.close()

try:
    import usocket as socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 80))
    s.listen(5)
except:
    import socket

Strip1.SetColor(0,0,0)
Strip2.SetColor(0,0,0)
strips_update_hue()
set_JSON(Light_A,Light_B)

#_thread.start_new_thread(thread_webserver,( 4, "webserver"))
#debug no thread
#thread_webserver(4,"webserver")
led.value(1)
toggle=1
cnt=0
while True:
    led.value(toggle)
    #    sleep_ms(200)
    #    led.value(0)

    r_value = r.get_rotary_encoder(sw, val_old)
    if r_value != None:
        if val_old == 16 and r_value == 0:
            r_value = 16  # fix overflow
        if val_old == 0 and r_value == 16:
            r_value = 0
        val_old = r_value

        Hue = r_value*16  # tranlate 16 steps to 255 color-steps
        if Hue > 256:
            Hue = 255
        if Hue < 1:
            Hue = 0
        print(f"Hue={Hue}")
        strips_update_hue()
    sleep_ms(200)
    cnt +=1
    if cnt == 5:
        print ("main loop")
        cnt=0
        if toggle == 0:
            toggle = 1
        else:
            toggle = 0
            gc.collect()

#    print ("colorwheel")
#    Strip1.SetColor(255,0,0)
#    sleep_ms(1000)
#    Strip1.SetColor(0,255,0)
#    sleep_ms(1000)
#    Strip1.SetColor(0,0,255)
#    sleep_ms(1000)
#    Strip1.SetColor(255,255,255)
#    sleep_ms(1000)


