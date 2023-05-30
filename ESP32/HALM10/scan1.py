import network
import time

authmodes = ['Open', 'WEP', 'WPA-PSK', 'WPA2-PSK', 'WPA/WPA2-PSK']
scan_interval = 5  # Angiv intervallet i sekunder mellem hver scanning

while True:
    print("Scanning for WiFi networks, please wait...")
    print("")

    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)

    for result in sta_if.scan():
        try:
            ssid = result[0].decode("utf-8")
            bssid = ':'.join('%02x' % b for b in result[1])
            channel = result[2]
            RSSI = result[3]
            authmode = authmodes[result[4]]
            hidden = result[5]

            print("* {:s}".format(ssid))
            print("   - Auth: {} {}".format(authmode, '(hidden)' if hidden else ''))
            print("   - Channel: {}".format(channel))
            print("   - RSSI: {}".format(RSSI))
            print("   - BSSID: {:s}".format(bssid))
            print()

        except IndexError:
            print("Error: Invalid scan result")

    print("Scanning completed.")
    print("Waiting for next scan...")
    print("")
    time.sleep(scan_interval)