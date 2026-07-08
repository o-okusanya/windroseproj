import logging
logger = logging.getLogger(__name__)
from datetime import datetime, timedelta, timezone
from scripts.WindRosePlot import WindPlot
from cfg.databaseconfig import database
from cfg.loggingconfig import setup_logging

setup_logging()

class Pipeline24HR(WindPlot):
    def run24hr(self, stations):
        now = datetime.now(timezone.utc)
        sd  = (now - timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%SZ")
        ed  = now.strftime("%Y-%m-%dT%H:%M:%SZ")

        results = {}
        for station in stations:
            logger.info(f"[24hr] {sd} -> {ed} for {station}")
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

        display_title = f"24HR Wind Roses — {sd[:10]} to {ed[:10]}"
        out_name      = f"wind_rose_24hr_{sd[:10]}_to_{ed[:10]}"

        fig = self.buildGrid(results, fname=display_title)
        self.save(fig, fname=out_name)

if __name__ == "__main__":
    stations = ['AN', 'SR', 'PL', 'UP', 'GR']
    logger.info(f"Running 24HR for {stations}")
    Pipeline24HR().run24hr(stations)