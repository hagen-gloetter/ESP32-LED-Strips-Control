"""
RGB LED-Strip PWM driver for ESP32.

Provides the ``LEDStrip`` class which controls a single common-cathode
RGB LED strip via three PWM channels.

Usage::

    from class_pwm import LEDStrip
    strip = LEDStrip(0, 0, 0, pin_r=27, pin_g=25, pin_b=32)
    strip.SetColor(512, 0, 0)   # half-brightness red

Hardware:
    - Three GPIO pins configured as PWM output (duty 0–1023)
    - Recommended PWM frequency: 7321 Hz (prime, avoids camera/eye artefacts)
"""
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
    """
    Single RGB LED strip controlled via three PWM channels.

    Args:
        R (int): Initial red duty cycle (0–1023).
        G (int): Initial green duty cycle (0–1023).
        B (int): Initial blue duty cycle (0–1023).
        GPIO1 (int): Pin number for the red channel.
        GPIO2 (int): Pin number for the green channel.
        GPIO3 (int): Pin number for the blue channel.
    """
    def __init__(self, R=0, G=0, B=0, GPIO1=27, GPIO2=25, GPIO3=32):
        """
        Create one PWM-driven RGB strip instance.

        Args:
            R (int): Initial red duty cycle.
            G (int): Initial green duty cycle.
            B (int): Initial blue duty cycle.
            GPIO1 (int): Red-channel GPIO.
            GPIO2 (int): Green-channel GPIO.
            GPIO3 (int): Blue-channel GPIO.

        Returns:
            None
        """
        frequency = 7321  # Prime for no visible artefacts in eyes and cellphones
        self.R = R
        self.G = G
        self.B = B
        # Initialize pins and PWM channels
        self.pwmR = PWM(Pin(GPIO1, Pin.OUT), freq=frequency, duty=0)
        self.pwmG = PWM(Pin(GPIO2, Pin.OUT), freq=frequency, duty=0)
        self.pwmB = PWM(Pin(GPIO3, Pin.OUT), freq=frequency, duty=0)        

    def SetColor(self, R, G, B):
        """
        Set the RGB colour of the strip.

        Values are clamped to [0, 1023] before being written to the
        PWM duty registers.

        Args:
            R (int): Red duty cycle (0–1023).
            G (int): Green duty cycle (0–1023).
            B (int): Blue duty cycle (0–1023).
        """
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
    """
    Run a simple RGB fade demo across all configured strips.

    Returns:
        None
    """
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

