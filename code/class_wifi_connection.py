import ujson
import network
from network import WLAN
import machine
from machine import Timer
import sys
from time import sleep_ms
import utime  # Verwende utime f�r Zeitmessung in MicroPython
from class_debug import debug

class WifiConnect:
    """Class to connect your ESP32 to local Wifi
    SSID and WiFi PW are read from file: secrets_wifi.json
    Usage:
    # Setup Wifi
    import class_wifi_connection
    global wifi
    wifi = class_wifi_connection.WifiConnect()
    (wifi_status, wifi_ssid, wifi_ip) = wifi.connect()
    # in a loop or timer
    list = wifi.check_connection()
    for item in list:
        debug(4, __name__, item)
    # stop
        wifi.disconnect()
    """

    def __init__(self):
        self.wifi_ssid = "offline"
        self.wifi_pw = "hidden"
        self.wifi_ip = "offline"
        self.wifi_status = "offline"
        self.wifi = None

    def connect(self):
        debug(4, __name__, "connect wifi called")
        fn_secrets = "secrets_wifi.json"
        try:
            wlan_json = ujson.load(open(fn_secrets))
        except:
            debug(4, __name__, f"!!!!!!!!!!!!!!!! ERROR !!!!!!!!!!!!!!!! File not found {fn_secrets}")
            return ("offline", "offline", "offline")
        else:
            debug(4, __name__, f"connect wifi called with {fn_secrets}")
            # debug(4, __name__, wlan_json)
            # debug(4, __name__, type (wlan_json))
            # for key in wlan_json.keys():
            #    debug(4, __name__, key)
            self.wifi = network.WLAN(network.STA_IF)
            self.wifi.active(True)
            self.wifi.disconnect()  # ensure we're disconnected
            nets = self.wifi.scan()
            # debug(4, __name__, "NETS: ",nets)
            # debug(4, __name__, type (nets))
            for ssid in wlan_json.keys():
                if ssid in str(nets):
                    debug(4, __name__, f"++++++++ Network {ssid} found!")
                    pwd = wlan_json[ssid]
                    debug(4, __name__, "Trying to connect to SSID:" + ssid)
                    (
                        self.wifi_status,
                        self.wifi_ssid,
                        self.wifi_ip,
                    ) = self.try_wifi_connect(ssid, pwd)
                    if self.wifi_status == "online":
                        break
            list = [self.wifi_status, self.wifi_ssid, self.wifi_ip]
            return list
            
            

    def try_wifi_connect(self, ssid=None, pwd=None):
        if ssid is None:
            ssid = self.wifi_ssid
            pwd = self.wifi_pw
        try:
            self.wifi.connect(ssid, pwd)
            timeout = 10000  # 10 Sekunden Timeout
            start_time = utime.ticks_ms()  # Millisekunden-Z�hler
            while not self.wifi.isconnected():
                if utime.ticks_diff(utime.ticks_ms(), start_time) > timeout:
                    debug(4, __name__, "Connection timeout reached")
                    break
                machine.idle()  # save power while waiting

            if self.wifi.isconnected():
                self.wifi_status = "online"
                self.wifi_ssid = ssid
                self.wifi_pw = pwd
                self.wifi_ip = self.wifi.ifconfig()[0]
                debug(4, __name__, "Connected to " + self.wifi_ssid)
                debug(4, __name__, " with IP address: " + self.wifi_ip)
            else:
                raise Exception("Connection failed")

        except Exception as e:
            debug(4, __name__, f"Failed to connect to any known network: {e}")
            self.wifi_status = "offline"
            self.wifi_ssid = "offline"
            self.wifi_ip = "offline"
            self.wifi.disconnect()  # ensure clean disconnect
        return [self.wifi_status, self.wifi_ssid, self.wifi_ip]

    def get_wifi_status(self):
        list = [self.wifi_status, self.wifi_ssid, self.wifi_ip]
        return list

    def isconnected(self):
        return self.wifi.isconnected()

    def check_connection(self):
        debug(4, __name__, "check_connection called")
        if self.wifi_ssid == "offline":
            debug(4, __name__, "Attempting to connect to SSID: " + self.wifi_ssid)
            self.connect()  # not connected at all
        elif not self.wifi.isconnected() or self.wifi_status == "offline":
            # no more  more connected
            self.wifi_status = "offline"
            debug(4, __name__, "Connection lost, trying to reconnect to SSID: " + self.wifi_ssid)
            (self.wifi_status, self.wifi_ssid, self.wifi_ip) = self.try_wifi_connect(
                self.wifi_ssid, self.wifi_pw
            )
        return [self.wifi_status, self.wifi_ssid, self.wifi_ip]

    def is_connected(self):
        debug(4, __name__, "is_connected called")
        (wifi_status, wifi_ssid, wifi_ip) = self.wifi.check_connection()
        list = [self.wifi_status, self.wifi_ssid, self.wifi_ip]
        return list

    def disconnect(self):
        debug(4, __name__, "disconnect called")
        self.wifi.disconnect()
        self.wifi_status = "offline"
        self.wifi_ssid = "offline"
        self.wifi_ip = "offline"

    def stop_all(self):
        debug(4, __name__, "stop_all called")
        self.disconnect()
        #self.wifi.disconnect()

def main():
    wifi = WifiConnect()  # Init the class
    (wifi_status, wifi_ssid, wifi_ip) = wifi.connect()  # connect to wifi
    i = 0
    while i == 0:
        list = wifi.check_connection()
        for item in list:
            debug(4, __name__, item)
        sleep_ms(3000)
    wifi.disconnect()


if __name__ == "__main__":
    sys.exit(main())

