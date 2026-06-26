import logging
logger = logging.getLogger(__name__)
from cfg.loggingconfig import setup_logging
from datetime import datetime, timedelta, timezone
from scripts.WindRosePlot import WindPlot
from cfg.databaseconfig import database

setup_logging()

class PipelineYear(WindPlot):
    def runyear(self, stations):
        now = datetime.now(timezone.utc)
        year = now.year
        sddt = datetime(year, 1, 1, tzinfo=timezone.utc)
        formatedyear = f"{year:04d}"

        self.sd = sddt.strftime("%Y-%m-%dT%H:%M:%SZ")
        self.ed = now.strftime("%Y-%m-%dT%H:%M:%SZ")

        logger.info(f"Fetching Yearly {self.sd} - {self.ed}")

        results = {}
        for station in stations:
            logger.info(f"Running Year {self.sd} -> {self.ed} for {station}")
            self.setupParameters(
                station=station,
                sd=self.sd,
                ed=self.ed,
            )
            try:
                wind = self.getData()
                if wind is None or wind.empty:
                    logger.warning(f"No data for {station}, skipping")
                    continue
                database(self, wind)
                results[station] = self.Bins(wind)
            except Exception as e:
                logger.error(f"Skipping {station}: {e}")
        if not results:
            logger.error("No stations returned data; nothing to plot")
            return

        display_title = f"Yearly Wind Roses — {formatedyear}"
        out_name = f"wind_rose_year{formatedyear}_ALL"

        fig = self.buildGrid(results, fname=display_title)
        self.save(fig, fname=out_name)


if __name__ == "__main__":
    stations = ['AN', 'SR', 'PL', 'UP', 'GR']
    logger.info(f"Running Yearly for {stations}")
    PipelineYear().runyear(stations)