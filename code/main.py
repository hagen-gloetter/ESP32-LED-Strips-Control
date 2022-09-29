# For more details and step by step guide visit: Microcontrollerslab.com

print ("main.py")

#from web_html import web_page
#from web_html import web_css
import machine
import time

from machine import Pin
from time import sleep_ms

from web_html import web_page, web_css
#from debounce_class import Button, button_a_callback, button_b_callback
from debounce_class import Button
from rotary_encoder_class_2 import RotaryIRQ
from pwm_class import LEDStrip

webpage=web_page()
#print (webpage)
webcss=web_css()
#print (webcss)
led = machine.Pin(2, machine.Pin.OUT)
Hue=256
ColorR=0
ColorG=0
ColorB=0
Strip1=LEDStrip(ColorR, ColorG, ColorB, 27,25,32)
Strip1.SetColor(0,0,0)

r = RotaryIRQ(
    pin_num_clk=33,
    pin_num_dt=34,
    min_val=0,
    max_val=16,
    reverse=True,
    range_mode=RotaryIRQ.RANGE_WRAP)
sw = Pin(14, Pin.IN)
val_old = r.value()
isRotaryEncoder = True

def button_a_switch():
    global Light_A
    global Light_B
    if Light_A == "OFF" and Light_B == "OFF":
        Light_A = "ON"
        print("White ON")
        Strip1.SetColor(Hue,Hue,Hue)
    elif Light_A == "ON" and Light_B == "OFF":
        Light_A = "OFF"
        print("White OFF")
        Strip1.SetColor(0,0,0)
        
def button_b_switch():
    global Light_A
    global Light_B
    if Light_B == "OFF" and Light_A == "OFF":
        Light_B = "ON"
        print("Red ON")
        Strip1.SetColor(Hue,0,0)
    elif Light_B == "OFF" and Light_A == "ON":
        Light_A = "OFF"
        Light_B = "ON"
        print("Red over White ON")
        Strip1.SetColor(Hue,0,0)
    else:
        Light_B = "OFF"
        print("Red OFF")
        Strip1.SetColor(0,0,0)


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
            print(f"Button A (%s) cnt:{Button_A_cnt} status:{Button_A_Status}" % pin)
            button_a_switch()
        else:
            pass
        Button_A_cnt +=1

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
            print(f"Button B (%s) cnt:{Button_B_cnt} status:{Button_B_Status}" % pin)
            button_b_switch()
        else:
            pass
        Button_B_cnt +=1

    
    

BUTTON_A_PIN = const(13)
BUTTON_B_PIN = const(10)
Button_A_Status = "OFF"
Button_A_cnt = 0
Button_B_Status = "OFF"
Button_B_cnt = 0
Light_A = "OFF" # white
Light_B = "OFF" # red

button_a = Button(pin=Pin(BUTTON_A_PIN, mode=Pin.IN, pull=Pin.PULL_UP), trigger=Pin.IRQ_RISING, callback=button_a_callback)
button_b = Button(pin=Pin(BUTTON_B_PIN, mode=Pin.IN, pull=Pin.PULL_UP), trigger=Pin.IRQ_RISING, callback=button_b_callback)





while True:
#    led.value(1)
#    sleep_ms(200)
#    led.value(0)
    
    r_value = r.get_rotary_encoder(sw, val_old)
    if r_value != None:
        if val_old==16 and r_value==0:
            r_value=16 # fix overflow
        if val_old==0 and r_value==16:
            r_value=0
        val_old = r_value

        Hue=r_value*16 # tranlate 16 steps to 255 color-steps
        if Hue>256:
            Hue=256
        if Hue<1:
            Hue=0
        print(f"Hue={Hue}")
    sleep_ms(200)
#    print ("colorwheel")
#    Strip1.SetColor(255,0,0)
#    sleep_ms(1000)
#    Strip1.SetColor(0,255,0)
#    sleep_ms(1000)
#    Strip1.SetColor(0,0,255)
#    sleep_ms(1000)
#    Strip1.SetColor(255,255,255)
#    sleep_ms(1000)
 

#    if isRotaryEncoder == True:
#        val_new = r.value()
#        if val_old != val_new:
#            val_old = val_new
#            print('result = {}'.format(val_new))

    


