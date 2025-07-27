import sqlite3

con = sqlite3.connect("agentic.db")
cur = con.cursor()
results = cur.execute("SELECT name FROM sqlite_master").fetchall()
tables= [res[0] for res in results]
print(f"Tables: {tables}")
for table in tables:
    cur.execute(f"SELECT * FROM {table}")
    headers = [description[0] for description in cur.description]
    cur.execute(f"SELECT * FROM {table} ORDER BY RANDOM() LIMIT 5")
    rows = cur.fetchall()
    print(f"-----------[{table}]---------")
    print(headers)
    for row in rows:
        print(row)
