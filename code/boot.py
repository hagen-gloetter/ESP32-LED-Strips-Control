# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()

import ujson

ssid = ""
password = ""

def get_wlankeys():
# load WLAN Secrets
    with open("secrets.json") as fp:
        secrets = ujson.load(fp)
    global ssid
    global password
    ssid = secrets['ssid']
    password = secrets['password']
#    print (ssid)
#    print (password)


def do_connect(ssid, pwd):
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(ssid, pwd)
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())
 
# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
 
# Attempt to connect to WiFi network

get_wlankeys()
print (ssid)
print (password)

do_connect(ssid, password)
 
import webrepl
webrepl.start()

try:
  import usocket as socket
except:
  import socket

from machine import Pin
import network

import esp
esp.osdebug(None)

import gc
gc.collect()

import time
last_on = 0

station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
  pass

print('Connection successful')
print(station.ifconfig())

lights_on = 0

led = Pin(2, Pin.OUT)

