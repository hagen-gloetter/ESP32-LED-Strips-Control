import machine
from machine import Pin, PWM, Timer
import time
import sys

print("LEDStrip Class loaded")


class LEDStrip:
    def __init__(self, R=0, G=0, B=0, GPIO1=27, GPIO2=25, GPIO3=32):
        frequency = 7321  # Prime for no visible artefacts in eyes and cellphones
        self.R = R
        self.G = G
        self.B = B
#        self.pin1 = Pin(GPIO1, Pin.OUT)
#        self.pin2 = Pin(GPIO2, Pin.OUT)
#        self.pin3 = Pin(GPIO3, Pin.OUT)
#        self.pwmR = PWM(self.pin1)
#        self.pwmG = PWM(self.pin2)
#        self.pwmB = PWM(self.pin3)
#        self.pwmR.freq(frequency)
#        self.pwmR.duty(0)
#        self.pwmG.freq(frequency)
#        self.pwmG.duty(0)
#        self.pwmB.freq(frequency)
#        self.pwmB.duty(0)
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
        # print(f"Set R{R}G{G}B{B} r{r}g{g}b{b}")


def main():
    ColorR = 0
    ColorG = 0
    ColorB = 0
    Strip1 = LEDStrip(ColorR, ColorG, ColorB, 27, 25, 32)
    while ColorR < 1024:
        Strip1.SetColor(ColorR, ColorG, ColorB)
        print(f"R:{ColorR} G:{ColorG} B:{ColorB} ")
        ColorR += 10
        ColorG += 10
        ColorB += 10
        time.sleep_ms(200)


if __name__ == "__main__":
    sys.exit(main())
