import network
import socket
import time

ssid = "Skoletest"
password = "1234567891"

server = None
client = None
start_time = 0
timeout_duration = 5  # Timeout på 5 sekunder

def setup_server():
    global server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 80))
    server.listen(1)
    print('Server started.')

def connect_to_wifi():
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.connect(ssid, password)

    while not wifi.isconnected():
        pass

    print('Connected to WiFi:', wifi.ifconfig())

def handle_client():
    global client, start_time

    client = None
    start_time = 0

    try:
        client, _ = server.accept()
        client.settimeout(timeout_duration)
        print('New client connected.')

        start_time = time.time()

        while client:
            try:
                data = client.recv(1024)

                if data:
                    current_time = time.time()
                    elapsed_time = int((current_time - start_time) * 1000)

                    # Send opdateringer til klienten
                    client.sendall("Timer: {} ms\r\n".format(elapsed_time))

                    print("Timer: {} ms".format(elapsed_time))
                else:
                    break

            except socket.timeout:
                disconnect_client()
                print("Client connection timed out.")
                break

            time.sleep(1)  # Vent et sekund mellem opdateringer

    except Exception as e:
        print("Error:", e)
        disconnect_client()

def disconnect_client():
    global client, start_time

    if client is not None:
        client.close()
        client = None

    start_time = 0

    print("Client disconnected.")

connect_to_wifi()
setup_server()

while True:
    handle_client()
    disconnect_client()
