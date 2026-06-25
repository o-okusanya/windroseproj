import logging
logger = logging.getLogger(__name__)
from cfg.loggingconfig import setup_logging
from scripts.WindRosePlot import WindPlot
from cfg.seasonconfig import lastseason
from cfg.databaseconfig import database

setup_logging()

class PipelineSeasonal(WindPlot):
    def runseason(self, stations):

        season, year, sd, ed = lastseason()

        logger.info(f"[season] {season.title()} {year} -- {sd} -> {ed}")

        results = {}
        for station in stations:
            logger.info(f"Running Seasonal for {station}")
            self.setupParameters(
                station=station,
                sd=sd,
                ed=ed,
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

        display_title = f"Seasonal Wind Roses — {self.sd[:10]} to {self.ed[:10]}"
        out_name = f"wind_rose_{season}_{year}_ALL"

        fig = self.buildGrid(results, fname=display_title)
        self.save(fig, fname=out_name)

if __name__ == "__main__":
    stations = ['AN', 'SR', 'PL', 'UP', 'GR']
    logger.info(f"Running Seasonal for {stations}")
    PipelineSeasonal().runseason(stations)


