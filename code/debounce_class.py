import time
from micropython import const
from machine import Pin

BUTTON_A_PIN = const(10)
BUTTON_B_PIN = const(13)
Button_A_Status = "OFF"
Button_A_cnt = 0
Button_B_Status = "OFF"
Button_B_cnt = 0
Light_A = "OFF" # white
Light_B = "OFF" # red

print('Debounce Class loaded')

class Button:
    def __init__(self, pin, callback, trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, min_ago=10):
        self.callback = callback
        self.min_ago = min_ago
        self._blocked = True
        self._next_call = time.ticks_ms() + self.min_ago
        pin.irq(trigger=trigger, handler=self.debounce_handler)
    def call_callback(self, pin):
        self.callback(pin)
    def debounce_handler(self, pin):
        if time.ticks_ms() > self._next_call:
            self._next_call = time.ticks_ms() + self.min_ago
            self.call_callback(pin)

    def x_button_a_switch():
        global Light_A
        global Light_B
        if Light_A == "OFF" and Light_B == "OFF":
            Light_A = "ON"
            print("White ON")
        elif Light_A == "ON" and Light_B == "OFF":
            Light_A = "OFF"
            print("White OFF")

    def x_button_b_switch():
        global Light_A
        global Light_B
        if Light_B == "OFF" and Light_A == "OFF":
            Light_B = "ON"
            print("Red ON")
        elif Light_B == "OFF" and Light_A == "ON":
            Light_A = "OFF"
            Light_B = "ON"
            print("Red over White ON")
        else:
            Light_B = "OFF"
            print("Red OFF")

    def x_button_a_callback(pin):
        global Button_A_cnt
        global Button_A_Status
        if pin.value() == 1:
            if Button_A_cnt % 2 == 0:
                Button_A_cnt = 0
                if Button_A_Status == "ON":
                    Button_A_Status = "OFF"
                else:
                    Button_A_Status = "ON"
                print(f"Button A (%s) cnt:{Button_A_cnt} status:{Button_A_Status}" % pin)
                button_a_switch()
            else:
                pass
            Button_A_cnt +=1

    def x_button_b_callback(pin):
        global Button_B_cnt
        global Button_B_Status
        if pin.value() == 1:
            Button_B_cnt %= 2 
            if Button_B_cnt == 1:
    #            Button_B_cnt = 0
                if Button_B_Status == "ON":
                    Button_B_Status = "OFF"
                else:
                    Button_B_Status = "ON"
                print(f"Button B (%s) cnt:{Button_B_cnt} status:{Button_B_Status}" % pin)
                button_b_switch()
            else:
                pass
            Button_B_cnt +=1

#button_a = Button(pin=Pin(BUTTON_A_PIN, mode=Pin.IN, pull=Pin.PULL_UP), trigger=Pin.IRQ_RISING, callback=button_a_callback)
#button_b = Button(pin=Pin(BUTTON_B_PIN, mode=Pin.IN, pull=Pin.PULL_UP), trigger=Pin.IRQ_RISING, callback=button_b_callback)

print('Button init done')


