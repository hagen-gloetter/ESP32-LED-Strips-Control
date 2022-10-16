
def connect_wifi():
    import ujson
    import network
    from network import WLAN
    import machine
    global wifi
    print("connect_wifi called")
    
    wlan_json=ujson.load(open("secrets.json"))
    #print (wlan_json)
    #print (type (wlan_json))
    #for key in wlan_json.keys():
    #    print (key)
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    nets = wifi.scan()
    #print ("NETS: ",nets)
    #print (type (nets))
    for ssid in wlan_json.keys():
        if ssid in str(nets):
            print(f"++++++++ Network {ssid} found!")
            pwd = wlan_json[ssid]
            print ("tying to connect ssid:",ssid)
            try:
                wifi.connect(ssid, pwd)
                while not wifi.isconnected():
                    machine.idle()
                    #machine.idle() # save power while waiting
                print("Connected to "+ ssid +" with IP address:" + wifi.ifconfig()[0])
                break
            except Exception as e:
                print("Failed to connect to any known network")

def disconnect_wifi():
    print("disconnect wifi network")
    global wifi
    wifi.disconnect()

#connect_wifi()
#disconnect_wifi()