import sqlite3

DB_PATH = "ecommerce.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Drop previous version so the new schema with order_date is created cleanly
    cursor.execute("DROP TABLE IF EXISTS orders")
    cursor.execute("""
        CREATE TABLE orders (
            id TEXT PRIMARY KEY,
            customer_name TEXT,
            status TEXT,
            carrier TEXT,
            tracking_number TEXT,
            order_date TEXT,
            delivered_date TEXT,
            total REAL,
            payment_status TEXT
        )
    """)
    
    sample_orders = [
        ("ORD-1022", "Chandana", "In-Transit", "FedEx", "FDX-8829104820", "2026-09-22", "2026-09-26", 200.00, "Paid"),
        ("ORD-1023", "Alex Morgan", "Delivered", "FedEx", "FDX-8829104821", "2026-09-20", "2026-09-26", 178.00, "Paid"),
        ("ORD-1024", "Taylor Swift", "Cancelled", "None", "None", "2026-09-29", None, 349.50, "Refunded/Voided"),
        ("ORD-1025", "David Miller", "Delivered", "UPS", "1Z9999999999999999", "2026-07-01", "2026-07-08", 89.99, "Paid"),
        ("ORD-1026", "Samantha Ray", "In-Transit", "UPS", "1Z8472910382910293", "2026-09-28", None, 215.00, "Paid"),
        ("ORD-1027", "Chris Evans", "Carrier Investigation", "USPS", "9400100000000000000000", "2026-09-15", None, 45.00, "Paid")
    ]
    
    cursor.executemany("""
        INSERT INTO orders 
        (id, customer_name, status, carrier, tracking_number, order_date, delivered_date, total, payment_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, sample_orders)
    
    conn.commit()
    conn.close()
    print("✅ Database refreshed with 5 diverse customer order scenarios!")

def get_order_by_id(order_id: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, customer_name, status, carrier, tracking_number, order_date, delivered_date, total, payment_status FROM orders WHERE id = ?", (order_id.strip(),))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "id": row[0],
            "customer_name": row[1],
            "status": row[2],
            "carrier": row[3],
            "tracking_number": row[4],
            "order_date": row[5],
            "delivered_date": row[6],
            "total": row[7],
            "payment_status": row[8]
        }
    return None

if __name__ == "__main__":
    init_db()