import requests
import pandas as pd
import logging
logger = logging.getLogger(__name__)

class WindAPIConfig:
    def fetch_var(self, var, sd=None, ed=None):
        sd = sd or self.sd
        ed = ed or self.ed
        url    = f"{self.base}/json/query/{self.station}"
        params = {"key": self.key, "sd": sd, "ed": ed, "var": var}
        r      = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        data   = r.json()

        if "stations" not in data:
            logger.warning(f"No stations key for {self.station}, var {var}: {data}")
            return pd.DataFrame(columns=["epoch", "value", "qa"])

        rows = []
        for st in data["stations"]:
            for v in st["variable"]:
                for m in v["measurements"]:
                    dt    = pd.to_datetime(m["time"], utc=True)
                    epoch = int(dt.timestamp())
                    rows.append({
                        "epoch": epoch,
                        "value": float(m["value"]),
                        "qa":    m["QA"],
                    })

        logger.debug(f"Fetched {len(rows)} rows for {var}")
        return pd.DataFrame(rows)