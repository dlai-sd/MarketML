"""Script to populate enrichment databases with Indian market data."""

import sqlite3
import json
from pathlib import Path

DATA_DIR = Path("data/enrichment")
DATA_DIR.mkdir(parents=True, exist_ok=True)


def create_location_database():
    """Create and populate location enrichment database."""
    db_path = DATA_DIR / "locations.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cities (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            state TEXT NOT NULL,
            tier INTEGER NOT NULL,
            population INTEGER,
            affluence_score INTEGER,
            digital_penetration INTEGER,
            business_density INTEGER,
            avg_income INTEGER
        )
    """)
    
    # Indian cities data
    cities_data = [
        # Tier 1 Cities
        ("Mumbai", "Maharashtra", 1, 20000000, 85, 80, 90, 75000),
        ("Delhi", "Delhi", 1, 19000000, 85, 82, 88, 70000),
        ("Bangalore", "Karnataka", 1, 12000000, 88, 90, 92, 80000),
        ("Hyderabad", "Telangana", 1, 10000000, 82, 85, 85, 65000),
        ("Chennai", "Tamil Nadu", 1, 9000000, 80, 83, 84, 65000),
        ("Kolkata", "West Bengal", 1, 15000000, 75, 78, 80, 55000),
        ("Pune", "Maharashtra", 1, 6500000, 83, 88, 87, 72000),
        ("Ahmedabad", "Gujarat", 1, 7500000, 78, 80, 82, 60000),
        
        # Tier 2 Cities
        ("Jaipur", "Rajasthan", 2, 3500000, 72, 75, 70, 50000),
        ("Lucknow", "Uttar Pradesh", 2, 3200000, 68, 70, 68, 45000),
        ("Kanpur", "Uttar Pradesh", 2, 3000000, 65, 68, 65, 42000),
        ("Nagpur", "Maharashtra", 2, 2500000, 70, 72, 72, 48000),
        ("Indore", "Madhya Pradesh", 2, 2700000, 73, 74, 71, 50000),
        ("Thane", "Maharashtra", 2, 2200000, 80, 82, 80, 65000),
        ("Bhopal", "Madhya Pradesh", 2, 2000000, 68, 70, 67, 45000),
        ("Visakhapatnam", "Andhra Pradesh", 2, 2100000, 70, 73, 69, 48000),
        ("Pimpri-Chinchwad", "Maharashtra", 2, 1800000, 78, 80, 78, 60000),
        ("Patna", "Bihar", 2, 2000000, 60, 65, 60, 38000),
        ("Vadodara", "Gujarat", 2, 1800000, 75, 77, 74, 55000),
        ("Ghaziabad", "Uttar Pradesh", 2, 1700000, 70, 73, 70, 50000),
        ("Ludhiana", "Punjab", 2, 1600000, 72, 74, 72, 52000),
        ("Agra", "Uttar Pradesh", 2, 1600000, 65, 68, 65, 42000),
        ("Nashik", "Maharashtra", 2, 1500000, 72, 75, 70, 50000),
        ("Faridabad", "Haryana", 2, 1500000, 73, 76, 73, 54000),
        ("Meerut", "Uttar Pradesh", 2, 1400000, 68, 70, 68, 45000),
        ("Rajkot", "Gujarat", 2, 1400000, 74, 76, 73, 53000),
        ("Kalyan-Dombivali", "Maharashtra", 2, 1300000, 76, 78, 75, 58000),
        ("Vasai-Virar", "Maharashtra", 2, 1300000, 74, 76, 73, 55000),
        ("Varanasi", "Uttar Pradesh", 2, 1200000, 62, 65, 62, 40000),
        ("Srinagar", "Jammu and Kashmir", 2, 1200000, 65, 68, 60, 42000),
        ("Aurangabad", "Maharashtra", 2, 1200000, 70, 72, 68, 48000),
        ("Dhanbad", "Jharkhand", 2, 1200000, 64, 66, 64, 41000),
        ("Amritsar", "Punjab", 2, 1200000, 70, 72, 68, 48000),
        ("Navi Mumbai", "Maharashtra", 2, 1100000, 82, 84, 82, 68000),
        ("Allahabad", "Uttar Pradesh", 2, 1100000, 66, 68, 65, 43000),
        ("Ranchi", "Jharkhand", 2, 1100000, 68, 70, 66, 45000),
        ("Howrah", "West Bengal", 2, 1100000, 68, 70, 68, 46000),
        ("Coimbatore", "Tamil Nadu", 2, 1050000, 76, 78, 74, 56000),
        ("Jabalpur", "Madhya Pradesh", 2, 1000000, 65, 67, 64, 42000),
        
        # Tier 3 Cities (Sample)
        ("Guwahati", "Assam", 3, 1000000, 68, 70, 65, 44000),
        ("Chandigarh", "Chandigarh", 3, 1000000, 80, 82, 78, 62000),
        ("Thiruvananthapuram", "Kerala", 3, 950000, 75, 77, 72, 52000),
        ("Solapur", "Maharashtra", 3, 950000, 65, 67, 63, 40000),
        ("Hubli-Dharwad", "Karnataka", 3, 950000, 70, 72, 68, 46000),
        ("Mysore", "Karnataka", 3, 900000, 73, 75, 70, 50000),
        ("Tiruppur", "Tamil Nadu", 3, 900000, 70, 72, 68, 47000),
        ("Moradabad", "Uttar Pradesh", 3, 900000, 62, 64, 60, 38000),
        ("Warangal", "Telangana", 3, 850000, 68, 70, 65, 43000),
        ("Bareilly", "Uttar Pradesh", 3, 850000, 63, 65, 61, 39000),
    ]
    
    cursor.executemany("""
        INSERT OR REPLACE INTO cities 
        (name, state, tier, population, affluence_score, digital_penetration, business_density, avg_income)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, cities_data)
    
    conn.commit()
    conn.close()
    print(f"✅ Created location database with {len(cities_data)} cities")


