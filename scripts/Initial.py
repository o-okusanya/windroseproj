import numpy as np
import pandas as pd
import logging
logger = logging.getLogger(__name__)
from cfg.apiconfig import WindAPIConfig

dir_bins = np.arange(0, 361, 45)
dir_labels = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
spd_bins = [0, 5, 10, 15, 30]
spd_labels = ["0-5", "5-10", "10-15", "15-30"]

class Initializer(WindAPIConfig):
    def setupParameters(self, station, sd, ed):
        self.base = "https://mw.buoybay.noaa.gov/api/v1"
        self.key = "f159959c117f473477edbdf3245cc2a4831ac61f"
        self.station = station
        self.sd = sd
        self.ed = ed
        logger.info(f"Parameters set for station {self.station} ({self.sd} to {self.ed})")
        return self

    def getData(self):
        logger.info(f"Fetching data for station {self.station}")
        speed = self.fetch_var("wind_speed")
        direction = self.fetch_var("wind_from_direction")

        speed = speed.rename(columns={"value": "wind_speed"})
        direction = direction.rename(columns={"value": "wind_dir"})

        logger.debug(f"Speed shape: {speed.shape}, Direction shape: {direction.shape}")

        wind = (speed.merge(direction, on="time")
        )[["time", "wind_speed", "wind_dir"]]
        logger.debug(f"Merged wind shape: {wind.shape}")
        return wind

    def Bins(self, wind):
        wind["dir_bin"] = pd.cut(
            wind["wind_dir"],
            bins=dir_bins,
            labels=dir_labels,
            include_lowest=True
        )

        wind["spd_bin"] = pd.cut(
            wind["wind_speed"],
            bins=spd_bins,
            labels=spd_labels,
            include_lowest=True
        )

        grouped = (
            wind.groupby(["dir_bin", "spd_bin"], observed=True)
            .size()
            .reset_index(name="count")
        )
        logger.debug(f"Grouped shape: {grouped.shape}")
        return grouped



