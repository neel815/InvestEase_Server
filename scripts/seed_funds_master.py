"""
Seed script to populate funds_master table with mutual fund directory.
Uses psycopg2 directly for synchronous bulk insert.

Run: python scripts/seed_funds_master.py
"""

import os
import sys
from pathlib import Path
from urllib.parse import urlparse
import uuid

# Add Backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import psycopg2
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Database connection details from .env
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise Exception("DATABASE_URL not found in .env")

# Parse connection string: postgresql+asyncpg://user:password@host:port/dbname -> postgresql://user:password@host:port/dbname
# Remove the +asyncpg part for psycopg2
psycopg2_url = DATABASE_URL.replace("+asyncpg", "")

try:
    conn = psycopg2.connect(psycopg2_url)
    cursor = conn.cursor()
except Exception as e:
    print(f"❌ Connection failed: {e}")
    sys.exit(1)

# Fund data: (id, scheme_code, scheme_name, fund_house, category)
FUNDS = [
    # Large Cap (10 funds)
    (str(uuid.uuid4()), "118989", "Mirae Asset Large Cap Direct Growth", "Mirae Asset", "Large Cap"),
    (str(uuid.uuid4()), "120503", "Axis Bluechip Direct Growth", "Axis", "Large Cap"),
    (str(uuid.uuid4()), "119028", "HDFC Top 100 Direct Growth", "HDFC", "Large Cap"),
    (str(uuid.uuid4()), "120586", "ICICI Prudential Bluechip Direct Growth", "ICICI Prudential", "Large Cap"),
    (str(uuid.uuid4()), "119255", "SBI Bluechip Direct Growth", "SBI", "Large Cap"),
    (str(uuid.uuid4()), "120841", "Kotak Bluechip Direct Growth", "Kotak", "Large Cap"),
    (str(uuid.uuid4()), "118701", "Nippon India Large Cap Direct Growth", "Nippon India", "Large Cap"),
    (str(uuid.uuid4()), "120818", "UTI Mastershare Direct Growth", "UTI", "Large Cap"),
    (str(uuid.uuid4()), "118825", "Canara Robeco Bluechip Direct Growth", "Canara Robeco", "Large Cap"),
    (str(uuid.uuid4()), "119006", "DSP Top 100 Equity Direct Growth", "DSP", "Large Cap"),
    
    # Mid Cap (10 funds)
    (str(uuid.uuid4()), "120505", "Axis Midcap Direct Growth", "Axis", "Mid Cap"),
    (str(uuid.uuid4()), "119027", "HDFC Mid-Cap Opportunities Direct Growth", "HDFC", "Mid Cap"),
    (str(uuid.uuid4()), "120839", "Kotak Emerging Equity Direct Growth", "Kotak", "Mid Cap"),
    (str(uuid.uuid4()), "118699", "Nippon India Growth Fund Direct Growth", "Nippon India", "Mid Cap"),
    (str(uuid.uuid4()), "119253", "SBI Magnum Midcap Direct Growth", "SBI", "Mid Cap"),
    (str(uuid.uuid4()), "145163", "Quant Mid Cap Direct Growth", "Quant", "Mid Cap"),
    (str(uuid.uuid4()), "135781", "Motilal Oswal Midcap Direct Growth", "Motilal Oswal", "Mid Cap"),
    (str(uuid.uuid4()), "133550", "Edelweiss Mid Cap Direct Growth", "Edelweiss", "Mid Cap"),
    (str(uuid.uuid4()), "120170", "Invesco India Mid Cap Direct Growth", "Invesco", "Mid Cap"),
    (str(uuid.uuid4()), "119775", "Franklin India Prima Direct Growth", "Franklin", "Mid Cap"),
    
    # Small Cap (10 funds)
    (str(uuid.uuid4()), "120828", "Quant Small Cap Direct Growth", "Quant", "Small Cap"),
    (str(uuid.uuid4()), "118778", "Nippon India Small Cap Direct Growth", "Nippon India", "Small Cap"),
    (str(uuid.uuid4()), "119256", "SBI Small Cap Direct Growth", "SBI", "Small Cap"),
    (str(uuid.uuid4()), "120507", "Axis Small Cap Direct Growth", "Axis", "Small Cap"),
    (str(uuid.uuid4()), "119030", "HDFC Small Cap Direct Growth", "HDFC", "Small Cap"),
    (str(uuid.uuid4()), "120843", "Kotak Small Cap Direct Growth", "Kotak", "Small Cap"),
    (str(uuid.uuid4()), "119008", "DSP Small Cap Direct Growth", "DSP", "Small Cap"),
    (str(uuid.uuid4()), "147946", "Canara Robeco Small Cap Direct Growth", "Canara Robeco", "Small Cap"),
    (str(uuid.uuid4()), "148150", "Union Small Cap Direct Growth", "Union", "Small Cap"),
    (str(uuid.uuid4()), "145114", "Tata Small Cap Direct Growth", "Tata", "Small Cap"),
    
    # Flexi Cap (10 funds)
    (str(uuid.uuid4()), "122639", "Parag Parikh Flexi Cap Direct Growth", "Parag Parikh", "Flexi Cap"),
    (str(uuid.uuid4()), "119029", "HDFC Flexi Cap Direct Growth", "HDFC", "Flexi Cap"),
    (str(uuid.uuid4()), "120840", "Kotak Flexicap Direct Growth", "Kotak", "Flexi Cap"),
    (str(uuid.uuid4()), "120819", "UTI Flexi Cap Direct Growth", "UTI", "Flexi Cap"),
    (str(uuid.uuid4()), "120506", "Axis Flexi Cap Direct Growth", "Axis", "Flexi Cap"),
    (str(uuid.uuid4()), "118826", "Canara Robeco Flexi Cap Direct Growth", "Canara Robeco", "Flexi Cap"),
    (str(uuid.uuid4()), "125354", "SBI Flexicap Direct Growth", "SBI", "Flexi Cap"),
    (str(uuid.uuid4()), "119776", "Franklin India Flexi Cap Direct Growth", "Franklin", "Flexi Cap"),
    (str(uuid.uuid4()), "119007", "DSP Flexi Cap Direct Growth", "DSP", "Flexi Cap"),
    (str(uuid.uuid4()), "118700", "Nippon India Flexi Cap Direct Growth", "Nippon India", "Flexi Cap"),
    
    # Hybrid (10 funds)
    (str(uuid.uuid4()), "119026", "HDFC Balanced Advantage Direct Growth", "HDFC", "Hybrid"),
    (str(uuid.uuid4()), "120584", "ICICI Prudential Balanced Advantage Direct Growth", "ICICI Prudential", "Hybrid"),
    (str(uuid.uuid4()), "120838", "Kotak Balanced Advantage Direct Growth", "Kotak", "Hybrid"),
    (str(uuid.uuid4()), "119252", "SBI Equity Hybrid Direct Growth", "SBI", "Hybrid"),
    (str(uuid.uuid4()), "118988", "Mirae Asset Hybrid Equity Direct Growth", "Mirae Asset", "Hybrid"),
    (str(uuid.uuid4()), "120504", "Axis Equity Hybrid Direct Growth", "Axis", "Hybrid"),
    (str(uuid.uuid4()), "119005", "DSP Equity and Bond Direct Growth", "DSP", "Hybrid"),
    (str(uuid.uuid4()), "118824", "Canara Robeco Equity Hybrid Direct Growth", "Canara Robeco", "Hybrid"),
    (str(uuid.uuid4()), "120817", "UTI Aggressive Hybrid Direct Growth", "UTI", "Hybrid"),
    (str(uuid.uuid4()), "118698", "Nippon India Balanced Advantage Direct Growth", "Nippon India", "Hybrid"),
    
    # ELSS (10 funds)
    (str(uuid.uuid4()), "120502", "Axis Long Term Equity Direct Growth", "Axis", "ELSS"),
    (str(uuid.uuid4()), "118987", "Mirae Asset Tax Saver Direct Growth", "Mirae Asset", "ELSS"),
    (str(uuid.uuid4()), "119251", "SBI Long Term Equity Direct Growth", "SBI", "ELSS"),
    (str(uuid.uuid4()), "119025", "HDFC Taxsaver Direct Growth", "HDFC", "ELSS"),
    (str(uuid.uuid4()), "120837", "Kotak Tax Saver Direct Growth", "Kotak", "ELSS"),
    (str(uuid.uuid4()), "120827", "Quant Tax Plan Direct Growth", "Quant", "ELSS"),
    (str(uuid.uuid4()), "119004", "DSP Tax Saver Direct Growth", "DSP", "ELSS"),
    (str(uuid.uuid4()), "118823", "Canara Robeco Equity Tax Saver Direct Growth", "Canara Robeco", "ELSS"),
    (str(uuid.uuid4()), "118697", "Nippon India Tax Saver Direct Growth", "Nippon India", "ELSS"),
    (str(uuid.uuid4()), "119774", "Franklin India Taxshield Direct Growth", "Franklin", "ELSS"),
    
    # Index (10 funds)
    (str(uuid.uuid4()), "120986", "Mirae Asset Nifty 50 ETF Direct Growth", "Mirae Asset", "Index"),
    (str(uuid.uuid4()), "120679", "HDFC Index Nifty 50 Direct", "HDFC", "Index"),
    (str(uuid.uuid4()), "120871", "UTI Nifty 50 Index Direct Growth", "UTI", "Index"),
    (str(uuid.uuid4()), "120780", "SBI Nifty Index Direct Growth", "SBI", "Index"),
    (str(uuid.uuid4()), "120620", "ICICI Prudential Nifty 50 Index Direct Growth", "ICICI Prudential", "Index"),
    (str(uuid.uuid4()), "120680", "HDFC Nifty Next 50 Direct Growth", "HDFC", "Index"),
    (str(uuid.uuid4()), "120845", "Kotak Nifty 50 Index Direct Growth", "Kotak", "Index"),
    (str(uuid.uuid4()), "146359", "DSP Nifty 50 Index Direct Growth", "DSP", "Index"),
    (str(uuid.uuid4()), "148511", "Axis Nifty 100 Index Direct Growth", "Axis", "Index"),
    (str(uuid.uuid4()), "147622", "Motilal Oswal Nifty Midcap 150 Index Direct Growth", "Motilal Oswal", "Index"),
]

# Insert funds with conflict handling
sql = """
INSERT INTO funds_master (id, scheme_code, scheme_name, fund_house, category, is_active)
VALUES (%s, %s, %s, %s, %s, true)
ON CONFLICT (scheme_code) DO NOTHING;
"""

try:
    cursor.executemany(sql, FUNDS)
    conn.commit()
    
    # Get count of funds in table
    cursor.execute("SELECT COUNT(*) FROM funds_master;")
    count = cursor.fetchone()[0]
    
    print(f"✅ Seeded {len(FUNDS)} funds successfully")
    print(f"✅ Total funds in database: {count}")
    
except Exception as e:
    conn.rollback()
    print(f"❌ Seeding failed: {e}")
    sys.exit(1)

finally:
    cursor.close()
    conn.close()
