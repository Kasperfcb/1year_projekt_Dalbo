import sqlite3

# Opret forbindelse til databasen
conn = sqlite3.connect('min_database.db')

# Opret en databaseforbindelse
cursor = conn.cursor()

# Hent indholdet fra tabellen
cursor.execute("SELECT * FROM min_tabel")
rows = cursor.fetchall()

# Udskriv hver række
for row in rows:
    print(row)

# Luk forbindelsen til databasen
conn.close()
