"""
Clear database tables (logs, uploads, predictions)
Keep user table intact
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "app" / "models" / "anomaly_detection.db"

if not DB_PATH.exists():
    print(f"❌ Database not found: {DB_PATH}")
    exit(1)

print(f"🔄 Connecting to database: {DB_PATH}")
conn = sqlite3.connect(DB_PATH)
conn.isolation_level = None
cursor = conn.cursor()

try:
    # Get list of all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print(f"\n📊 Current tables: {len(tables)}")
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"   - {table_name}: {count} rows")
    
    # Tables to clear (everything except 'users')
    tables_to_clear = [
        'csv_uploads',
        'predictions',
        'inference_logs',
        'inference_summary'
    ]
    
    print(f"\n🗑️  Clearing tables...")
    for table in tables_to_clear:
        try:
            cursor.execute(f"DELETE FROM {table}")
            print(f"   ✅ Cleared: {table}")
        except sqlite3.OperationalError:
            print(f"   ⚠️  Table not found: {table}")
    
    print(f"\n📊 After clearing:")
    for table in tables_to_clear:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   - {table}: {count} rows")
        except:
            pass
    
    # Show user table (kept intact)
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    print(f"   - users: {user_count} rows (kept)")
    
    print(f"\n✅ Database cleared successfully!")

except Exception as e:
    print(f"❌ Error: {e}")
finally:
    conn.close()
