# Written 10.2022 by Hagen@gloetter.de

import dht
from machine import Pin
import sys
import time


class HumiditySensor:
    """Class to connect your ESP32 to a dht-Sensor"""

    def __init__(self, pin=33):
        self.temperature = 0
        self.humidity = 0
        self.oldtemperature = 0
        self.oldhumidity = 0

        self.pin = pin
        self.sensor = dht.DHT11(Pin(self.pin))

        # if this is called TOO FAST the DHT returns a
        # OSError: [Errno 116] ETIMEDOUT
        # and stops program execution. to avoid this i use try except
        # on error return the old values

    def get_humidity_and_temperature(self):
        # has to be done at the same time otherwise you get an error
        #self.oldtemperature = self.temperature
        #self.oldhumidity = self.humidity
        try:
            self.sensor.measure()
            self.temperature = self.sensor.temperature()
            self.humidity = self.sensor.humidity()
        except:
            # when fail return old value
            self.temperature = self.oldtemperature
            self.humidity = self.oldhumidity
        list = [self.temperature, self.humidity]
        return list

    def get_temperature(self):
        (self.temperature, self.humidity) = self.get_humidity_and_temperature()
        return self.temperature

    def get_humidity(self):
        (self.temperature, self.humidity) = self.get_humidity_and_temperature()
        return self.humidity

    def set_oldtemperature(self, old):
        self.oldtemperature = old

    def set_oldhumidity(self, old):
        self.oldhumidity = old

    def get_oldtemperature(self):
        return self.oldtemperature

    def get_oldhumidity(self):
        return self.oldhumidity


def main():
    sensor = HumiditySensor()
    while True:
        (temperature, humidity) = sensor.get_humidity_and_temperature()
        print(f"temperature={temperature}, humidity={humidity}")
        time.sleep(2)


if __name__ == "__main__":
    sys.exit(main())

