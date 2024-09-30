# More details can be found in TechToTinker.blogspot.com
# George Bantique | tech.to.tinker@gmail.com

from machine import Pin
from time import sleep_ms
from rotary_irq_esp import RotaryIRQ

r = RotaryIRQ(
    pin_num_clk=33,
    pin_num_dt=34,
    min_val=1,
    max_val=255,
    reverse=True,
    range_mode=RotaryIRQ.RANGE_WRAP)
sw = Pin(14, Pin.IN)
val_old = r.value()
isRotaryEncoder = True
#print ("rotary_encoder loaded")

# Debouncing function for switch
def debounce(pin):
    sleep_ms(50)  # Debounce time
    return pin.value()

def get_rotary_encoder():
    global isRotaryEncoder
    global sw
    # Switch toggling logic with debounce
#    if debounce(sw) == 1:
#        isRotaryEncoder = not isRotaryEncoder
#        if isRotaryEncoder == True:
#            print('Rotary Encoder is now enabled.')
#        else:
#            print('Rotary Encoder is now disabled.')
#
#    if isRotaryEncoder == True:
    global val_old
    val_new = r.value()
    if val_old != val_new:
        val_old = val_new
        print('result = {}'.format(val_new))
        return val_new
