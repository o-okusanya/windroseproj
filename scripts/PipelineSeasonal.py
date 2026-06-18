import logging
logger = logging.getLogger(__name__)
from cfg.loggingconfig import setup_logging
from scripts.WindRosePlot import WindPlot
from cfg.seasonconfig import lastseason
from cfg.databaseconfig import database

setup_logging()

class PipelineSeasonal(WindPlot):
    def runseason(self):

        season, year, sd, ed = lastseason()

        logger.info(f"[season] {season.title()} {year} -- {self.sd} -> {self.ed}")

        wind = self.getData()
        df = database(self, wind)
        grouped = self.Bins(wind)
        self.plot(
            grouped,
            fname=f"wind_rose_{season}_{year}_{self.station}"
        )

if __name__ == "__main__":
    season, year, sd, ed = lastseason()
    station_codes = {
        "Annapolis":      "AN",
        "Stingray Point": "SR",
        "Potomac":        "PL",
        "Upper Potomac":  "UP",
        "Gooses Reef":    "GR",
    }

    print("Select a station:")
    for name, code in station_codes.items():
        print(f"  {name} ({code})")

    user_input = input("Station code(s): ")
    selected = [s.strip().upper() for s in user_input.split(",")]

    for station in selected:
        if station not in station_codes.values():
            print(f"Station not found: {station}")
            continue
        logger.info(f"Running Seasonal for {station}")
        pipeline = PipelineSeasonal()
        pipeline.setupParameters(
            station=station,
            sd=sd,
            ed=ed,
        )
        try:
            pipeline.runseason()
        except Exception as e:
            logger.error(f"Skipping {station}: {e}")
