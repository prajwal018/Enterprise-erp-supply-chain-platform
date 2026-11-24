import sqlite3
from pathlib import Path
import pandas as pd

DB_PATH = Path(__file__).with_name("erp_demo.db")

def connect():
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = connect()
    cur = con.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS suppliers(
      supplier_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
      contact_email TEXT, lead_time_days INTEGER DEFAULT 7, rating REAL DEFAULT 3.5,
      active INTEGER DEFAULT 1
    );
    CREATE TABLE IF NOT EXISTS products(
      sku TEXT PRIMARY KEY, name TEXT NOT NULL, category TEXT, uom TEXT DEFAULT 'pcs',
      on_hand REAL DEFAULT 0, reorder_level REAL DEFAULT 0, unit_cost REAL DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS purchase_orders(
      po_id INTEGER PRIMARY KEY AUTOINCREMENT, supplier_id INTEGER, sku TEXT,
      quantity REAL NOT NULL, unit_price REAL NOT NULL, status TEXT DEFAULT 'Open',
      created_at TEXT DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY(supplier_id) REFERENCES suppliers(supplier_id),
      FOREIGN KEY(sku) REFERENCES products(sku)
    );
    CREATE TABLE IF NOT EXISTS sales_orders(
      so_id INTEGER PRIMARY KEY AUTOINCREMENT, customer TEXT NOT NULL, sku TEXT,
      quantity REAL NOT NULL, due_date TEXT, status TEXT DEFAULT 'Open',
      created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS bom(
      parent_sku TEXT, component_sku TEXT, qty_per REAL NOT NULL,
      PRIMARY KEY(parent_sku, component_sku)
    );
    CREATE TABLE IF NOT EXISTS goods_receipts(
      grn_id INTEGER PRIMARY KEY AUTOINCREMENT, po_id INTEGER, sku TEXT,
      quantity REAL, received_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS migration_log(
      log_id INTEGER PRIMARY KEY AUTOINCREMENT, file_name TEXT, rows_total INTEGER,
      rows_valid INTEGER, rows_rejected INTEGER, details TEXT,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)
    con.commit()
    # Seed only when empty
    if cur.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0:
        suppliers = [
          ("Apex Chemicals","orders@apex.example",8,4.4,1),
          ("Precision Packaging","sales@precision.example",5,4.1,1),
          ("Metro Components","supply@metro.example",12,3.8,1),
          ("Global Industrial","contact@global.example",10,4.0,1)
        ]
        cur.executemany("INSERT INTO suppliers(name,contact_email,lead_time_days,rating,active) VALUES(?,?,?,?,?)", suppliers)
        products = [
          ("RM-001","Active Ingredient A","Raw Material","kg",420,150,85.0),
          ("RM-002","Solvent B","Raw Material","L",180,100,42.0),
          ("PK-001","Packaging Bottle","Packaging","pcs",2400,800,3.5),
          ("PK-002","Printed Label","Packaging","pcs",1600,700,1.2),
          ("FG-001","Finished Product Alpha","Finished Good","bottle",300,250,145.0),
          ("FG-002","Finished Product Beta","Finished Good","bottle",180,200,118.0),
          ("RM-003","Excipient C","Raw Material","kg",90,120,28.0)
        ]
        cur.executemany("INSERT INTO products VALUES(?,?,?,?,?,?,?)", products)
        cur.executemany("INSERT INTO bom VALUES(?,?,?)", [
          ("FG-001","RM-001",0.08),("FG-001","RM-002",0.12),
          ("FG-001","PK-001",1),("FG-001","PK-002",1),
          ("FG-002","RM-001",0.05),("FG-002","RM-003",0.10),
          ("FG-002","PK-001",1),("FG-002","PK-002",1)
        ])
        cur.executemany("INSERT INTO purchase_orders(supplier_id,sku,quantity,unit_price,status) VALUES(?,?,?,?,?)", [
          (1,"RM-001",200,82,"Open"),(2,"PK-001",1000,3.4,"Open"),(3,"RM-003",150,27,"Received")
        ])
        cur.executemany("INSERT INTO sales_orders(customer,sku,quantity,due_date,status) VALUES(?,?,?,?,?)", [
          ("Northstar Distributors","FG-001",120,"2026-12-05","Open"),
          ("Healthway Stores","FG-002",90,"2026-12-08","Open"),
          ("CityCare Wholesale","FG-001",75,"2026-12-12","In Production")
        ])
        con.commit()
    con.close()

def query_df(sql, params=()):
    con = connect()
    df = pd.read_sql_query(sql, con, params=params)
    con.close()
    return df

def execute(sql, params=()):
    con = connect()
    cur = con.cursor()
    cur.execute(sql, params)
    con.commit()
    last = cur.lastrowid
    con.close()
    return last
