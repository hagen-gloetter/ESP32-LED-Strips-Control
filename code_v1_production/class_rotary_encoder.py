# The MIT License (MIT)
# Copyright (c) 2020 Mike Teachman
# https://opensource.org/licenses/MIT

# Platform-specific MicroPython code for the rotary encoder module
# ESP8266/ESP32 implementation

# Documentation:
#   https://github.com/MikeTeachman/micropython-rotary

from machine import Pin
from rotary import Rotary
from sys import platform
from time import sleep_ms
from class_debug import debug

class RotaryIRQ(Rotary):

    def __init__(self, pin_num_clk, pin_num_dt, min_val=0, max_val=10, reverse=False, range_mode=Rotary.RANGE_UNBOUNDED, pull_up=False, half_step=False, invert=False):

        super().__init__(min_val, max_val, reverse, range_mode, half_step, invert)

        if pull_up == True:
            self._pin_clk = Pin(pin_num_clk, Pin.IN, Pin.PULL_UP)
            self._pin_dt = Pin(pin_num_dt, Pin.IN, Pin.PULL_UP)
        else:
            self._pin_clk = Pin(pin_num_clk, Pin.IN)
            self._pin_dt = Pin(pin_num_dt, Pin.IN)

        self._enable_clk_irq(self._process_rotary_pins)
        self._enable_dt_irq(self._process_rotary_pins)

    def _enable_clk_irq(self, callback=None):
        self._pin_clk.irq(
            trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING,
            handler=callback)

    def _enable_dt_irq(self, callback=None):
        self._pin_dt.irq(
            trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING,
            handler=callback)

    def _disable_clk_irq(self):
        self._pin_clk.irq(handler=None)

    def _disable_dt_irq(self):
        self._pin_dt.irq(handler=None)

    def _hal_get_clk_value(self):
        return self._pin_clk.value()

    def _hal_get_dt_value(self):
        return self._pin_dt.value()

    def _hal_enable_irq(self):
        self._enable_clk_irq(self._process_rotary_pins)
        self._enable_dt_irq(self._process_rotary_pins)

    def _hal_disable_irq(self):
        self._disable_clk_irq()
        self._disable_dt_irq()

    def _hal_close(self):
        self._hal_disable_irq()
        
    def get_rotary_encoder(self, sw, val_old):
        global isRotaryEncoder
#        global sw
#        if sw.value() == 1:
#            isRotaryEncoder = not isRotaryEncoder
#            if isRotaryEncoder == True:
#                debug(4, __name__, 'Rotary Encoder is now enabled.')
#            else:
#                debug(4, __name__, 'Rotary Encoder is now disabled.')
#        if sw.value() == 0:
#            isRotaryEncoder = not isRotaryEncoder
#            if isRotaryEncoder == True:
#                debug(4, __name__, 'Rotary Encoder is now enabled.')
#            else:
#                debug(4, __name__, 'Rotary Encoder is now disabled.')
        if isRotaryEncoder == True:
#            global val_old
            val_new = self.value()
            if val_old != val_new:
                val_old = val_new
                #debug(4, __name__, 'result = {}'.format(val_new))
                return val_new
        
#r = RotaryIRQ(
#    pin_num_clk=33,
#    pin_num_dt=34,
#    min_val=1,
#    max_val=255,
#    reverse=True,
#    range_mode=RotaryIRQ.RANGE_WRAP)

#sw = Pin(14, Pin.IN)
#sw_val_old = sw.value()
#val_old = r.value()

isRotaryEncoder = True

#while True:
#    r.get_rotary_encoder()
#    sleep_ms(200)