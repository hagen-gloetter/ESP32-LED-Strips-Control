"""
DHT11 temperature and humidity sensor driver for ESP32.

Wraps the MicroPython ``dht`` module and caches the last successful
reading so stale values are returned on I2C/timing errors.

Usage::

    from class_humidity_sensor import HumiditySensor
    sensor = HumiditySensor(pin=0)
    temp, hum = sensor.get_humidity_and_temperature()

Hardware:
    - DHT11 sensor data pin connected to the configured GPIO
    - Minimum measurement interval: ~2 s (hardware limitation of DHT11)
"""
# Written 10.2022 by Hagen@gloetter.de

import dht
from machine import Pin
import sys
import time
from class_debug import debug


class HumiditySensor:
    """Class to connect your ESP32 to a dht-Sensor"""

    def __init__(self, pin=0):
        """
        Initialise the DHT11 sensor wrapper.

        Args:
            pin (int): GPIO number connected to the DHT11 data pin.

        Returns:
            None
        """
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
        """
        Measure and return temperature and humidity.

        On sensor error the previous valid values are returned so the
        caller always receives a usable result.

        Returns:
            list: ``[temperature (°C, int), humidity (%, int)]``.
        """
        # has to be done at the same time otherwise you get an error
        #self.oldtemperature = self.temperature
        #self.oldhumidity = self.humidity
        try:
            self.sensor.measure()
            self.temperature = self.sensor.temperature()
            self.humidity = self.sensor.humidity()
        except Exception as e:
            debug(2, __name__, f"DHT11 sensor error: {e}, using old values")
            # when fail return old value
            self.temperature = self.oldtemperature
            self.humidity = self.oldhumidity
        list = [self.temperature, self.humidity]
        return list

    def get_temperature(self):
        """
        Return the current temperature in degrees Celsius.

        Returns:
            int: Temperature value from the last successful DHT11 reading.
        """
        (self.temperature, self.humidity) = self.get_humidity_and_temperature()
        return self.temperature

    def get_humidity(self):
        """
        Return the current relative humidity in percent.

        Returns:
            int: Humidity value from the last successful DHT11 reading.
        """
        (self.temperature, self.humidity) = self.get_humidity_and_temperature()
        return self.humidity

    def set_oldtemperature(self, old):
        """
        Store the fallback temperature value used after read errors.

        Args:
            old (int): Previous valid temperature.

        Returns:
            None
        """
        self.oldtemperature = old

    def set_oldhumidity(self, old):
        """
        Store the fallback humidity value used after read errors.

        Args:
            old (int): Previous valid humidity.

        Returns:
            None
        """
        self.oldhumidity = old

    def get_oldtemperature(self):
        """
        Return the cached fallback temperature value.

        Returns:
            int: Last stored fallback temperature.
        """
        return self.oldtemperature

    def get_oldhumidity(self):
        """
        Return the cached fallback humidity value.

        Returns:
            int: Last stored fallback humidity.
        """
        return self.oldhumidity


def main():
    """
    Run a standalone DHT11 read loop for manual testing.

    Returns:
        None
    """
    sensor = HumiditySensor()
    while True:
        (temperature, humidity) = sensor.get_humidity_and_temperature()
        print ( f"temperature={temperature}, humidity={humidity}")
        time.sleep(2)


if __name__ == "__main__":
    sys.exit(main())


