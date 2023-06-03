import socket
import sqlite3

server_ip = "192.168.43.71"  # Lyt på server's netværksinterfaces
server_port = 8002
dbname = "min_database.db"

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((server_ip, server_port))
    server.listen(1)
    print('Server startet. Venter på forbindelser...')

    while True:
        client, addr = server.accept()
        print('Ny forbindelse fra:', addr[0])
        handle_connection(client)

def handle_connection(client):
    while True:
        data = client.recv(1024)
        if data:
            message = data.decode().strip()
            print('Modtaget data:', message)

            try:
                conn = sqlite3.connect(dbname)
                cursor = conn.cursor()
                sql = "INSERT INTO min_tabel (kolonne1) VALUES (?)"  #Indsæt data i databasen
                data = (message,)
                cursor.execute(sql, data)
                conn.commit()
                print('Data blev indsat i databasen.')
            except sqlite3.Error as e:
                print('Fejl ved indsættelse af data:', str(e))
            finally:
                cursor.close()
                conn.close()
        else:
            break

    client.close()
    print('...')

start_server() # Start serveren
