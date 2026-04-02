import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
url = os.getenv('DATABASE_URL').replace('+asyncpg', '')
conn = psycopg2.connect(url)
cur = conn.cursor()

# Create explore_holdings table
sql = """
CREATE TABLE IF NOT EXISTS explore_holdings (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    goal_id UUID NOT NULL REFERENCES goals(id),
    scheme_code VARCHAR(50) NOT NULL,
    scheme_name VARCHAR(200) NOT NULL,
    category VARCHAR(100) NOT NULL,
    units FLOAT NOT NULL,
    average_nav FLOAT NOT NULL,
    invested_amount NUMERIC(14, 2) NOT NULL,
    current_value NUMERIC(14, 2) NOT NULL,
    last_known_nav FLOAT,
    nav_last_updated TIMESTAMP,
    last_updated TIMESTAMP,
    created_at TIMESTAMP
);
"""

cur.execute(sql)
conn.commit()

# Create indexes
cur.execute("CREATE INDEX IF NOT EXISTS ix_explore_holdings_user_id ON explore_holdings(user_id);")
cur.execute("CREATE INDEX IF NOT EXISTS ix_explore_holdings_goal_id ON explore_holdings(goal_id);")
conn.commit()

# Create funds_master table
sql_funds = """
CREATE TABLE IF NOT EXISTS funds_master (
    id UUID PRIMARY KEY,
    scheme_code VARCHAR(20) UNIQUE NOT NULL,
    scheme_name VARCHAR(255) NOT NULL,
    fund_house VARCHAR(100),
    category VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT true NOT NULL,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL
);
"""

cur.execute(sql_funds)
conn.commit()

# Create indexes for funds_master
cur.execute("CREATE INDEX IF NOT EXISTS ix_funds_master_scheme_code ON funds_master(scheme_code);")
cur.execute("CREATE INDEX IF NOT EXISTS ix_funds_master_scheme_name ON funds_master(scheme_name);")
cur.execute("CREATE INDEX IF NOT EXISTS ix_funds_master_category ON funds_master(category);")
cur.execute("CREATE INDEX IF NOT EXISTS ix_funds_master_category_active ON funds_master(category, is_active);")
conn.commit()

print("✅ Tables created successfully")
conn.close()
