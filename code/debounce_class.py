import time
from micropython import const
from machine import Pin
import sys
from time import sleep_ms
import machine
led = machine.Pin(2, machine.Pin.OUT)

Button_W_PIN = const(13)
Button_R_PIN = const(10)
Button_W_Status = "OFF"
Button_W_cnt = 0
Button_R_Status = "OFF"
Button_R_cnt = 0
Light_W = "OFF" # white
Light_R = "OFF" # red

Button_W=None
Button_R=None


print('Debounce Class loaded')
# based on https://gist.github.com/jedie/8564e62b0b8349ff9051d7c5a1312ed7
#  based on https://blog.csdn.net/xinshuwei/article/details/123112633

class Button:
    def __init__(self, pin, callback, trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, min_ago=400):
        self.callback = callback
        self.min_ago = min_ago
        self._is_pressed = True
        self._next_call = time.ticks_ms() + self.min_ago 
        pin.irq(trigger=trigger, handler=self.debounce_handler)
        self._is_pressed = False
    def call_callback(self, pin):
        print ("call_callback")
        self._is_pressed = True
        if self.callback is not None:
            self.callback(pin)
    def debounce_handler(self, pin):
        print (f"debounce_handler {time.ticks_ms()} {self._next_call}")
        if time.ticks_ms() > self._next_call:
        #if time.ticks_diff(time.ticks_ms(), self._next_call) > 0:
            self._next_call = time.ticks_ms() + self.min_ago
            #self._next_call = time.ticks_add(time.ticks_ms(), self.min_ago)
            print (f"debounce_handler2 {time.ticks_add(time.ticks_ms(), self.min_ago)} ")
            self.call_callback(pin)
    def value(self):
        p = self._is_pressed
        self._is_pressed=False
        return p

DebugLevel=4
ColorSollwerte=None
Brightness = 0
Button_Counter=0

def debug(level, cnt, text):
    global DebugLevel
    if level <= DebugLevel:
        print(f"{str(cnt)} {str(text)}")

def Button_W_switch():
    global Light_W
    global Light_R
    global ColorSollwerte
    global Brightness
    global Button_Counter
    txt = "Button_W_switch"
    if Light_R == "ON":
        Light_W = "OFF"
        Button_Counter += 1
        txt = "Button_W_switch: White IGNORE - Red over White"
    elif Light_W == "OFF" and Light_R == "OFF":
        Light_W = "ON"
        Button_Counter += 1
        txt = "Button_W_switch: White ON"
        ColorSollwerte = [Brightness, Brightness, Brightness]
    elif Light_W == "ON" and Light_R == "OFF":
        Light_W = "OFF"
        Button_Counter += 1
        txt = "Button_W_switch: White OFF"
        ColorSollwerte = [0, 0, 0]
    else:
        txt = "Button_W_switch: Else Case ERROR Red=" + Light_R + " white="+Light_W
    debug(2, Button_Counter, txt)
    #set_JSON(Light_W, Light_R)


def Button_R_switch():
    global Light_W
    global Light_R
    global ColorSollwerte
    global Brightness
    global Button_Counter
    txt = Button_R_switch
    if Light_R == "OFF" and Light_W == "OFF":
        Light_R = "ON"
        Light_W = "OFF"  # just 2b sure
        Button_Counter += 1
        txt = "Button_R_switch: Red ON"
        ColorSollwerte = [Brightness, 0, 0]
        do_a_blink(1)
    elif Light_R == "OFF" and Light_W == "ON":
        Light_R = "ON"
        Light_W = "OFF"
        Button_Counter += 1
        txt = "Button_R_switch: Red over White ON"
        ColorSollwerte = [Brightness, 0, 0]  # TODO check if this is right
        do_a_blink(1)
    elif Light_R == "ON":
        Light_R = "OFF"
        Button_Counter += 1
        txt = "Button_R_switch: Red OFF"
        ColorSollwerte = [0, 0, 0]
        do_a_blink(0)
    else:
        txt = "Button_R_switch: Else Case ERROR Red=" + Light_R + " white="+Light_W
    debug(2, Button_Counter, txt)
    #set_JSON(Light_W, Light_R)

def Button_W_callback(pin):
    global Button_W_cnt
    global Button_W
    p1=Button_W.value()
    sleep_ms(100)
    p2=Button_W.value()
    if  p1 == True and p2==False:
        Button_W_switch()
        Button_W_cnt +=1

def Button_R_callback(pin):
    global Button_R_cnt
    sleep_ms(100)
    if Button_R.value() == True:
        Button_R_switch()
        Button_R_cnt +=1

def do_a_blink(status):
    led.value(status)
#    sleep_ms(200)
#    led.value(0)

print('Button init done')

def main():
    global Button_W
    global Button_R
#    Button_W = Button(pin=Pin(Button_W_PIN, mode=Pin.IN, pull=Pin.PULL_UP), trigger=Pin.IRQ_RISING, callback=Button_W_callback)
#    Button_R = Button(pin=Pin(Button_R_PIN, mode=Pin.IN, pull=Pin.PULL_UP), trigger=Pin.IRQ_RISING, callback=Button_R_callback)
    Button_W = Button(pin=Pin(Button_W_PIN, mode=Pin.IN, pull=Pin.PULL_UP), trigger=Pin.IRQ_FALLING, callback=Button_W_callback)
    Button_R = Button(pin=Pin(Button_R_PIN, mode=Pin.IN, pull=Pin.PULL_UP), trigger=Pin.IRQ_FALLING, callback=Button_R_callback)

    i=0
    while i==0:
        #w=Button_W.value() 
        #r=Button_R.value()
        #if r==True or w==True:
        #    print ("w="+ str(w) + " r="+ str(r))
        sleep_ms(1000)


if __name__ == '__main__':
    sys.exit(main())

