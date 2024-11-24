import machine
from machine import Pin, PWM, Timer
import time
import sys
from class_debug import debug

global PIN_STRIP_1R 
global PIN_STRIP_1G 
global PIN_STRIP_1B 
global PIN_STRIP_2R 
global PIN_STRIP_2G 
global PIN_STRIP_2B 
global PIN_STRIP_3R 
global PIN_STRIP_3G 
global PIN_STRIP_3B 
global PIN_BUTTON_W 
global PIN_BUTTON_R 
# Rotary
global PIN_BUTTON_D  # Switch
global PIN_CLK 
global PIN_DT 
# DHT GPIO0
print ("LEDStrip Class loaded")

class LEDStrip:
    def __init__(self, R=0, G=0, B=0, GPIO1=27, GPIO2=25, GPIO3=32):
        frequency = 7321  # Prime for no visible artefacts in eyes and cellphones
        self.R = R
        self.G = G
        self.B = B
        # Initialize pins and PWM channels
        self.pwmR = PWM(Pin(GPIO1, Pin.OUT), freq=frequency, duty=0)
        self.pwmG = PWM(Pin(GPIO2, Pin.OUT), freq=frequency, duty=0)
        self.pwmB = PWM(Pin(GPIO3, Pin.OUT), freq=frequency, duty=0)        

    def SetColor(self, R, G, B):
        # duty is from 0 to 1023
        # Clamp values to be between 0 and 1023
        R = min(max(R, 0), 1023)
        G = min(max(G, 0), 1023)
        B = min(max(B, 0), 1023)

        # Set PWM duty cycles
        self.pwmR.duty(R)
        self.pwmG.duty(G)
        self.pwmB.duty(B)
        # debug(4, __name__, f"Set R{R}G{G}B{B} r{r}g{g}b{b}")


def main():
    ColorR = 0
    ColorG = 0
    ColorB = 0
    Strip1 = LEDStrip(ColorR, ColorG, ColorB, PIN_STRIP_1R, PIN_STRIP_1G, PIN_STRIP_1B)
    Strip2 = LEDStrip(ColorR, ColorG, ColorB, PIN_STRIP_2R, PIN_STRIP_2G, PIN_STRIP_2B)
    Strip3 = LEDStrip(ColorR, ColorG, ColorB, PIN_STRIP_3R, PIN_STRIP_3G, PIN_STRIP_3B)

    while ColorR < 1024:
        Strip1.SetColor(ColorR, ColorG, ColorB)
        Strip2.SetColor(ColorR, ColorG, ColorB)
        Strip3.SetColor(ColorR, ColorG, ColorB)
        debug(4, __name__, f"R:{ColorR} G:{ColorG} B:{ColorB} ")
        ColorR += 10
        ColorG += 10
        ColorB += 10
        time.sleep_ms(200)


if __name__ == "__main__":
    sys.exit(main())

