
import machine
from machine import Pin, PWM, Timer

print('LEDStrip Class loaded')

class LEDStrip:
    def __init__(self, R,G,B, GPIO1=27,GPIO2=25,GPIO3=32):
        frequency=7321 # Prime for no visible artefacts in eyes and cellphones
        self.R=R
        self.G=G
        self.B=B
        self.pin1=Pin(GPIO1, Pin.OUT)
        self.pin2=Pin(GPIO2, Pin.OUT)
        self.pin3=Pin(GPIO3, Pin.OUT)
        self.pwmR=PWM(self.pin1)
        self.pwmG=PWM(self.pin2)
        self.pwmB=PWM(self.pin3)
        self.pwmR.freq(frequency)
        self.pwmR.duty(0)
        self.pwmG.freq(frequency)
        self.pwmG.duty(0)
        self.pwmB.freq(frequency)
        self.pwmB.duty(0)
        
    def SetColor (self, R,G,B):
        # duty is from 0 to 1023 RGB is from 0-255 ->
        r=R
        g=G
        b=B
        if r>1023:
            r=1023 
        if g>1023:
            g=1023 
        if b>1023:
            b=1023 
        self.pwmR.duty(r)
        self.pwmG.duty(g)
        self.pwmB.duty(b)
        #print(f"Set R{R}G{G}B{B} r{r}g{g}b{b}") 
        
#ColorR=255
#ColorG=0
#ColorB=0
#Strip1=PWM(ColorR, ColorG, ColorB, 27,25,32)
#Strip1.Set