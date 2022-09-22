
from machine import Pin, Timer
import time


def on_pressed(timer):
    print('pressed 1')

def on_pressed2(timer):
    print('pressed 2')


def debounce1(pin):
#    print (pin)
    # Start or replace a timer for 200ms, and trigger on_pressed.
    timer1.init(mode=Timer.ONE_SHOT, period=200, callback=on_pressed)

def debounce2(pin):
#    print (pin)
    # Start or replace a timer for 200ms, and trigger on_pressed.
    timer2.init(mode=Timer.ONE_SHOT, period=200, callback=on_pressed2)

# Register a new hardware timer.
timer1 = Timer(0)
timer2 = Timer(1)

# Setup the button input pin with a pull-up resistor.
button1 = Pin(35, Pin.IN, Pin.PULL_UP)
button2 = Pin(34, Pin.IN, Pin.PULL_UP)

# Register an interrupt on rising button input.
button1.irq(debounce1, Pin.IRQ_RISING)
button2.irq(debounce2, Pin.IRQ_RISING)

while True:
    time.sleep(1.2)
    print (".")