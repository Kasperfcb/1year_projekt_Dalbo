import socket
import time
import _thread as thread
import network

ssid = "Skoletest"
password = "1234567891"
server_port = 8001

server = None
last_message_time = 0
is_connected = False
timeout_duration = 5  # Timeout på 5 sekunder (kan ændres efter behov)

def setup_server():
    global server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', server_port))
    server.listen(1)
    print('Server started.')

def connect_to_wifi():
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.connect(ssid, password)

    while not wifi.isconnected():
        pass

    print('Connected to WiFi:', wifi.ifconfig())

def handle_client(client):
    global last_message_time, is_connected

    print('Client disconnected.')

def timeout_check(client):
    global last_message_time, is_connected

    while True:
        current_time = time.time()
        if is_connected and current_time - last_message_time > timeout_duration:
            print('Connection timeout. Disconnected.')
            if client.fileno() != -1:
                client.close()
            is_connected = False
            break

        time.sleep(1)

def run_server():
    setup_server()
    connect_to_wifi()

    while True:
        client, _ = server.accept()
        current_time = time.localtime()
        formatted_time = f"{current_time[0]}-{current_time[1]:02d}-{current_time[2]:02d} {current_time[3]:02d}:{current_time[4]:02d}:{current_time[5]:02d}"
        print('New client connected at', formatted_time)
        last_message_time = time.time()
        is_connected = True

        # Start håndtering af klienten i en separat tråd
        thread.start_new_thread(handle_client, (client,))
        # Start timeout-tråden for klienten i en separat tråd
        thread.start_new_thread(timeout_check, (client,))

    # Genstart serveren efter timeout
    server.close()
    run_server()

# Kør serveren
run_server()
