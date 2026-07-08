import logging
import os
logger = logging.getLogger(__name__)

import plotly.express as px
from scripts.Initial import Initializer, spd_labels, dir_labels

class WindPlotIndividual(Initializer):
    def buildFig(self, results, sd=None, ed=None):
        logger.info(f"Starting plot for station {self.station}")

        title_sd = sd if sd else self.sd
        title_ed = ed if ed else self.ed

        fig = px.bar_polar(
            results,
            r="count",
            theta="dir_bin",
            color="spd_bin",
            category_orders={
                "dir_bin": dir_labels,
                "spd_bin": spd_labels
            },
            color_discrete_sequence=["#AED6F1", "#2E86C1", "#1A5276", "#E67E22", "#C0392B"],
            title=f"Wind Rose — CBIBS Station {self.station}<br>"
                  f"<sup>{title_sd[:10]} to {title_ed[:10]}</sup>",
            labels={"spd_bin": "Speed (m/s)", "dir_bin": "Direction", "count": "Count"},
            template="plotly_white"
        )

        fig.update_layout(
            polar=dict(
                angularaxis=dict(direction="clockwise", rotation=90),
                domain=dict(x=[0.0, 0.55], y=[0.1, 0.9])
            ),
            legend=dict(
                x=0.58,
                y=0.9,
                xanchor="left",
                yanchor="top"
            ),
            legend_title_text="Wind Speed (m/s)",
            title_font_size=16,
            width=1100,
            height=700,
            annotations=[
                dict(
                    x=0.58,
                    y=0.45,
                    xref="paper",
                    yref="paper",
                    xanchor="left",
                    yanchor="middle",
                    align="left",
                    showarrow=False,
                    text=(
                        "<b>How to Read the Wind Rose</b><br><br>"
                        "<b>Direction:</b> Each spoke points in the<br>"
                        "direction the wind is coming FROM.<br>"
                        "North (top) means wind blowing southward.<br><br>"
                        "<b>Length:</b> The longer the spoke, the more<br>"
                        "frequently wind came from that direction.<br><br>"
                        "<b>Color:</b> Each color band represents a wind<br>"
                        "speed range (m/s). Lighter blue = calm winds,<br>"
                        "dark navy = strong winds, orange/red = highest."
                    ),
                    font=dict(size=11),
                )
            ]
        )
        return fig

    def save(self, fig, fname):
        output_dir = r"C:\Users\ncbof\hypoxia\windroseproj\dataOutput"
        os.makedirs(output_dir, exist_ok=True)
        fig.write_html(os.path.join(output_dir,  f"{fname}.html"))
        fig.write_image(os.path.join(output_dir, f"{fname}.png"), scale=2)
        fig.write_image(os.path.join(output_dir, f"{fname}.svg"), scale=2)
        fig.show()

    def plot(self, results, fname, sd=None, ed=None):
        fig = self.buildFig(results, sd=sd, ed=ed)
        self.save(fig, fname)
        return fig