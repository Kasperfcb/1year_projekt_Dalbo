import socket
import time
import _thread as thread
import network

ssid = "Skoletest"
password = "1234567891"
server_port = 8005

timeout_duration = 5  # Timeout på 5 sekunder

server = None
last_message_time = 0
is_connected = False

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

    while True:
        try:
            data = client.recv(1024)
            if data:
                last_message_time = time.time()
                print('Received data:', data.decode())
                is_connected = True
                # Send data til Raspberry Pi
                send_data_to_pi(data.decode())
        except OSError as e:
            if e.args[0] == 128:
                # Socket is not connected
                break

    client.close()
    print('Client disconnected.')

def timeout_check(client):
    global last_message_time, is_connected

    while True:
        current_time = time.time()
        if is_connected and current_time - last_message_time > timeout_duration:
            print('Connection timeout. Disconnected.')
            if client.fileno() != -1:
                client.close()
            print('Disconnected')
            is_connected = False
            break

        time.sleep(1)

def run_server():
    setup_server()
    connect_to_wifi()

    while True:
        client, _ = server.accept()
        print('New client connected.')
        last_message_time = time.time()
        is_connected = True

        # Start håndtering af klienten i en separat tråd
        thread.start_new_thread(handle_client, (client,))
        # Start timeout-tråden for klienten i en separat tråd
        thread.start_new_thread(timeout_check, (client,))

    # Genstart serveren efter timeout
    server.close()
    run_server()

def send_data_to_pi(data):
    pi_ip = "192.168.43.134"
    pi_port = 8005

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((pi_ip, pi_port))
    client.sendall(data.encode())
    client.close()

# Kør serveren
run_server()
