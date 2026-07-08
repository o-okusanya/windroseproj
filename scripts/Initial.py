import concurrent.futures
import numpy as np
import pandas as pd
import logging
logger = logging.getLogger(__name__)
from datetime import datetime, timedelta, timezone
from cfg.apiconfig import WindAPIConfig

dir_bins   = np.arange(0, 361, 45)
dir_labels = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
spd_bins   = [0, 5, 10, 15, 30]
spd_labels = ["0-5", "5-10", "10-15", "15-30"]

class Initializer(WindAPIConfig):

    def generateChunks(self, sd, ed):
        chunks    = []
        currentsd = sd
        while currentsd <= ed:
            currented = min(currentsd + timedelta(days=13), ed)
            chunks.append({
                "start": currentsd.strftime("%Y-%m-%d"),
                "end":   currented.strftime("%Y-%m-%d"),
            })
            currentsd = currentsd + timedelta(days=14)
        return chunks

    def setupParameters(self, station, sd, ed):
        self.base = "https://mw.buoybay.noaa.gov/api/v1"
        self.key = "f159959c117f473477edbdf3245cc2a4831ac61f"
        self.station = station
        self.sd = sd
        self.ed = ed
        self.rootDir = r"C:\Users\ncbof\hypoxia\windroseproj"
        logger.info(f"Parameters set for station {self.station} ({self.sd} to {self.ed})")
        return self

    def fetchChunk(self, chunk):
        sd = f"{chunk['start']}T00:00:00Z"
        ed = f"{chunk['end']}T23:59:59Z"

        logger.info(f"Fetching chunk {chunk['start']} -> {chunk['end']}")

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            future_speed     = executor.submit(self.fetch_var, "wind_speed",          sd, ed)
            future_gust      = executor.submit(self.fetch_var, "wind_speed_of_gust",  sd, ed)
            future_direction = executor.submit(self.fetch_var, "wind_from_direction",  sd, ed)

            speed     = future_speed.result()
            gust      = future_gust.result()
            direction = future_direction.result()

        if speed.empty or "epoch" not in speed.columns:
            logger.warning(f"Empty response for chunk {chunk['start']} -> {chunk['end']} — skipping")
            return None

        speed     = speed.rename(columns={"value": "wind_speed",    "qa": "wind_speed_qa"})
        gust      = gust.rename(columns={"value": "wind_gust",      "qa": "wind_gust_qa"})
        direction = direction.rename(columns={"value": "wind_dir",   "qa": "wind_dir_qa"})

        df = pd.merge(speed,  gust,      on="epoch", how="outer")
        df = pd.merge(df,     direction, on="epoch", how="outer")
        return df

    def getData(self):
        logger.info(f"Fetching data for station {self.station}")

        sd = datetime.strptime(self.sd, "%Y-%m-%dT%H:%M:%SZ")
        ed = datetime.strptime(self.ed, "%Y-%m-%dT%H:%M:%SZ")

        chunks = self.generateChunks(sd, ed)
        logger.info(f"Split into {len(chunks)} chunks")

        all_frames = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(self.fetchChunk, chunk): chunk for chunk in chunks}
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    if result is not None:
                        all_frames.append(result)
                except Exception as e:
                    logger.error(f"Chunk failed: {e}")

        if not all_frames:
            logger.warning(f"No data returned for {self.station}")
            return pd.DataFrame()

        combined = pd.concat(all_frames, ignore_index=True)
        combined = combined.drop_duplicates(subset=["epoch"])
        combined = combined.sort_values(by="epoch", ascending=True).reset_index(drop=True)

        logger.debug(f"Combined wind shape: {combined.shape}")
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