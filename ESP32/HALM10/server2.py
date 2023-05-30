import network
import socket
import time
import _thread as thread

ssid = "Skoletest"
password = "1234567891"
server_port = 8000
timeout_duration = 10  # Timeout på 10 sekunder

server = None

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
    last_message_time = time.time()

    while True:
        data = client.recv(1024)
        if data:
            last_message_time = time.time()
            print('Received data:', data.decode())
        else:
            break

    client.close()
    print('Client disconnected.')

def timeout_check(client):
    last_message_time = time.time()

    while True:
        if time.time() - last_message_time > timeout_duration:
            print('Connection timeout. Disconnected.')
            client.close()
            break

def run_server():
    setup_server()
    connect_to_wifi()

    while True:
        client, _ = server.accept()
        print('New client connected.')

        # Start håndtering af klienten i en separat tråd
        thread.start_new_thread(handle_client, (client,))
        # Start timeout-tråden for klienten i en separat tråd
        thread.start_new_thread(timeout_check, (client,))

    # Genstart serveren efter timeout
    server.close()
    run_server()

# Kør serveren
run_server()
