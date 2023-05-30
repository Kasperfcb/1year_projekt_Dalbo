import network
import time

authmodes = ['Open', 'WEP', 'WPA-PSK', 'WPA2-PSK', 'WPA/WPA2-PSK']
scan_interval = 20  # Angiv intervallet i sekunder mellem hver scanning

def connect_to_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        print('Connecting to WiFi...')
        wlan.active(True)
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            pass
        print('WiFi connected:', wlan.ifconfig())
    else:
        print('Already connected to WiFi:', wlan.ifconfig())

while True:
    print("Scanning for WiFi networks, please wait...")
    print("")

    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)

    skoletest_found = False
    skoletest_rssi = 0

    for result in sta_if.scan():
        try:
            ssid = result[0].decode("utf-8")
            bssid = ':'.join('%02x' % b for b in result[1])
            channel = result[2]
            RSSI = result[3]
            authmode = authmodes[result[4]]
            hidden = result[5]

            if ssid == "Skoletest":
                skoletest_found = True
                print("Detected network: {:s}".format(ssid))
                print("   - Signalstyrke: {:d} dBm".format(RSSI))
                if RSSI < -25:
                    skoletest_rssi = RSSI
                    print("Signalstyrke under -25")
                    break

        except IndexError:
            pass

    if skoletest_found and skoletest_rssi < -25:
        print("Connecting to network 'Skoletest'...")
        connect_to_wifi("Skoletest", "1234567891")
        print("Connected to 'Skoletest'.")
        break

    if not skoletest_found:
        print("Skoletest netværk ikke fundet.")

    print("Scanning completed.")
    print("Waiting for next scan...")
    print("")
    time.sleep(scan_interval)
