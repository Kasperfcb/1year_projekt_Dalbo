import socket
import utime

# Opretter en TCP-serversocket
server_ip = '192.168.75.151'  # IP-adresse for serveren
server_port = 1234  # Portnummer for serveren

# Opretter en TCP-serversocket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Opsætning af serveren
server_socket.bind((server_ip, server_port))
server_socket.listen(1)

# Vent på en klientforbindelse
print('Venter på klientforbindelse...')
client_socket, client_address = server_socket.accept()
print('Forbundet til klient:', client_address)

# Send en besked til klienten
message = "Hej fra serveren!"
client_socket.send(message.encode('utf-8'))

# Start tidstagning
start_time = utime.time()
print("Tidstagning startede.")

# Åbn logfilen
log_file = open("server_log.txt", "a")
log_file.write("Forbindelse etableret: " + utime.ctime() + "\n")

# Modtag en besked fra klienten
received_message = client_socket.recv(1024).decode('utf-8')
print('Modtaget besked fra klienten:', received_message)

# Modtag beskeder fra klienten og send svar
while True:
    try:
        # Modtag en besked fra klienten
        received_message = client_socket.recv(1024).decode('utf-8')
        print('Modtaget besked fra klienten:', received_message)
        
        if received_message == 'luk':
            # Hvis klienten sender 'luk', afsluttes forbindelsen
            break
        
        # Send en besked til klienten
        message = "Modtog din besked: " + received_message
        client_socket.send(message.encode('utf-8'))
    
    except ConnectionResetError:
        print('Klientforbindelse afbrudt.')
        break

# Stop tidstagning
end_time = utime.time()
elapsed_time = end_time - start_time
print("Tidstagning stoppede.")
print("Tid brugt:", elapsed_time, "sekunder")

# Skriv information til logfilen
log_file.write("Forbindelse afbrudt: " + utime.ctime() + "\n")
log_file.write("Tid brugt: " + str(elapsed_time) + " sekunder\n")
log_file.close()

# Luk forbindelsen
client_socket.close()
server_socket.close()
