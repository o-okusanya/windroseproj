import requests
import pandas as pd
import logging
logger = logging.getLogger(__name__)

class WindAPIConfig:

    def fetch_var(self, var):
        url = f"{self.base}/json/query/{self.station}"
        params = {"key": self.key, "sd": self.sd, "ed": self.ed, "var": var}
        logger.debug(f"Fetching {var} for station {self.station} from {self.sd} to {self.ed}") 
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()

        if "stations" not in data:
            logger.warning(f"No stations key for station {self.station}, var {var}: {data}")
            return pd.DataFrame(columns=["time", "value", "qa"])

        rows = []
        for st in data["stations"]:
            for v in st["variable"]:
                for m in v["measurements"]:
                    rows.append({
                        "time": m["time"],
                        "value": float(m["value"]),
                        "qa": m["QA"],
                    })
        df = pd.DataFrame(rows)
        df["time"] = pd.to_datetime(df["time"], format="ISO8601")
        logger.debug(f"Fetched {len(df)} rows for {var}")
        return df