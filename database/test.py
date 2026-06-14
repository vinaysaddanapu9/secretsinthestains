import sqlite3

conn = sqlite3.connect("database.db")
cur = conn.cursor()

cur.execute("SELECT * FROM messages")
print(cur.fetchall())

conn.close()