def create_industry_database():
    """Create and populate industry enrichment database."""
    db_path = DATA_DIR / "industries.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS industries (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            market_size_cr INTEGER,
            growth_rate REAL,
            digital_maturity INTEGER,
            avg_budget_lakhs INTEGER,
            common_keywords TEXT
        )
    """)
    
    industries_data = [
        ("Technology", 50000, 15.5, 90, 25, "software,IT,tech,digital,cloud,AI,development"),
        ("Retail", 85000, 8.2, 70, 15, "shop,store,retail,ecommerce,shopping,outlet"),
        ("Healthcare", 45000, 12.3, 75, 20, "hospital,clinic,health,medical,doctor,healthcare"),
        ("Education", 30000, 10.5, 68, 12, "school,college,education,training,learning,institute"),
        ("Real Estate", 65000, 9.8, 72, 30, "property,real estate,housing,construction,builder"),
        ("Manufacturing", 120000, 7.5, 65, 35, "factory,manufacturing,production,industrial,plant"),
        ("Food & Beverage", 42000, 11.2, 73, 18, "restaurant,food,cafe,catering,hospitality,dining"),
        ("Professional Services", 28000, 13.5, 85, 22, "consulting,legal,accounting,services,advisory"),
        ("Finance", 55000, 10.8, 88, 28, "banking,finance,insurance,investment,fintech"),
        ("E-commerce", 38000, 25.5, 95, 20, "online,ecommerce,marketplace,shopping,delivery"),
        ("Automotive", 45000, 6.8, 70, 25, "car,automotive,vehicle,automobile,auto"),
        ("Pharma", 40000, 9.5, 72, 22, "pharma,pharmaceutical,medicine,drugs,healthcare"),
        ("Textile", 35000, 5.5, 60, 12, "textile,garment,fashion,clothing,fabric"),
        ("Agriculture", 50000, 6.2, 55, 10, "agriculture,farming,agri,crop,rural"),
        ("Construction", 48000, 8.5, 62, 28, "construction,building,infrastructure,civil,contractor"),
        ("Tourism", 25000, -2.5, 75, 15, "travel,tourism,hotel,hospitality,vacation"),
        ("Logistics", 32000, 12.8, 78, 20, "logistics,transport,shipping,delivery,supply chain"),
        ("Media & Entertainment", 28000, 10.2, 88, 18, "media,entertainment,advertising,marketing,content"),
        ("Telecommunications", 42000, 7.8, 92, 25, "telecom,network,mobile,communication,internet"),
        ("Energy", 55000, 8.5, 68, 35, "energy,power,electricity,solar,renewable"),
    ]
    
    cursor.executemany("""
        INSERT OR REPLACE INTO industries 
        (name, market_size_cr, growth_rate, digital_maturity, avg_budget_lakhs, common_keywords)
        VALUES (?, ?, ?, ?, ?, ?)
    """, industries_data)
    
    conn.commit()
    conn.close()
    print(f"✅ Created industry database with {len(industries_data)} industries")


def create_competitor_database():
    """Create competitor patterns database."""
    db_path = DATA_DIR / "competitors.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS competitors (
            id INTEGER PRIMARY KEY,
            industry TEXT NOT NULL,
            company_name TEXT NOT NULL,
            tier INTEGER,
            market_share REAL
        )
    """)
    
    # Sample competitor data
    competitors_data = [
        ("Technology", "TCS", 1, 8.5),
        ("Technology", "Infosys", 1, 7.2),
        ("Technology", "Wipro", 1, 6.8),
        ("Retail", "Reliance Retail", 1, 12.5),
        ("Retail", "DMart", 1, 8.3),
        ("E-commerce", "Flipkart", 1, 35.0),
        ("E-commerce", "Amazon India", 1, 32.0),
        ("Finance", "HDFC Bank", 1, 15.2),
        ("Finance", "ICICI Bank", 1, 12.8),
        ("Pharma", "Sun Pharma", 1, 9.5),
        ("Automotive", "Maruti Suzuki", 1, 42.0),
        ("Automotive", "Hyundai", 1, 18.5),
    ]
    
    cursor.executemany("""
        INSERT OR REPLACE INTO competitors 
        (industry, company_name, tier, market_share)
        VALUES (?, ?, ?, ?)
    """, competitors_data)
    
    conn.commit()
    conn.close()
    print(f"✅ Created competitor database with {len(competitors_data)} entries")


