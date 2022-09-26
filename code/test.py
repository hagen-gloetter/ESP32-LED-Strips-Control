#from web_html import web_page
#from web_html import web_css
import machine
import time

from machine import Pin
from time import sleep_ms

from web_html import web_page, web_css
from debounce_class import Button
from rotary_encoder import get_rotary_encoder

webpage=web_page()
#print (webpage)
webcss=web_css()
#print (webcss)
led = machine.Pin(2, machine.Pin.OUT)
while True:
    led.value(1)
    sleep_ms(200)
    led.value(0)
    sleep_ms(200)
    get_rotary_encoder()

    
