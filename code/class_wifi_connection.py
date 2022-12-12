import ujson
import network
from network import WLAN
import machine
from machine import Timer
import sys
from time import sleep_ms

class WifiConnect ():
    """ Class to connect your ESP32 to local Wifi
        SSID and WiFi PW are read from file: secrets_wifi.json

    """

    def __init__(self):
        self.wifi_ssid = "offline"
        self.wifi_pw = "hidden"
        self.wifi_ip = "offline"
        self.wifi_status = "offline"
        self.wifi = None

    def connect(self):
        print("connect wifi called")
        fn_secrets="secrets_wifi.json"
        try:
            wlan_json = ujson.load(open(fn_secrets))
        except:
            print (f"!!!!!!!!!!!!!!!! ERROR !!!!!!!!!!!!!!!! File not found {fn_secrets}")
            return ("offline", "offline", "offline")
        else:
            print(f"connect wifi called with {fn_secrets}")
            #print (wlan_json)
            #print (type (wlan_json))
            # for key in wlan_json.keys():
            #    print (key)
            self.wifi = network.WLAN(network.STA_IF)
            self.wifi.active(True)
            self.wifi.disconnect() # be sure to be disconnected
            nets = self.wifi.scan()
            #print ("NETS: ",nets)
            #print (type (nets))
            for ssid in wlan_json.keys():
                if ssid in str(nets):
                    print(f"++++++++ Network {ssid} found!")
                    pwd = wlan_json[ssid]
                    print("tying to connect ssid:", ssid)
                    (self.wifi_status, self.wifi_ssid, self.wifi_ip) = self.try_wifi_connect(ssid, pwd)
                    if self.wifi_status == "online":
                        break
            list = [self.wifi_status, self.wifi_ssid, self.wifi_ip]
            return (list)

    def try_wifi_connect(self, ssid=None, pwd=None):
        if ssid == None:
            ssid=self.wifi_ssid
            pwd=self.wifi_pw
        try:
            self.wifi.connect(ssid, pwd)
            while not self.wifi.isconnected():
                machine.idle()  # save power while waiting
            self.wifi_status = "online"
            self.wifi_ssid = ssid
            self.wifi_pw = pwd
            self.wifi_ip = self.wifi.ifconfig()[0]
            print("Connected to " + self.wifi_ssid )
            print(" with IP address:" + self.wifi_ip)
        except Exception as e:
            print("Failed to connect to any known network")
            self.wifi_status = "offline"
            self.wifi_ssid = "offline"
            self.wifi_ip = "offline"
            self.wifi.disconnect() # do a clean disconnected
        list = [self.wifi_status, self.wifi_ssid, self.wifi_ip]
        return (list)


        
    def check_connection(self):
        print("check_connection called")
        if self.wifi_ssid == "offline":
            print("tying to connect ssid:", self.wifi_ssid)
            self.connect()  # we are not connected at all
        elif not self.wifi.isconnected() or self.wifi_status == "offline":
            # no more  more connected
            self.wifi_status = "offline"
            print("tying to connect ssid:", self.wifi_ssid)
            (self.wifi_status, self.wifi_ssid, self.wifi_ip) = self.try_wifi_connect(
                self.wifi_ssid, self.wifi_pw)
        list = [self.wifi_status, self.wifi_ssid, self.wifi_ip]
        return (list)

    def is_connected(self):
        print("is_connected called")
        (wifi_status, wifi_ssid, wifi_ip) = self.wifi.check_connection()
        list = [self.wifi_status, self.wifi_ssid, self.wifi_ip]
        return (list)

    def disconnect(self):
        print("disconnect called")
        self.wifi.disconnect()

    def stop_all(self):
        print("disconnect called")
        self.wifi.disconnect()



def main():
    wifi = WifiConnect() # Init the class
    (wifi_status, wifi_ssid, wifi_ip) = wifi.connect()  # connect to wifi
    i=0
    while i==0:
        list = wifi.check_connection()
        for item in list:
            print (item)
        sleep_ms(3000)
        
    wifi.disconnect()

if __name__ == '__main__':
    sys.exit(main())



