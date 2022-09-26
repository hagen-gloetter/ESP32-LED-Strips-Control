import time
from micropython import const
from machine import Pin

BUTTON_A_PIN = const(35)
BUTTON_B_PIN = const(39)

class Button:
    def __init__(self, pin, callback, trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, min_ago=100):
        self.callback = callback
        self.min_ago = min_ago
        self._blocked = False
        self._next_call = time.ticks_ms() + self.min_ago
        pin.irq(trigger=trigger, handler=self.debounce_handler)
    def call_callback(self, pin):
        self.callback(pin)
    def debounce_handler(self, pin):
        if time.ticks_ms() > self._next_call:
            self._next_call = time.ticks_ms() + self.min_ago
            self.call_callback(pin)

def button_a_callback(pin):
    if pin.value() == 0:
        print("Button A (%s) LONG PRESSED" % pin)

def button_b_callback(pin):
    print("Button B (%s) changed to: %r" % (pin, pin.value()))

#button_a = Button(pin=Pin(BUTTON_A_PIN, mode=Pin.IN), callback=button_a_callback)
button_a = Button(pin=Pin(BUTTON_A_PIN, mode=Pin.IN, pull=Pin.PULL_UP), callback=button_a_callback)
button_b = Button(pin=Pin(BUTTON_B_PIN, mode=Pin.IN, pull=Pin.PULL_UP), callback=button_b_callback)