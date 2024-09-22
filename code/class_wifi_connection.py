import ujson
import network
from network import WLAN
import machine
from machine import Timer
from time import sleep_ms

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
        print(item)
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
        print("connect wifi called")
        fn_secrets = "secrets_wifi.json"
        try:
            wlan_json = ujson.load(open(fn_secrets))
        except:
            print(f"!!!!!!!!!!!!!!!! ERROR !!!!!!!!!!!!!!!! File not found {fn_secrets}")
            return ("offline", "offline", "offline")
        else:
            print(f"connect wifi called with {fn_secrets}")
            self.wifi = network.WLAN(network.STA_IF)
            self.wifi.active(True)
            self.wifi.disconnect()  # ensure we're disconnected
            nets = self.wifi.scan()

            for ssid in wlan_json.keys():
                if ssid in str(nets):
                    print(f"++++++++ Network {ssid} found!")
                    pwd = wlan_json[ssid]
                    print("Trying to connect to SSID:", ssid)
                    (
                        self.wifi_status,
                        self.wifi_ssid,
                        self.wifi_ip,
                    ) = self.try_wifi_connect(ssid, pwd)
                    if self.wifi_status == "online":
                        break
            return [self.wifi_status, self.wifi_ssid, self.wifi_ip]

    def try_wifi_connect(self, ssid=None, pwd=None):
        if ssid is None:
            ssid = self.wifi_ssid
            pwd = self.wifi_pw
        try:
            self.wifi.connect(ssid, pwd)
            timeout = 10000  # 10 seconds timeout
            start_time = machine.time() * 1000
            while not self.wifi.isconnected():
                if machine.time() * 1000 - start_time > timeout:
                    print("Connection timeout reached")
                    break
                machine.idle()  # save power while waiting

            if self.wifi.isconnected():
                self.wifi_status = "online"
                self.wifi_ssid = ssid
                self.wifi_pw = pwd
                self.wifi_ip = self.wifi.ifconfig()[0]
                print("Connected to " + self.wifi_ssid)
                print(" with IP address: " + self.wifi_ip)
            else:
                raise Exception("Connection failed")

        except Exception as e:
            print(f"Failed to connect: {e}")
            self.wifi_status = "offline"
            self.wifi_ssid = "offline"
            self.wifi_ip = "offline"
            self.wifi.disconnect()  # ensure clean disconnect
        return [self.wifi_status, self.wifi_ssid, self.wifi_ip]

    def check_connection(self):
        print("check_connection called")
        if self.wifi_ssid == "offline":
            print("Attempting to connect to SSID:", self.wifi_ssid)
            self.connect()  # not connected at all
        elif not self.wifi.isconnected() or self.wifi_status == "offline":
            print("Connection lost, trying to reconnect to SSID:", self.wifi_ssid)
            (self.wifi_status, self.wifi_ssid, self.wifi_ip) = self.try_wifi_connect(
                self.wifi_ssid, self.wifi_pw
            )
        return [self.wifi_status, self.wifi_ssid, self.wifi_ip]

    def is_connected(self):
        print("is_connected called")
        return [self.wifi_status, self.wifi_ssid, self.wifi_ip]

    def disconnect(self):
        print("disconnect called")
        self.wifi.disconnect()
        self.wifi_status = "offline"
        self.wifi_ssid = "offline"
        self.wifi_ip = "offline"

    def stop_all(self):
        print("stop_all called")
        self.disconnect()

#def main():
#    wifi = WifiConnect()  # Init the class
#    (wifi_status, wifi_ssid, wifi_ip) = wifi.connect()  # connect to wifi
#    i = 0
#    while i == 0:
#        list = wifi.check_connection()
#        for item in list:
#            print(item)
#        sleep_ms(3000)

#    wifi.disconnect()
#
#
#if __name__ == "__main__":
#    sys.exit(main())
