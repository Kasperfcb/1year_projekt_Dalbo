import network
import socket
import time
import uasyncio as asyncio

ssid = "Skoletest"
password = "1234567891"
server_port = 8005
raspberry_pi_ip = "192.168.43.134"  # Indsæt Raspberry Pi's IP-adresse her

server = None
last_message_time = 0
is_connected = False

async def setup_server():
    global server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', server_port))
    server.listen(1)
    print('Server started.')

async def connect_to_wifi():
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.connect(ssid, password)

    while not wifi.isconnected():
        await asyncio.sleep(0.1)

    print('Connected to WiFi:', wifi.ifconfig())

async def handle_client(client):
    global last_message_time, is_connected

    while True:
        try:
            data = client.recv(1024)
            if data:
                message = data.decode().strip()
                last_message_time = time.time()
                if message == "Hej":
                    print('Received data:', message)
                    is_connected = True
                    # Send bekræftelsesbesked tilbage til klienten
                    client.sendall("Bekræftelse: Besked modtaget".encode())
                    send_data_to_raspberry_pi(message)  # Send data til Raspberry Pi
        except OSError as e:
            if e.args[0] == 128:
                # Socket is not connected
                break

    client.close()
    print('Client disconnected.')

async def timeout_check(client):
    global last_message_time, is_connected

    while True:
        current_time = time.time()
        if is_connected and current_time - last_message_time > timeout_duration:
            print('Connection timeout. Disconnected.')
            if client.fileno() != -1:
                client.close()
            is_connected = False
            break

        await asyncio.sleep(1)

def send_data_to_raspberry_pi(data):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((raspberry_pi_ip, server_port))
        s.sendall(data.encode())
        s.close()
        print('Sent data to Raspberry Pi:', data)
    except OSError as e:
        print('Failed to send data to Raspberry Pi:', e)

async def run_server():
    await setup_server()
    await connect_to_wifi()

    while True:
        client, _ = server.accept()
        current_time = time.localtime()
        formatted_time = f"{current_time[0]}-{current_time[1]:02d}-{current_time[2]:02d} {current_time[3]:02d}:{current_time[4]:02d}:{current_time[5]:02d}"
        print('New client connected at', formatted_time)
        last_message_time = time.time()
        is_connected = True

        # Start håndtering af klienten
        asyncio.create_task(handle_client(client))
        # Start timeout-tråden for klienten
        asyncio.create_task(timeout_check(client))

    # Genstart serveren efter timeout
    server.close()
    await run_server()

# Kør serveren
asyncio.run(run_server())
