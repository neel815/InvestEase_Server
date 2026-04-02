import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
url = os.getenv('DATABASE_URL').replace('+asyncpg', '')
conn = psycopg2.connect(url)
cur = conn.cursor()

# Check tables
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name")
tables = [row[0] for row in cur.fetchall()]
print(f"✅ Total tables: {len(tables)}")
print("Tables:", ", ".join(tables))

conn.close()
