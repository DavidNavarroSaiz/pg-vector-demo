import psycopg2
import numpy as np
from dotenv import load_dotenv
import os

load_dotenv()

db_name = os.getenv("DB_NAME")
db_username = os.getenv("DB_USERNAME")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")

connection_string = f"dbname={db_name} user={db_username} password={db_password} host={db_host} port={db_port}"
print("connection_string", connection_string)

# Connect to the database
conn = psycopg2.connect(connection_string)
cur = conn.cursor()

# Insert a vector
embedding = np.array([1.5, 2.5, 3.5])
cur.execute("INSERT INTO items (embedding) VALUES (%s)", (embedding.tolist(),))

# Perform a similarity search with explicit cast to vector
query_vector = np.array([2, 3, 4])
cur.execute("SELECT * FROM items ORDER BY embedding <-> %s::vector LIMIT 1", (query_vector.tolist(),))

result = cur.fetchone()
print(f"Nearest neighbor: {result}")

conn.commit()
cur.close()
conn.close()
