import time
from machine import Pin
from machine import Timer
import sys
import machine
led = machine.Pin(2, machine.Pin.OUT)

print('Debounce Class loaded')

class debounced_Button():
    """ Class to debounce a hardware button
    Code: Hagen@gloetter.de 2022
    """

    def __init__(self, pin=10):
        self.pin = Pin(pin, mode=Pin.IN, pull=Pin.PULL_UP)
        self.status = "OFF"
        self.cnt = 0
        self.debounceTime = 5  # x cycles have to be done

    def get_status(self):
        # Button has to be pressed 5 ti
        if self.pin.value() == 0:
            self.cnt += 1
        if self.pin.value() == 1:
            self.cnt = 0
        if self.cnt == self.debounceTime:
            self.status = self.togglebutton()
        if self.cnt >= self.debounceTime*10:
            print("button longpress")
            self.cnt = self.debounceTime*2 # prevent buffer overflow
        return self.status

    def togglebutton(self):
        if self.status == "OFF":
            self.status = "ON"
        else:
            self.status = "OFF"
        return self.status


global Button1
global Button2


def debounceTimer(timer0):
    global Button1
    global Button2
    led.value(not led.value())
    b1 = Button1.get_status()
    b2 = Button2.get_status()
    


def main():
    global Button1
    global Button2
    Button1 = debounced_Button(10)
    Button2 = debounced_Button(13)

    print("Start Timer")
    #mytimer0 = Timer(0)
    #mytimer0.init(period=10, mode=Timer.PERIODIC, callback=debounceTimer)
    i=0
    b1 = Button1.get_status()
    b2 = Button2.get_status()

    while i==0:
        b3 = b1
        b4 = b2
        b1 = Button1.get_status()
        b2 = Button2.get_status()
        time.sleep_ms(10)
        if b3 != b1:
            print(f"b1={b1}, b2={b2}")
        if b4 != b2:
            print(f"b1={b1}, b2={b2}")

if __name__ == '__main__':
    sys.exit(main())

print('Button init done')

