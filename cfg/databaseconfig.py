import sys
sys.path.append(r"C:\Users\ncbof\hypoxia\cbibsbaseproj\cbibsbase")

import logging
import os
logger = logging.getLogger(__name__)

from src.slDb.DBWindMgr import DBWindMgr

DB_DIR = r"C:\Users\ncbof\hypoxia\windroseproj\dataOutput\db"

def database(self, df):
    """Save wind dataframe to SQLite via DBWindMgr from cbibsbaseproj."""
    os.makedirs(DB_DIR, exist_ok=True)

    mgr  = DBWindMgr(self.station)
    conn = mgr.getSqlLiteConnection(DB_DIR)

    begin = int(df["epoch"].min())
    end   = int(df["epoch"].max())

    # Delete existing rows in this range to avoid duplicates
    cur = conn.cursor()
    cur.execute("BEGIN TRANSACTION")
    cur.execute(
        "DELETE FROM wind WHERE obs_time BETWEEN ? AND ?",
        (begin, end)
    )
    cur.execute("COMMIT")

    # Insert new rows
    cur.execute("BEGIN TRANSACTION")
    for _, row in df.iterrows():
        cur.execute(
            "INSERT OR IGNORE INTO wind "
            "(obs_time, ws, ws_unit, wd, wd_unit, u, v, wind_qc) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (
                int(row["epoch"]),
                row.get("wind_speed"),
                "m/s",
                row.get("wind_dir"),
                "degrees",
                None,   # u vector — not computed
                None,   # v vector — not computed
                row.get("wind_speed_qa")
            )
        )
    conn.commit()
    conn.close()
    logger.info(f"Saved {len(df)} wind rows for {self.station} to {DB_DIR}")