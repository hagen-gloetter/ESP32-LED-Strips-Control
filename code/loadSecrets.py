
import ujson

with open("secrets.json") as fp:
    secrets = ujson.load(fp)
print (secrets)
ssid= secrets['ssid']
password= secrets['password']
print (ssid)
print (password)