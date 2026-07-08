import logging
logger = logging.getLogger(__name__)
from scripts.IndividualWindRosePlot import WindPlotIndividual
from cfg.seasonconfig import lastseason
from cfg.databaseconfig import database
from cfg.loggingconfig import setup_logging

setup_logging()

class PipelineSeasonalIndividual(WindPlotIndividual):
    def runseason(self, stations):
        season, year, sd, ed = lastseason()

        for station in stations:
            logger.info(f"[season] {season.title()} {year} -- {sd} -> {ed}")
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
                    fname=f"wind_rose_{season}_{year}_{station}",
                    sd=sd,
                    ed=ed
                )
            except Exception as e:
                logger.error(f"Skipping {station}: {e}")

if __name__ == "__main__":
    stations = ['AN', 'SR', 'PL', 'UP', 'GR']
    logger.info(f"Running Seasonal for {stations}")
    PipelineSeasonalIndividual().runseason(stations)