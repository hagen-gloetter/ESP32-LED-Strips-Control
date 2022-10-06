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
Brightness = 256

ColorRGB=[0,0,0]
ColorSollwerte = [0,0,0]

Strip1 = LEDStrip(ColorRGB[0], ColorRGB[1], ColorRGB[2], 27, 25, 32)    # TODO  Listen übergeben
Strip1.SetColor(ColorRGB[0], ColorRGB[1], ColorRGB[2])
Strip2 = LEDStrip(ColorRGB[0], ColorRGB[1], ColorRGB[2], 17, 21, 22)
Strip2.SetColor(ColorRGB[0], ColorRGB[1], ColorRGB[2])

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

def strips_update_Brightness():
    global ColorSollwerte
    global Brightness
    if Light_W == "ON":
        ColorSollwerte=[Brightness,Brightness,Brightness] # set Brightness to Sollwerte
        print(f"Brightness White Changed: {Brightness}")
    elif Light_R == "ON":
        ColorSollwerte=[Brightness,0,0]
        print(f"Brightness Red Changed: {Brightness}") # set Brightness to Sollwerte

    for i in range(ColorRGB):
        if ColorRGB[i] > ColorSollwerte[i]: # fade in
            ColorRGB[i] += 1
        elif ColorRGB[i] < ColorSollwerte[i] # fade out
            ColorRGB[i] -= 1
        else:
            pass # values are equal
    Strip1.SetColor(ColorRGB[0], ColorRGB[2], ColorRGB[2]) # TODO: LIST as Parameter
    Strip2.SetColor(ColorRGB[0], ColorRGB[2], ColorRGB[2])
    set_JSON(Light_W,Light_R)
        
def set_JSON(status1, status2):
    global JSONdata
    global Brightness
    s1='{\n"button_red":"'  +  str(Light_R) + '",\n'
    s2='"button_white":"'   +  str(Light_W) + '",\n'
    s3='"LED_brightness":"' +  str(Brightness) + '",\n'
    s4='"LED_roof":"'       +  "NA" + '"\n}\n'
    JSONdata=s1+s2+s3+s4

def Button_W_switch():
    global Light_W
    global Light_R
    global ColorSollwerte
    global Brightness
    if Light_W == "OFF" and Light_R == "OFF":
        Light_W = "ON"
        print("White ON")
#        Strip1.SetColor(Brightness, Brightness, Brightness)
#        Strip2.SetColor(Brightness, Brightness, Brightness)
        ColorSollwerte=[Brightness,Brightness,Brightness]
    elif Light_W == "ON" and Light_R == "OFF":
        Light_W = "OFF"
        print("White OFF")
#        Strip1.SetColor(0, 0, 0)
#        Strip2.SetColor(0, 0, 0)
#        ColorSollwerte=[0,0,0]
        ColorSollwerte=[0,0,0]
    set_JSON(Light_W,Light_R)

def Button_R_switch():
    global Light_W
    global Light_R
    global ColorSollwerte
    if Light_R == "OFF" and Light_W == "OFF":
        Light_R = "ON"
        print("Red ON")
#        Strip1.SetColor(Brightness, 0, 0)
#        Strip2.SetColor(Brightness, 0, 0)
        ColorSollwerte=[Brightness,0,0]
    elif Light_R == "OFF" and Light_W == "ON":
        Light_W = "OFF"
        Light_R = "ON"
        print("Red over White ON")
#        Strip1.SetColor(Brightness, 0, 0)
#        Strip2.SetColor(Brightness, 0, 0)
        ColorSollwerte=[0,0,0]      
    else:
        Light_R = "OFF"
        print("Red OFF")
 #       Strip1.SetColor(0, 0, 0)
 #       Strip2.SetColor(0, 0, 0)
        ColorSollwerte=[0,0,0]      
    set_JSON(Light_W,Light_R)

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
            print(
                f"Button A (%s) cnt:{Button_W_cnt} status:{Button_W_Status}" % pin)
            Button_W_switch()
        else:
            pass
        Button_W_cnt += 1


def Button_R_callback(pin):
    global Button_R_cnt
    global Button_R_Status
    if pin.value() == 1:
        Button_R_cnt %= 2
        if Button_R_cnt == 1:
            #            Button_R_cnt = 0
            if Button_R_Status == "ON":
                Button_R_Status = "OFF"
            else:
                Button_R_Status = "ON"
            print(
                f"Button B (%s) cnt:{Button_R_cnt} status:{Button_R_Status}" % pin)
            Button_R_switch()
        else:
            pass
        Button_R_cnt += 1


Button_W_PIN = const(13)
Button_R_PIN = const(10)
Button_W_Status = "OFF"
Button_W_cnt = 0
Button_R_Status = "OFF"
Button_R_cnt = 0
Light_W = "OFF"  # white
Light_R = "OFF"  # red

Button_W = Button(pin=Pin(Button_W_PIN, mode=Pin.IN, pull=Pin.PULL_UP),
                  trigger=Pin.IRQ_RISING, callback=Button_W_callback)
Button_R = Button(pin=Pin(Button_R_PIN, mode=Pin.IN, pull=Pin.PULL_UP),
                  trigger=Pin.IRQ_RISING, callback=Button_R_callback)

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
strips_update_Brightness()
set_JSON(Light_W,Light_R)

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
    if Light_W=="ON" or Light_R=="ON": # only if at least one switch is on
        r_value = r.get_rotary_encoder(sw, val_old)
        if r_value != None:
            if val_old == 16 and r_value < 2: # cant turn more thab 3 steps in one turn 
                r_value = 16  # fix overflow
            if val_old == 0 and r_value > 13:  # cant turn more thab 3 steps in one turn
                r_value = 0
            val_old = r_value
            Brightness = r_value*16  # tranlate 16 steps to 255 color-steps and set limits
    if Brightness > 256:
        Brightness = 255
    if Brightness < 1:
        Brightness = 0
    print(f"Brightness update ={Brightness}")
    strips_update_Brightness()
    sleep_ms(20)
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


