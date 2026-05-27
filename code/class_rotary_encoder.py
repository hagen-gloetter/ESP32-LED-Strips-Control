"""
ESP32 hardware-interrupt rotary encoder driver.

Extends the platform-independent ``Rotary`` base class with GPIO IRQ
handling. Also provides a convenience method ``get_rotary_encoder()``
that filters repeated values for use in polling loops.

Usage::

    from class_rotary_encoder import RotaryIRQ
    r = RotaryIRQ(pin_num_clk=33, pin_num_dt=34, min_val=0, max_val=10,
                  reverse=True, range_mode=RotaryIRQ.RANGE_BOUNDED)
    old = r.value()
    while True:
        new = r.get_rotary_encoder(sw_pin, old)
        if new is not None:
            old = new

Hardware:
    - CLK pin: GPIO 33 (in main.py)
    - DT  pin: GPIO 34 (in main.py)
    - SW  pin: GPIO 14 (not used inside this class)
"""
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
        """
        Initialise the GPIO-backed rotary encoder driver.

        Args:
            pin_num_clk (int): GPIO number for the CLK signal.
            pin_num_dt (int): GPIO number for the DT signal.
            min_val (int): Minimum encoder value.
            max_val (int): Maximum encoder value.
            reverse (bool): Reverse the rotation direction when True.
            range_mode (int): Rotary range mode from the base class.
            pull_up (bool): Enable internal pull-ups on both inputs.
            half_step (bool): Enable half-step decoding.
            invert (bool): Invert the interpreted direction.

        Returns:
            None
        """

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
        """
        Enable interrupts for the CLK pin.

        Args:
            callback (callable | None): IRQ handler to call on pin changes.

        Returns:
            None
        """
        self._pin_clk.irq(
            trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING,
            handler=callback)

    def _enable_dt_irq(self, callback=None):
        """
        Enable interrupts for the DT pin.

        Args:
            callback (callable | None): IRQ handler to call on pin changes.

        Returns:
            None
        """
        self._pin_dt.irq(
            trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING,
            handler=callback)

    def _disable_clk_irq(self):
        """Disable interrupts for the CLK pin.

        Returns:
            None
        """
        self._pin_clk.irq(handler=None)

    def _disable_dt_irq(self):
        """Disable interrupts for the DT pin.

        Returns:
            None
        """
        self._pin_dt.irq(handler=None)

    def _hal_get_clk_value(self):
        """Return the current logic level of the CLK pin.

        Returns:
            int: ``0`` or ``1``.
        """
        return self._pin_clk.value()

    def _hal_get_dt_value(self):
        """Return the current logic level of the DT pin.

        Returns:
            int: ``0`` or ``1``.
        """
        return self._pin_dt.value()

    def _hal_enable_irq(self):
        """Enable both rotary input IRQs.

        Returns:
            None
        """
        self._enable_clk_irq(self._process_rotary_pins)
        self._enable_dt_irq(self._process_rotary_pins)

    def _hal_disable_irq(self):
        """Disable both rotary input IRQs.

        Returns:
            None
        """
        self._disable_clk_irq()
        self._disable_dt_irq()

    def _hal_close(self):
        """Release hardware resources used by the encoder.

        Returns:
            None
        """
        self._hal_disable_irq()

    def set_enabled(self, is_enabled):
        """
        Enable or disable encoder IRQ processing.

        Args:
            is_enabled (bool): When True the encoder IRQs are active.

        Returns:
            None
        """
        if is_enabled:
            self._hal_enable_irq()
        else:
            self._hal_disable_irq()
        
    def get_rotary_encoder(self, sw, val_old, is_enabled=True):
        """
        Return the current encoder value if it changed since *val_old*.

        Args:
            sw (Pin): The rotary encoder push-button pin (reserved for
                future enable/disable toggle; currently unused).
            val_old (int): The previously seen encoder value.
            is_enabled (bool): When False the encoder is ignored and
                ``None`` is always returned.

        Returns:
            int | None: New value if the encoder moved, else ``None``.
        """
        if is_enabled:
            val_new = self.value()
            if val_old != val_new:
                val_old = val_new
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