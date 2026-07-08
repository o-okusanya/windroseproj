import logging
logger = logging.getLogger(__name__)
from datetime import datetime, timezone
from scripts.WindRosePlot import WindPlot
from cfg.databaseconfig import database
from cfg.loggingconfig import setup_logging

setup_logging()

class PipelineMonth(WindPlot):
    def runmonth(self, stations):
        now  = datetime.now(timezone.utc)
        month = now.month
        strmonth = datetime.now().strftime("%B")
        year = now.year
        sd   = datetime(year, month, 1, tzinfo=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        ed   = now.strftime("%Y-%m-%dT%H:%M:%SZ")

        logger.info(f"[year] {sd} -> {ed}")

        results = {}
        for station in stations:
            logger.info(f"Running Month {strmonth} for {station}")
            self.setupParameters(station=station, sd=sd, ed=ed)
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

        display_title = f"{strmonth} {year} Wind Roses"
        out_name      = f"wind_rose_{strmonth}_{year}"

        fig = self.buildGrid(results, fname=display_title)
        self.save(fig, fname=out_name)

if __name__ == "__main__":
    stations = ['AN', 'SR', 'PL', 'UP', 'GR']
    logger.info(f"Running Yearly for {stations}")
    PipelineMonth().runmonth(stations)