import sqlite3
import os
import pandas as pd
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'predictions.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            tv_spend REAL NOT NULL,
            radio_spend REAL NOT NULL,
            newspaper_spend REAL NOT NULL,
            total_spend REAL NOT NULL,
            predicted_sales REAL NOT NULL,
            confidence_interval TEXT NOT NULL,
            roi_score REAL NOT NULL,
            recommendation TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def save_prediction(tv, radio, newspaper, total_spend, predicted_sales, confidence, roi, recommendation):
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO predictions (timestamp, tv_spend, radio_spend, newspaper_spend, total_spend, predicted_sales, confidence_interval, roi_score, recommendation)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (now, tv, radio, newspaper, total_spend, predicted_sales, confidence, roi, recommendation))
    conn.commit()
    prediction_id = cursor.lastrowid
    conn.close()
    return prediction_id

def get_all_predictions(limit=50):
    init_db()
    conn = get_db_connection()
    df = pd.read_sql_query(f"SELECT * FROM predictions ORDER BY id DESC LIMIT {limit}", conn)
    conn.close()
    return df.to_dict(orient='records')

def clear_prediction_history():
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM predictions")
    conn.commit()
    conn.close()
