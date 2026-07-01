import numpy as np
import pandas as pd
import logging
from datetime import datetime, timedelta
logger = logging.getLogger(__name__)
from cfg.apiconfig import WindAPIConfig

dir_bins = np.arange(0, 361, 45)
dir_labels = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
spd_bins = [0, 5, 10, 15, 30]
spd_labels = ["0-5", "5-10", "10-15", "15-30"]

class Initializer(WindAPIConfig):
    def generateChunks(self, sd, ed):
        sd = sd
        ed = ed
        chunks = []
        currentsd = sd
        while currentsd <= ed:
            currented = currentsd + timedelta(days=20)
            if currented > ed:
                currented = ed
            chunks.append({
                "start": currentsd.strftime("%Y-%m-%d"),
                "end": currented.strftime("%Y-%m-%d"),
            })
            currentsd = currentsd + timedelta(days=21)
        return chunks

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

        sd = datetime.strptime(self.sd, "%Y-%m-%dT%H:%M:%SZ")
        ed = datetime.strptime(self.ed, "%Y-%m-%dT%H:%M:%SZ")

        chunks = self.generateChunks(sd, ed)
        logger.info(f"Split into {len(chunks)} chunks")

        all_frames = []
        for chunk in chunks:
            logger.info(f"Fetching data for chunk {chunk}")
            self.sd = f"{chunk['start']}T00:00:00Z"
            self.ed = f"{chunk['end']}T00:00:00Z"

            speed = self.fetch_var("wind_speed")
            gust = self.fetch_var("wind_speed_of_gust")
            direction = self.fetch_var("wind_from_direction")

            speed = speed.rename(columns={"value": "wind_speed", "qa": "wind_speed_qa"})
            direction = direction.rename(columns={"value": "wind_dir", "qa": "wind_dir_qa"})
            gust = gust.rename(columns={"value": "wind_gust", "qa": "wind_gust_qa"})

            speed = speed.drop_duplicates(subset="epoch")
            gust = gust.drop_duplicates(subset="epoch")
            direction = direction.drop_duplicates(subset="epoch")

            logger.debug(f"Speed shape: {speed.shape}, Gust shape:{gust.shape} Direction shape: {direction.shape}")

            df = pd.merge(speed, gust, on="epoch", how="outer")
            df = pd.merge(df, direction, on="epoch", how="outer")
            all_frames.append(df)

        self.sd = sd.strftime("%Y-%m-%dT%H:%M:%SZ")
        self.ed = ed.strftime("%Y-%m-%dT%H:%M:%SZ")

        combined = pd.concat(all_frames, ignore_index=True)
        combined = combined.drop_duplicates(subset="epoch", keep="last")
        combined = combined.sort_values(by="epoch", ascending=True).reset_index(drop=True)
        logger.debug(f"Combined wind shape: {df.shape}")

        return combined

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



