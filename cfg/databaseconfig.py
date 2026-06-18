import os
import sqlite3
import logging
logger = logging.getLogger(__name__)

def database(self, df):
    db_path = r"C:\Users\ncbof\hypoxia\windroseproj\dataOutput\windbuoydata.db"
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)

    cursor = conn.cursor()

    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS wind_data(
                       epoch                INTEGER,
                       wind_speed           REAL,
                       wind_speed_qa        TEXT,
                       wind_gust            REAL,
                       wind_gust_qa         TEXT,
                       wind_direction       REAL,
                       wind_direction_qa    TEXT,
                       station              TEXT,
                       UNIQUE(epoch, station)
                       )
                   """)

    for _, row in df.iterrows():
        cursor.execute("""
                       INSERT
                       OR IGNORE INTO wind_data
                VALUES (?,?,?,?,?,?,?,?)
                       """, (
                           row["epoch"],
                           row.get("wind_speed"), row.get("wind_speed_qa"),
                           row.get("wind_gust"), row.get("wind_gust_qa"),
                           row.get("wind_direction"), row.get("wind_direction_qa"),
                           self.station
                       ))

    conn.commit()
    conn.close()

    logger.info(f"Saved {len(df)} rows for station {self.station} to the database.")