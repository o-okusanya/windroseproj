import logging
logger = logging.getLogger(__name__)
from cfg.loggingconfig import setup_logging
from datetime import datetime, timedelta, timezone
from scripts.IndividualWindRosePlot import WindPlotIndividual
from cfg.databaseconfig import database

setup_logging()

class PipelineIndividualWeek(WindPlotIndividual):
    def runweek(self, stations):
        now = datetime.now(timezone.utc)
        self.ed = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        self.sd = (now - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")

        for station in stations:
            logger.info(f"[24hr] Fetching {self.sd} - {self.ed}")
            self.setupParameters(station=station, sd=self.sd, ed=self.ed)
            try:
                wind = self.getData()
                if wind is None or wind.empty:
                    logger.warning(f"No data for {station}, skipping")
                    continue
                database(self, wind)
                grouped = self.Bins(wind)
                self.plot(grouped, fname=f"wind_rose_24hr_{self.station} (Previous 7 Days)")
            except Exception as e:
                logger.error(f"Skipping {station}: {e}")

if __name__ == "__main__":
    stations = ['AN', 'SR', 'PL', 'UP', 'GR']
    logger.info(f"Running 24Hr for {stations}")
    PipelineIndividualWeek().runweek(stations)