def create_keywords_database():
    """Create marketing keywords database."""
    db_path = DATA_DIR / "keywords.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS keywords (
            id INTEGER PRIMARY KEY,
            keyword TEXT UNIQUE NOT NULL,
            category TEXT NOT NULL,
            digital_signal INTEGER,
            urgency_signal INTEGER
        )
    """)
    
    keywords_data = [
        # Digital maturity signals
        ("website", "digital", 8, 5),
        ("digital marketing", "digital", 9, 7),
        ("SEO", "digital", 9, 8),
        ("social media", "digital", 8, 6),
        ("ecommerce", "digital", 10, 9),
        ("online", "digital", 7, 6),
        ("app", "digital", 9, 7),
        ("cloud", "digital", 9, 6),
        ("AI", "digital", 10, 7),
        ("analytics", "digital", 8, 6),
        
        # Growth signals
        ("founder", "growth", 7, 8),
        ("startup", "growth", 8, 9),
        ("growing", "growth", 7, 7),
        ("expanding", "growth", 8, 8),
        ("scaling", "growth", 9, 9),
        
        # Budget signals
        ("enterprise", "budget", 10, 5),
        ("SME", "budget", 6, 6),
        ("small business", "budget", 4, 7),
        ("bootstrapped", "budget", 3, 5),
        ("funded", "budget", 9, 7),
        
        # Pain point signals
        ("leads", "pain", 7, 9),
        ("customers", "pain", 7, 8),
        ("visibility", "pain", 8, 9),
        ("reach", "pain", 7, 8),
        ("sales", "pain", 8, 9),
    ]
    
    cursor.executemany("""
        INSERT OR REPLACE INTO keywords 
        (keyword, category, digital_signal, urgency_signal)
        VALUES (?, ?, ?, ?)
    """, keywords_data)
    
    conn.commit()
    conn.close()
    print(f"✅ Created keywords database with {len(keywords_data)} keywords")


if __name__ == "__main__":
    print("🏗️  Building enrichment databases...")
    create_location_database()
    create_industry_database()
    create_competitor_database()
    create_keywords_database()
    print("✅ All enrichment databases created successfully!")
