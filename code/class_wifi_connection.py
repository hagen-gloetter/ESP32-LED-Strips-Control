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
    """
    Multi-SSID WiFi connection manager for ESP32.

    Reads credentials from ``secrets_wifi.json`` (a JSON object mapping
    SSID → password). Scans for known networks and connects to the first
    match. Provides reconnect logic for use in the main loop.

    Usage::

        import class_wifi_connection
        wifi = class_wifi_connection.WifiConnect()
        wifi_status, wifi_ssid, wifi_ip = wifi.connect()
        # Later in main loop:
        wifi.check_connection()

    Notes:
        ``secrets_wifi.json`` must exist on the device filesystem before
        ``connect()`` is called.
    """

    def __init__(self):
        """
        Initialise cached WiFi state and the default DHCP hostname.

        Returns:
            None
        """
        self.wifi_ssid = "offline"
        self.wifi_pw = "hidden"
        self.wifi_ip = "offline"
        self.wifi_status = "offline"
        self.wifi = None
        self.hostname = "ESP32-Huettenlicht"

    def set_hostname(self, name):
        """
        Set the DHCP hostname used on the next WiFi connect/reconnect.

        Args:
            name (str): Hostname announced to the DHCP server.

        Returns:
            None
        """
        self.hostname = name

    def connect(self):
        """
        Load credentials from ``secrets_wifi.json`` and connect.

        Scans for available networks and tries each SSID listed in the
        credentials file until a connection is established.

        The scan is performed once up front so reconnect attempts can reuse
        the last known SSID/password pair without rescanning every time.

        Returns:
            list: ``[status (str), ssid (str), ip (str)]``.
                  *status* is ``"online"`` on success, ``"offline"`` on failure.
        """
        debug(4, __name__, "connect wifi called")
        fn_secrets = "secrets_wifi.json"
        debug(4, __name__, "WiFi debug: opening secrets file")
        try:
            with open(fn_secrets) as f:
                wlan_json = ujson.load(f)
        except Exception as e:
            debug(4, __name__, f"!!!!!!!!!!!!!!!! ERROR !!!!!!!!!!!!!!!! File not found {fn_secrets}: {e}")
            return ("offline", "offline", "offline")
        else:
            debug(4, __name__, f"connect wifi called with {fn_secrets}")
            try:
                import gc
                debug(4, __name__, "WiFi debug: free RAM before WLAN object: " + str(gc.mem_free()))
            except Exception:
                pass
            debug(4, __name__, "WiFi step: create STA interface")
            self.wifi = network.WLAN(network.STA_IF)
            debug(4, __name__, "WiFi debug: STA interface object created")
            debug(4, __name__, "WiFi step: enable STA interface")
            self.wifi.active(True)
            debug(4, __name__, "WiFi step: STA interface enabled")
            try:
                debug(4, __name__, "WiFi debug: status after active(True): " + str(self.wifi.status()))
            except Exception as e:
                debug(4, __name__, "WiFi debug: status() failed: " + str(e))
            utime.sleep_ms(100)
            for ssid in wlan_json.keys():
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
        """
        Attempt a connection to a specific SSID with a 10-second timeout.

        Args:
            ssid (str): Network SSID. Defaults to stored ``wifi_ssid``.
            pwd (str): Network password. Defaults to stored ``wifi_pw``.

        Returns:
            list: ``[status, ssid, ip]`` — same format as :meth:`connect`.
        """
        if ssid is None:
            ssid = self.wifi_ssid
            pwd = self.wifi_pw
        try:
            debug(4, __name__, "WiFi debug: entering connect() for SSID: " + str(ssid))
            self.wifi.connect(ssid, pwd)
            debug(4, __name__, "WiFi debug: connect() returned for SSID: " + str(ssid))
            timeout = 10000
            start_time = utime.ticks_ms()
            debug(4, __name__, "WiFi debug: waiting for isconnected()")
            while not self.wifi.isconnected():
                if utime.ticks_diff(utime.ticks_ms(), start_time) > timeout:
                    debug(4, __name__, "Connection timeout reached")
                    break
                machine.idle()  # Yield while waiting instead of busy-spinning.

            if self.wifi.isconnected():
                debug(4, __name__, "WiFi debug: isconnected() became True")
                self.wifi_status = "online"
                self.wifi_ssid = ssid
                self.wifi_pw = pwd
                self.wifi_ip = self.wifi.ifconfig()[0]
                debug(4, __name__, "Connected to " + self.wifi_ssid)
                debug(4, __name__, " with IP address: " + self.wifi_ip)
            else:
                try:
                    debug(4, __name__, "WiFi debug: final status before failure: " + str(self.wifi.status()))
                except Exception as status_error:
                    debug(4, __name__, "WiFi debug: final status() failed: " + str(status_error))
                raise Exception("Connection failed")

        except Exception as e:
            debug(4, __name__, f"Failed to connect to any known network: {e}")
            self.wifi_status = "offline"
            self.wifi_ssid = "offline"
            self.wifi_ip = "offline"
            self.wifi.disconnect()
        return [self.wifi_status, self.wifi_ssid, self.wifi_ip]

    def get_wifi_status(self):
        """
        Return the cached connection state without triggering reconnects.

        Returns:
            list: ``[status, ssid, ip]`` from the cached state.
        """
        list = [self.wifi_status, self.wifi_ssid, self.wifi_ip]
        return list

    def isconnected(self):
        """
        Proxy to ``network.WLAN.isconnected()`` for existing callers.

        Returns:
            bool: ``True`` when the WLAN interface is connected.
        """
        return self.wifi.isconnected()

    def check_connection(self):
        """
        Verify WiFi is still connected; reconnect automatically if not.

        Returns:
            list: ``[status, ssid, ip]``.
        """
        debug(4, __name__, "check_connection called")
        if self.wifi_ssid == "offline":
            debug(4, __name__, "Attempting to connect to SSID: " + self.wifi_ssid)
            self.connect()
        elif not self.wifi.isconnected() or self.wifi_status == "offline":
            # Reuse the last successful credentials before falling back to a
            # full rescan on the next explicit ``connect()``.
            self.wifi_status = "offline"
            debug(4, __name__, "Connection lost, trying to reconnect to SSID: " + self.wifi_ssid)
            (self.wifi_status, self.wifi_ssid, self.wifi_ip) = self.try_wifi_connect(
                self.wifi_ssid, self.wifi_pw
            )
        return [self.wifi_status, self.wifi_ssid, self.wifi_ip]

    def is_connected(self):
        """
        Compatibility wrapper returning the same tuple as ``check_connection()``.

        Returns:
            list: ``[status, ssid, ip]`` after the connection check.
        """
        debug(4, __name__, "is_connected called")
        (wifi_status, wifi_ssid, wifi_ip) = self.check_connection()
        list = [self.wifi_status, self.wifi_ssid, self.wifi_ip]
        return list

    def disconnect(self):
        """
        Disconnect and reset the cached connection metadata.

        Returns:
            None
        """
        debug(4, __name__, "disconnect called")
        self.wifi.disconnect()
        self.wifi_status = "offline"
        self.wifi_ssid = "offline"
        self.wifi_ip = "offline"

    def stop_all(self):
        """
        Stop WiFi activity; kept for symmetry with other subsystem classes.

        Returns:
            None
        """
        debug(4, __name__, "stop_all called")
        self.disconnect()

def main():
    """
    Run the standalone WiFi connection test loop.

    Returns:
        None
    """
    wifi = WifiConnect()
    (wifi_status, wifi_ssid, wifi_ip) = wifi.connect()
    i = 0
    while i == 0:
        list = wifi.check_connection()
        for item in list:
            debug(4, __name__, item)
        sleep_ms(10000)
    wifi.disconnect()


if __name__ == "__main__":
    sys.exit(main())


