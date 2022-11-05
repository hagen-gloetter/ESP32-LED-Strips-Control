# This file is executed on every boot (including wake-boot from deepsleep)
import esp
#esp.osdebug(None)
from machine import Pin
#esp.osdebug(None)
import gc
import time
#import webrepl
print ("boot.py") 

#webrepl.start()
#print ("boot.py done") 

import os
import machine

print ("boot.py get_wifi_connection") 
import get_wifi_connection
wifi=None
get_wifi_connection.connect_wifi()
print ("boot.py done") 
