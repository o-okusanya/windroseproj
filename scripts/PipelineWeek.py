import logging
logger = logging.getLogger(__name__)
from cfg.loggingconfig import setup_logging
from datetime import datetime, timedelta, timezone
from scripts.WindRosePlot import WindPlot
from cfg.databaseconfig import database

setup_logging()

class PipelineWeek(WindPlot):
    def runweek(self):
        now = datetime.now(timezone.utc)
        self.ed = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        self.sd = (now - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")

        logger.info(f"[24hr] Fetching {self.sd} - {self.ed}")
        wind = self.getData()
        df = database(self, wind)
        grouped = self.Bins(wind)
        fig = self.plot(
            grouped,
            fname=f"wind_rose_24hr_{self.station} (Previous 7 Days)"
        )
        return fig

if __name__ == "__main__":
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
        logger.info(f"Running Week for {station}")
        pipeline = PipelineWeek()
        pipeline.setupParameters(
            station=station,
            sd=None,
            ed=None
        )
        try:
            pipeline.runweek()
        except Exception as e:
            logger.error(f"Skipping {station}: {e}")