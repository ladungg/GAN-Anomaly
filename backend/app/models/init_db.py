from .database import get_db
import hashlib
import os

def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    salt = os.urandom(32)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return salt.hex() + pwd_hash.hex()

def verify_password(stored_hash: str, password: str) -> bool:
    """Verify password against hash"""
    try:
        salt = bytes.fromhex(stored_hash[:64])
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        return pwd_hash.hex() == stored_hash[64:]
    except:
        return False

def init_db():
    """
    Khởi tạo database với các bảng
    """
    conn = get_db()
    cursor = conn.cursor()

    # ===== USERS =====
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'user',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        last_login DATETIME
    );
    """)

    # ===== MIGRATION: Add last_login column if missing =====
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN last_login DATETIME;")
        conn.commit()
        print("[OK] Added last_login column to users table")
    except:
        pass  # Column already exists

    # ===== DATASETS =====
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS datasets (
        dataset_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        file_path TEXT NOT NULL,
        num_samples INTEGER,
        num_features INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # ===== RUNS =====
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS runs (
        run_id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_type TEXT NOT NULL,
        user_id INTEGER,
        dataset_id INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id),
        FOREIGN KEY (dataset_id) REFERENCES datasets(dataset_id)
    );
    """)

    # ===== METRICS =====
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS metrics (
        metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id INTEGER,
        roc_auc REAL,
        avg_runtime_ms REAL,
        FOREIGN KEY (run_id) REFERENCES runs(run_id)
    );
    """)

    # ===== CONFUSION MATRIX =====
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS confusion_matrix (
        cm_id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id INTEGER,
        tn INTEGER,
        fp INTEGER,
        fn INTEGER,
        tp INTEGER,
        FOREIGN KEY (run_id) REFERENCES runs(run_id)
    );
    """)

    # ===== ARTIFACTS =====
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS artifacts (
        artifact_id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id INTEGER,
        file_type TEXT,
        file_path TEXT,
        FOREIGN KEY (run_id) REFERENCES runs(run_id)
    );
    """)

    # ===== CSV UPLOADS =====
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS csv_uploads (
        upload_id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        file_path TEXT NOT NULL,
        num_rows INTEGER,
        num_features INTEGER,
        upload_status TEXT DEFAULT 'completed',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # ===== INFERENCE PREDICTIONS =====
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS predictions (
        prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
        upload_id INTEGER NOT NULL,
        row_index INTEGER,
        anomaly_score REAL,
        is_anomaly INTEGER,
        prediction REAL,
        confidence REAL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (upload_id) REFERENCES csv_uploads(upload_id)
    );
    """)

    # ===== INFERENCE RESULTS SUMMARY =====
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inference_summary (
        summary_id INTEGER PRIMARY KEY AUTOINCREMENT,
        upload_id INTEGER NOT NULL UNIQUE,
        total_samples INTEGER,
        normal_count INTEGER,
        anomaly_count INTEGER,
        anomaly_percentage REAL,
        inference_time_ms REAL,
        status TEXT DEFAULT 'completed',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (upload_id) REFERENCES csv_uploads(upload_id)
    );
    """)

    # ===== INFERENCE LOGS =====
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inference_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        upload_id INTEGER NOT NULL,
        csv_filename TEXT NOT NULL,
        total_samples INTEGER,
        normal_count INTEGER,
        anomaly_count INTEGER,
        anomaly_percentage REAL,
        threshold REAL,
        inference_time_ms REAL,
        model_status TEXT,
        error_message TEXT,
        user_notes TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (upload_id) REFERENCES csv_uploads(upload_id)
    );
    """)

    conn.commit()

    # ===== INSERT DEFAULT USERS =====
    cursor.execute("SELECT COUNT(*) FROM users;")
    user_count = cursor.fetchone()[0]
    
    if user_count == 0:
        # Insert admin user
        admin_hash = hash_password("admin123")
        cursor.execute("""
        INSERT INTO users (username, email, password_hash, role)
        VALUES (?, ?, ?, ?)
        """, ("admin", "admin@gandetection.local", admin_hash, "admin"))
        
        # Insert regular user
        user_hash = hash_password("user123")
        cursor.execute("""
        INSERT INTO users (username, email, password_hash, role)
        VALUES (?, ?, ?, ?)
        """, ("user", "user@gandetection.local", user_hash, "user"))
        
        conn.commit()
        print("[OK] Default users created:")
        print("   - admin / admin123 (role: admin)")
        print("   - user / user123 (role: user)")
    else:
        print(f"[INFO] Database already has {user_count} users, skipping user creation")

    conn.close()
    print("[OK] SQLite database initialized successfully")

if __name__ == "__main__":
    init_db()

