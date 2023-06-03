import sqlite3

conn = sqlite3.connect('min_database.db') # Opret forbindelse til databasen
cursor = conn.cursor()  # Opret en databaseforbindelse
cursor.execute('''CREATE TABLE IF NOT EXISTS min_tabel
                  (kolonne1 TEXT, kolonne2 TEXT)''')  # Opret en tabel med to kolonner til tekst
data = ('Hej', 'Verden')
cursor.execute("INSERT INTO min_tabel (kolonne1, kolonne2) VALUES (?, ?)", data)
conn.commit()
conn.close() # Gem ændringer og luk forbindelsen til databasen
