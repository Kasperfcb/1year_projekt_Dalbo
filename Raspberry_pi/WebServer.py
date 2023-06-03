from flask import Flask, render_template
from flask_socketio import SocketIO
import sqlite3

app = Flask(__name__)
socketio = SocketIO(app)

dbname = "min_database.db"

def get_data_from_database():
    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM min_tabel")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

@app.route('/')
def index():
    data = get_data_from_database()
    return render_template('index.html', data=data)

@socketio.on('connect')
def on_connect():
    print('Ny Socket.IO-forbindelse etableret')

@socketio.on('disconnect')
def on_disconnect():
    print('Socket.IO-forbindelse afbrudt')

@socketio.on('get_data')
def emit_data():
    data = get_data_from_database()
    socketio.emit('data_update', data)

if __name__ == '__main__':
    socketio.run(app)
