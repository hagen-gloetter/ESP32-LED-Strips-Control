"""
Software button debounce for ESP32 GPIO inputs.

Provides ``debounced_Button`` which needs to be polled at a fixed rate
(e.g. via a 10 ms hardware timer). A button state change is only accepted
after the input has been stable for ``debounceTime`` consecutive polls.

Usage::

    from class_debounce import debounced_Button
    btn = debounced_Button(pin=13)
    # call btn.get_status() every 10 ms (e.g. from a Timer callback)
    if btn.get_status() == "ON":
        ...

Hardware:
    - GPIO configured as input with internal pull-up
    - Active-low wiring (button connects pin to GND)
"""
import time
from machine import Pin
from machine import Timer
import sys
import machine
from class_debug import debug

led = machine.Pin(2, machine.Pin.OUT)

print ( 'Debounce Class loaded')

class debounced_Button():
    """ Class to debounce a hardware button
    Code: Hagen@gloetter.de 2022
    """

    def __init__(self, pin=10):
        """
        Initialise a debounced button on a pull-up input pin.

        Args:
            pin (int): GPIO number used for the button input.

        Returns:
            None
        """
        self.pin = Pin(pin, mode=Pin.IN, pull=Pin.PULL_UP)
        self.status = "OFF"
        self.cnt = 0
        self.debounceTime = 10  # x cycles have to be done (increased for robustness)
        self.oldstatus = self.status
        self.longpress = 0 
        self.xtremelongpress = 0 

    def get_status(self):
        """
        Poll the button pin and return the debounced state.

        Must be called at a regular interval (typically 10 ms via a Timer).
        A transition is registered after ``debounceTime`` consecutive stable
        readings. Long-press and extreme-long-press counters are also updated.

        Returns:
            str: ``"ON"`` or ``"OFF"``.
        """
        # Button has to be pressed 5 cycles
        if self.pin.value() == 0:  # PULL_UP -> 0 = pressed
            self.cnt += 1
        if self.pin.value() == 1:  # PULL_UP -> 1 = not pressed
            self.cnt = 0
            self.longpress = 0
            self.xtremelongpress = 0 
        if self.cnt == self.debounceTime:  # button toggle
            self.status = self.togglebutton()
            self.oldstatus = self.status
        if self.cnt >= self.debounceTime*100: # default 50*100 = 5 s
            debug(4, __name__, "button longpress")
            self.longpress += 1
        if self.cnt >= self.debounceTime*200: # default 50*200 = 10 s
            debug(4, __name__, "button xtremelongpress")
            self.xtremelongpress += 1 
            self.cnt = self.debounceTime*500  # prevent buffer overflow
        return self.status

    def get_oldstatus(self):
        """Return the button state as of the last confirmed transition."""
        return self.oldstatus

    def get_longpress(self):
        """Return the long-press counter (increments once per ~5 s hold)."""
        return self.longpress

    def get_xtremelongpress(self):
        """Return the extreme-long-press counter (increments once per ~10 s hold)."""
        return self.xtremelongpress

    def get_holdcount(self):
        """Return the current hold counter (increments every 10 ms while pressed)."""
        return self.cnt

    def togglebutton(self):
        """
        Toggle the cached ON/OFF state.

        Returns:
            str: The new debounced state.
        """
        if self.status == "OFF":
            self.status = "ON"
        else:
            self.status = "OFF"
        return self.status

global Button1
global Button2

def ButtonDebounceTimer(timer0):
    """
    Poll the demo buttons from a hardware timer callback.

    Args:
        timer0 (Timer): Triggering timer instance.

    Returns:
        None
    """
    global Button1
    global Button2
    b3 = Button1.get_oldstatus()
    b4 = Button2.get_oldstatus()
    b1 = Button1.get_status()
    b2 = Button2.get_status()
    if b3 != b1 or b4 != b2:
        debug(4, __name__, f"b1={b1}, b2={b2}")
    if Button1.get_longpress() > 0 :
        debug(4, __name__, "Button1 longpress")
    if Button2.get_longpress() > 0 :
        debug(4, __name__, "Button2 longpress")



def main():
    """
    Run the standalone debounce test harness.

    Returns:
        None
    """
    global Button1
    global Button2
    Button1 = debounced_Button(13)
    Button2 = debounced_Button(10)
    Button3 = debounced_Button(14)
    viaTimer=False
    if viaTimer==True:
        debug(4, __name__, "Start Timer")
        timer2 = Timer(2)
        timer2.init(period=10, mode=Timer.PERIODIC, callback=ButtonDebounceTimer)
    if viaTimer==False:
        i = 0
        while i==0:
            b3 = Button1.get_oldstatus() # achtung erst den alten Status holen 
            b4 = Button2.get_oldstatus()
            b1 = Button1.get_status()
            b2 = Button2.get_status()
            time.sleep_ms(10)
            if b3 != b1 or b4 != b2:
                debug(4, __name__, f"b1={b1}, b2={b2}")
            if Button1.get_longpress() > 0 :
                debug(4, __name__, "Button1 longpress")
            if Button2.get_longpress() > 0 :
                debug(4, __name__, "Button2 longpress")
if __name__ == '__main__':
    sys.exit(main())

print ('Button init done')



