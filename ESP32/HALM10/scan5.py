import network
import time
import socket

authmodes = ['Open', 'WEP', 'WPA-PSK', 'WPA2-PSK', 'WPA/WPA2-PSK']
scan_interval = 5  # Angiv intervallet i sekunder mellem hver scanning
pi_ip = "192.168.43.134"  # Replace with your Raspberry Pi's IP address
pi_port = 8006  # Replace with the port number on which your Raspberry Pi is listening

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

def send_message(message):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((pi_ip, pi_port))
        s.send(message.encode())
        print('Message sent to Raspberry Pi:', message)
    except OSError as e:
        print('Error sending message:', str(e))
    s.close()

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

            if ssid == "Dør1":
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
        print("Connecting to network 'ROyaRO'...")
        connect_to_wifi("ROyaRO", "RoyaR195")
        print("Connected to 'ROyaRO'.")
        current_time = time.localtime()
        formatted_time = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
            current_time[0], current_time[1], current_time[2],
            current_time[3], current_time[4], current_time[5]
        )
        message = "Connected to 'ROyaRO' at {}".format(formatted_time)
        send_message(message)
        break

    if not skoletest_found:
        print("ROyaRO netværk ikke fundet.")

    print("Scanning completed.")
    print("Waiting for next scan...")
    print("")
    time.sleep(scan_interval)
