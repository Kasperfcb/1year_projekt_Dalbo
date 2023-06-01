import network
import utime
import socket
import ntptime
import machine
from machine import Pin, ADC

authmodes = ['Open', 'WEP', 'WPA-PSK', 'WPA2-PSK', 'WPA/WPA2-PSK']
scan_interval = 1  # Interval in seconds between each scan
battery_check_interval = 12  # Interval in seconds for checking the battery level
pi_ip = "192.168.43.71"  # Replace with your Raspberry Pi's IP address
pi_port = 8002  # Replace with the port number on which your Raspberry Pi is listening
time_difference = 2  # Time difference in hours from UTC

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

def set_local_time():
    ntptime.settime()
    rtc = machine.RTC()
    t = utime.localtime(utime.mktime(utime.gmtime()) + (time_difference * 3600))
    rtc.datetime(t[0:3] + (0,) + t[3:6] + (0,))

def send_message(message):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((pi_ip, pi_port))
        s.send(message.encode())
        print('Message sent to Raspberry Pi:', message)
    except OSError as e:
        print('Error sending message:', str(e))
    s.close()

def measure_battery_percentage():
    bat = ADC(Pin(33))
    bat.atten(ADC.ATTN_11DB)
    bat.width(ADC.WIDTH_12BIT)
    controlbat = 3.90
    control_spændingsdeler = 2.64
    scaling = controlbat / control_spændingsdeler

    bat_val = bat.read() * scaling
    m_voltage = bat_val / 4095 * 3.3
    percentage = (m_voltage - 3.0) / (4.2 - 3.0) * 100
    percentage = max(0, min(percentage, 100))
    return percentage

connected_to_dor1 = False
connected_to_dor2 = False
last_battery_check_time = 0

while True:
    print("Scanning for WiFi networks, please wait...")
    print("")

    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)

    dor1_found = False
    dor2_found = False

    for result in sta_if.scan():
        try:
            ssid = result[0].decode("utf-8")
            RSSI = result[3]

            if ssid == "Dør1" and RSSI > -25 and not connected_to_dor1:
                print("Detected network: {:s}".format(ssid))
                print("   - Signalstyrke: {:d} dBm".format(RSSI))
                print("Connecting to network 'ROyaRO'...")
                connect_to_wifi("ROyaRO", "RoyaR195")
                print("Connected to 'ROyaRO'.")
                set_local_time()  # Update the local time
                current_time = utime.localtime()
                formatted_time = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
                    current_time[0], current_time[1], current_time[2],
                    current_time[3], current_time[4], current_time[5]
                )
                message = "Hamlen nr 10 er indadgående' at {}".format(formatted_time)
                send_message(message)
                connected_to_dor1 = True
                dor1_found = True

            if ssid == "Dør2" and RSSI > -25 and connected_to_dor1 and not connected_to_dor2:
                print("Detected network: {:s}".format(ssid))
                print("   - Signalstyrke: {:d} dBm".format(RSSI))
                connected_to_dor2 = True
                dor2_found = True
                current_time = utime.localtime()
                formatted_time = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
                    current_time[0], current_time[1], current_time[2],
                    current_time[3], current_time[4], current_time[5]
                )
                message = "Hamlen nr 10 er udadgående' at {}".format(formatted_time)
                send_message(message)
                break

        except IndexError:
            pass

    if not dor1_found:
        print("Dør1 network not found or signal strength is not below -25 dBm.")

    if connected_to_dor1 and not dor2_found:
        print("Dør2 network not found or signal strength is not below -25 dBm.")
        current_time = utime.time()
        if current_time - last_battery_check_time >= battery_check_interval:
            battery_percentage = measure_battery_percentage()
            print("Batteriniveau : {:.2f}%".format(battery_percentage))
            message = "Batteriniveau fra hamel 10: {:.2f}%".format(battery_percentage)
            send_message(message)
            last_battery_check_time = current_time

    if connected_to_dor1 and connected_to_dor2:
        break

    print("Scanning completed.")
    print("Waiting for next scan...")
    print("")
    utime.sleep(scan_interval)

