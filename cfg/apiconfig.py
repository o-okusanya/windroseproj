import sys
sys.path.append(r"C:\Users\ncbof\hypoxia\cbibsbaseproj\cbibsbase")

import pandas as pd
import logging
import pytz
from datetime import datetime

from src.api.CbibsApiQuery import CbibsApiQuery

logger = logging.getLogger(__name__)

ROOT_DIR = r"C:\Users\ncbof\hypoxia\cbibsbaseproj\cbibsbase"

class WindAPIConfig:
    def fetch_var(self, var, sd=None, ed=None):
        sd_str = sd or self.sd
        ed_str = ed or self.ed

        # CbibsApiQuery expects timezone-aware datetime objects
        tz    = pytz.timezone('UTC')
        sd_dt = tz.localize(datetime.strptime(sd_str, "%Y-%m-%dT%H:%M:%SZ"))
        ed_dt = tz.localize(datetime.strptime(ed_str, "%Y-%m-%dT%H:%M:%SZ"))

        query       = CbibsApiQuery(ROOT_DIR, self.station, var, sd_dt, ed_dt)
        stationList = query.getApiData()

        rows = []
        for station in stationList:
            for variable in station.variable:
                for m in variable.measurements:
                    dt    = pd.to_datetime(m.time, utc=True)
                    epoch = int(dt.timestamp())
                    rows.append({
                        "epoch": epoch,
                        "value": float(m.value),
                        "qa":    m.QA,
                    })

        logger.debug(f"Fetched {len(rows)} rows for {var}")
        return pd.DataFrame(rows) if rows else pd.DataFrame(columns=["epoch", "value", "qa"])