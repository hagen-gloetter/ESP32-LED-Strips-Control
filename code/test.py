#from web_html import web_page
#from web_html import web_css
import machine
import time

from machine import Pin
from time import sleep_ms

from web_html import web_page, web_css
from debounce_class import Button, button_a_callback, button_b_callback
from rotary_encoder_class_2 import RotaryIRQ
from pwm_class import PWM

webpage=web_page()
#print (webpage)
webcss=web_css()
#print (webcss)
led = machine.Pin(2, machine.Pin.OUT)
#r = Rotary(pin_num_clk=33,
#    pin_num_dt=34,
#    min_val=1,
#    max_val=255,
#    reverse=True,
#    range_mode=RotaryIRQ.RANGE_WRAP)
ColorR=255
ColorG=0
ColorB=0
Strip1=PWM(ColorR, ColorG, ColorB, 27,25,32)
Strip1.SetColor(0,0,0)

r = RotaryIRQ(
    pin_num_clk=33,
    pin_num_dt=34,
    min_val=1,
    max_val=255,
    reverse=True,
    range_mode=RotaryIRQ.RANGE_WRAP)
sw = Pin(14, Pin.IN)
val_old = r.value()
isRotaryEncoder = True

BUTTON_A_PIN = const(10)
BUTTON_B_PIN = const(13)
button_a = Button(pin=Pin(BUTTON_A_PIN, mode=Pin.IN, pull=Pin.PULL_UP), trigger=Pin.IRQ_RISING, callback=button_a_callback)
button_b = Button(pin=Pin(BUTTON_B_PIN, mode=Pin.IN, pull=Pin.PULL_UP), trigger=Pin.IRQ_RISING, callback=button_b_callback)

while True:
#    led.value(1)
#    sleep_ms(200)
#    led.value(0)
    
    r_value = r.get_rotary_encoder(sw, val_old)
    if r_value != None:
        print(r_value)
        val_old = r_value
    
    sleep_ms(1000)
    Strip1.SetColor(255,0,0)
    sleep_ms(1000)
    Strip1.SetColor(0,255,0)
    sleep_ms(1000)
    Strip1.SetColor(0,0,255)
    sleep_ms(1000)
    Strip1.SetColor(255,255,255)


#    if isRotaryEncoder == True:
#        val_new = r.value()
#        if val_old != val_new:
#            val_old = val_new
#            print('result = {}'.format(val_new))

    

