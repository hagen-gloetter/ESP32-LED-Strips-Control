
from machine import Pin, Timer
import time

light_white = 0 #white
light_red = 0 #red
button_white_pressed=False
button_red_pressed=False
button_white_status=True
button_red_pressed=False
LED_brightness=255

led = Pin(2, Pin.OUT)

def on_pressed(timer):
    print('button_white_pressed')
    global button_white_pressed
    button_white_pressed=True
    

def on_pressed2(timer):
    print('button_red_pressed')
    global button_red_pressed
    button_red_pressed=True
    
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
    time.sleep(.5)
    statechange=0
    # Drehregler abfragen
    
    if light_red == 0 and button_red_pressed == True:
        light_red = LED_brightness
        light_white = 0
        statechange+=1
        print('MAIN light_red ON  light_white OFF')
    elif light_red > 0 and button_red_pressed == True:
        print('MAIN light_red OFF ')
        light_red = 0
        statechange+=1
    elif light_red > 0 and button_red_pressed == False:
        print('MAIN light_red ON LED_brightness ')
#        statechange+=1        

    elif light_white == 0 and button_white_pressed == True and light_red == 0:
        light_white = LED_brightness
        print('MAIN light_white ON ')
        statechange+=1
    elif light_white > 0 and button_white_pressed == True:
        print('MAIN light_white OFF ')
        light_white = 0
        statechange+=1
    elif light_white > 0 and button_white_pressed == False:
        print('MAIN light_white LED_brightness')
#        statechange+=1        
#    else:
        
    if statechange>0:
        print (f"light_white:{light_white} light_red:{light_red} button_white_pressed:{button_white_pressed} button_red_pressed:{button_red_pressed} LED_brightness:{LED_brightness}")

    button_red_pressed = False
    button_white_pressed = False
#    print (f"light_white:{} light_red:{} button_white_pressed:{} button_red_pressed:{}",,light_red,button_white_pressed,button_red_pressed )



#    elif light_red = 0 and light_white > 0
    
#    elif button_white_pressed == True:
#        print('MAIN button_white_pressed ')
#        button_white_pressed=False
        

while True:
    
    if light_red == 0:
        if light_white == 0:
            led.value(1)
            light_white = 1
            print('light on')
        elif light_white == 1:
            led.value(0)
            light_white = 0
            print('light off')
    
    light_red
    if light_white == 0:
        if light_red == 0:
            led.value(1)
            light_red = 1
            print('light on')
        elif light_red == 1:
            led.value(0)
            light_red = 0
            print('light off')
    elif light_white == 1:
        if light_red == 0:
            print('red over white')
            light_red == 1
#        elif light_red == 1:
#            led.value(0)
#            light_white = 0
#            light_red = 0

