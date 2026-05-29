"""
Boot script executed on every ESP32 reset (including deep-sleep wake).

WebREPL is started later in main.py after WiFi STA connects,
to avoid RAM pressure during WiFi scan.
"""
# This file is executed on every boot (including wake-boot from deepsleep)
import esp
#esp.osdebug(None)
import gc
print("boot.py")

gc.collect()
print("boot.py done")
