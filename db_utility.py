import sqlite3

# 1. Connect to the database file
conn = sqlite3.connect('instance/database.db')
cursor = conn.cursor()

# 2. Optional: See what tables exist in the database
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("Tables:", cursor.fetchall())

# 3. View data from a specific table
cursor.execute("SELECT * FROM user;")
rows = cursor.fetchall()

for row in rows:
    print(row)

# 4. Always close the connection when finished
conn.close()




