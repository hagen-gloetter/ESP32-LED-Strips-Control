# This file is executed on every boot (including wake-boot from deepsleep)
import esp
#esp.osdebug(None)
import ujson
from machine import Pin
import network
import esp
#esp.osdebug(None)
import gc
import time
import network
try:
    import usocket as socket
except:
    import socket
import webrepl
print ("boot.py") 

ssid = ""
password = ""

def get_wlankeys():
# load WLAN Secrets
    with open("secretsSW.json") as fp:
        secrets = ujson.load(fp)
    global ssid
    global password
    ssid = secrets['ssid']
    password = secrets['password']
#    print (ssid)
#    print (password)


def do_connect(ssid, pwd):
    import network
    station = network.WLAN(network.STA_IF)
    if not station.isconnected():
        print('connecting to network...')
        station.active(True)
        station.connect(ssid, pwd)
        while not station.isconnected():
            sleep_ms(10)
            pass
    print('network config:', station.ifconfig())

#webrepl.start()
#get_wlankeys()
#print (ssid)
#print ("pw")
#do_connect(ssid, password)
