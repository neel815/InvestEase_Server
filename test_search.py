import asyncio
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
url = os.getenv('DATABASE_URL').replace('+asyncpg', '')
conn = psycopg2.connect(url)
cur = conn.cursor()

# Search for HDFC funds
cur.execute("SELECT scheme_code, scheme_name FROM funds_master WHERE scheme_name ILIKE '%hdfc%' AND is_active = true LIMIT 20")
results = cur.fetchall()

print(f'✅ Search test: Found {len(results)} HDFC funds')
for code, name in results[:5]:
    print(f'  - {code}: {name}')

# Count all funds
cur.execute("SELECT COUNT(*) FROM funds_master")
total = cur.fetchone()[0]
print(f'✅ Total funds in database: {total}')

conn.close()
