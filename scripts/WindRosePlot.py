import os
import logging

log_dir = r"C:\Users\ncbof\hypoxia\windroseproj\logs"
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(r"C:\Users\ncbof\hypoxia\windroseproj\logs\windrose.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

import plotly.express as px
from scripts.Initial import Initializer



class WindPlot(Initializer):
    def plot(self, fname):
        logger.info(f"Starting plot for station {self.station}")
        grouped, speed, direction, dir_bin, spd_bin = self.Bins()
        dir_labels = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
        spd_labels = ["0-5", "5-10", "10-15", "15-30"]

        output_dir = r"C:\Users\ncbof\hypoxia\windroseproj\dataOutput"
        os.makedirs(output_dir, exist_ok=True)

        fig = px.bar_polar(
            grouped,
            r="count",
            theta="dir_bin",
            color="spd_bin",
            category_orders={
                "dir_bin": dir_labels,
                "spd_bin": spd_labels
            },
            color_discrete_sequence=["#AED6F1", "#2E86C1", "#1A5276", "#E67E22", "#C0392B"],
            title=f"Wind Rose — CBIBS Station {self.station}<br>"
                  f"<sup>{self.sd[:10]} to {self.ed[:10]}</sup>",
            labels={"spd_bin": "Speed (m/s)", "dir_bin": "Direction", "count": "Count"},
            template="plotly_white"
        )

        fig.update_layout(
            polar=dict(
                angularaxis=dict(direction="clockwise", rotation=90),
            ),
            legend_title_text="Wind Speed (m/s)",
            title_font_size=16,
            width=700,
            height=700,
        )

        fig.write_html(os.path.join(output_dir, f"{fname}.html"))
        fig.write_image(os.path.join(output_dir, f"{fname}.png"), scale=2)
        fig.show()

if __name__ == "__main__":
    stations = [
        ("AN", "2025-06-01T00:00:00z", "2025-06-08T00:00:00z", "wind_rose_AN"),
        ("SR", "2025-06-01T00:00:00z", "2025-06-08T00:00:00z", "wind_rose_SR"),
        ("PL", "2025-06-01T00:00:00z", "2025-06-08T00:00:00z", "wind_rose_PL"),
    ]

    for station, sd, ed, fname in stations:
        wp = WindPlot()
        wp.setupParameters(station, sd, ed)
        try:
            wp.plot(fname)
        except Exception as e:
            logger.error(f"Skipping {station}: {e}")