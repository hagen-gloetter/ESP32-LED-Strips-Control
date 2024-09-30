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
        self.oldstatus = self.status
        self.longpress = 0 
        self.xtremelongpress = 0 

    def get_status(self):
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
            print("button longpress")
            self.longpress += 1
        if self.cnt >= self.debounceTime*200: # default 50*200 = 10 s
            print("button xtremelongpress")
            self.xtremelongpress += 1 
            self.cnt = self.debounceTime*500  # prevent buffer overflow
        return self.status

    def get_oldstatus(self):
        return self.oldstatus

    def get_longpress(self):
        return self.longpress

    def get_xtremelongpress(self):
        return self.xtremelongpress

    def togglebutton(self):
        if self.status == "OFF":
            self.status = "ON"
        else:
            self.status = "OFF"
        return self.status

global Button1
global Button2

def ButtonDebounceTimer(timer0):
    global Button1
    global Button2
    b3 = Button1.get_oldstatus()
    b4 = Button2.get_oldstatus()
    b1 = Button1.get_status()
    b2 = Button2.get_status()
    if b3 != b1 or b4 != b2:
        print(f"b1={b1}, b2={b2}")
    if Button1.get_longpress() > 0 :
        print("Button1 longpress")
    if Button2.get_longpress() > 0 :
        print("Button2 longpress")



def main():
    global Button1
    global Button2
    Button1 = debounced_Button(13)
    Button2 = debounced_Button(10)
    Button3 = debounced_Button(14)
    viaTimer=False
    if viaTimer==True:
        print("Start Timer")
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
                print(f"b1={b1}, b2={b2}")
            if Button1.get_longpress() > 0 :
                print("Button1 longpress")
            if Button2.get_longpress() > 0 :
                print("Button2 longpress")
if __name__ == '__main__':
    sys.exit(main())

print('Button init done')


