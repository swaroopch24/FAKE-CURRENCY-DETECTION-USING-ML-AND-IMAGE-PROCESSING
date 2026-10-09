import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/fake_currency")

# Extract connection components
# Format: postgresql://user:password@host:port/dbname
try:
    from urllib.parse import urlparse
    result = urlparse(db_url)
    target_db = result.path.lstrip("/") or "fake_currency"

    print(f"Connecting to PostgreSQL to verify database '{target_db}'...")
    
    # Connect to default 'postgres' database via DSN
    postgres_dsn = db_url.rsplit('/', 1)[0] + '/postgres'
    conn = psycopg2.connect(postgres_dsn)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    # Check if target db exists
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (target_db,))
    exists = cursor.fetchone()
    
    if not exists:
        print(f"Database '{target_db}' does not exist. Creating it now...")
        cursor.execute(f'CREATE DATABASE "{target_db}"')
        print(f"Database '{target_db}' created successfully!")
    else:
        print(f"Database '{target_db}' already exists!")
        
    cursor.close()
    conn.close()
    print("PostgreSQL database setup complete.")
except Exception as e:
    print(f"Error during database setup: {e}")
