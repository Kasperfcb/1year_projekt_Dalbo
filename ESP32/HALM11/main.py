import network
import utime
import socket
import ntptime
import machine
from machine import Pin, ADC

authmodes = ['Open', 'WEP', 'WPA-PSK', 'WPA2-PSK', 'WPA/WPA2-PSK']
scan_interval = 0.5  # hvor ofte den skal scanne efter netværk
battery_check_interval = 1  # hvor ofte den skal tjekke batteriniveau
battery_send_interval = 10  # hvor ofte den skal sende batteriniveau
pi_ip = "192.168.43.71"  # ip adressen på vores pi/computer
pi_port = 8002  #port nummer som vores pi/computer lytter på
time_difference = 2  # lægge to til på tiden i utc

led_pin = Pin(32, Pin.OUT)  # GPIO pin nummer for vores led 
battery_threshold = 20  # led blinker hvis batteriniveau er under 20

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
    controlbat = 4.18
    control_spændingsdeler = 2.64
    scaling = controlbat / control_spændingsdeler

    bat_val = bat.read() * scaling
    m_voltage = bat_val / 4095 * 3.3
    percentage = (m_voltage - 3.0) / (4.2 - 3.0) * 100
    percentage = max(0, min(percentage, 100))

    # Check if battery percentage is below threshold
    if percentage < battery_threshold:
        led_pin.on()  # Turn on the LED
        utime.sleep(0.5)  # Wait for 0.5 seconds
        led_pin.off()  # Turn off the LED

    return percentage

connected_to_dor1 = False
connected_to_dor2 = False
last_battery_check_time = 0
last_battery_send_time = 0

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

            if ssid == "Dør1" and RSSI > -45 and not connected_to_dor1:
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
                message = "Hamlen nr 11 er indadgående' at {}".format(formatted_time)
                send_message(message)
                connected_to_dor1 = True
                dor1_found = True

            if ssid == "Dør2" and RSSI > -45 and connected_to_dor1 and not connected_to_dor2:
                print("Detected network: {:s}".format(ssid))
                print("   - Signalstyrke: {:d} dBm".format(RSSI))
                connected_to_dor2 = True
                dor2_found = True
                current_time = utime.localtime()
                formatted_time = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
                    current_time[0], current_time[1], current_time[2],
                    current_time[3], current_time[4], current_time[5]
                )
                message = "Hamlen nr 11 er udadgående' at {}".format(formatted_time)
                send_message(message)
                break

        except IndexError:
            pass

    current_time = utime.time()

    if current_time - last_battery_check_time >= battery_check_interval:
        battery_percentage = measure_battery_percentage()
        print("Battery level: {:.2f}%".format(battery_percentage))
        last_battery_check_time = current_time

    if current_time - last_battery_send_time >= battery_send_interval:
        message = "Battery level from Hamlen 11: {:.2f}%".format(battery_percentage)
        send_message(message)
        last_battery_send_time = current_time

    if not dor1_found:
        print("Dør1 network not found or signal strength is not below -45 dBm.")

    if connected_to_dor1 and not dor2_found:
        print("Dør2 network not found or signal strength is not below -45 dBm.")

    if connected_to_dor1 and connected_to_dor2:
        break

    print("Scanning completed.")
    print("Waiting for next scan...")
    print("")
    utime.sleep(scan_interval)



