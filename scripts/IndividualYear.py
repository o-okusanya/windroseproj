import logging
logger = logging.getLogger(__name__)
from cfg.loggingconfig import setup_logging
from datetime import datetime, timezone
from scripts.IndividualWindRosePlot import WindPlotIndividual
from cfg.databaseconfig import database

setup_logging()

class PipelineYearIndividual(WindPlotIndividual):
    def runyear(self, stations):
        now  = datetime.now(timezone.utc)
        year = now.year
        sd   = datetime(year, 1, 1, tzinfo=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        ed   = now.strftime("%Y-%m-%dT%H:%M:%SZ")

        for station in stations:
            logger.info(f"[year] {sd} -> {ed} for {station}")
            self.setupParameters(station=station, sd=sd, ed=ed)
            try:
                wind = self.getData()
                if wind is None or wind.empty:
                    logger.warning(f"No data for {station}, skipping")
                    continue
                self.sd = sd
                self.ed = ed
                database(self, wind)
                grouped = self.Bins(wind)
                self.plot(
                    grouped,
                    fname=f"wind_rose_{ed[:4]}_{station}",
                    sd=sd,
                    ed=ed
                )
            except Exception as e:
                logger.error(f"Skipping {station}: {e}")

if __name__ == "__main__":
    stations = ['AN', 'SR', 'PL', 'UP', 'GR']
    logger.info(f"Running Yearly for {stations}")
    PipelineYearIndividual().runyear(stations)