import logging
import os
from matplotlib import pyplot as plt

logger = logging.getLogger(__name__)

import plotly.express as px
from scripts.Initial import Initializer, spd_labels, dir_labels
from plotly.subplots import make_subplots

SPEED_COLORS = dict(zip(spd_labels, ["#AED6F1", "#2E86C1", "#1A5276", "#E67E22", "#C0392B"]))
STATION_NAMES = {
    "AN": "Annapolis",
    "SR": "Susquehanna River",
    "PL": "Patapsco",
    "BH": "Baltimore Harbor",
    "GR": "Gooses Reef",
    "YS": "York Spit"
}

class WindPlot(Initializer):
    def buildGrid(self, results, fname, rows=3, cols=2):
        stations = list(results.keys())
        titles = [STATION_NAMES.get(st, st) for st in stations]

        fig = make_subplots(
            rows=rows, cols=cols,
            specs=[[{"type": "polar"}] * cols for _ in range(rows)],
            subplot_titles=titles,
            horizontal_spacing=0.08,
            vertical_spacing=0.10,
        )

        seen = set()  # track which legend entries we've already shown
        for i, st in enumerate(stations):
            r, c = i // cols + 1, i % cols + 1
            sub = px.bar_polar(
                results[st],
                r="count",
                theta="dir_bin",
                color="spd_bin",
                category_orders={
                    "dir_bin": dir_labels,
                    "spd_bin": spd_labels},
                color_discrete_map=SPEED_COLORS,
            )
            for tr in sub.data:
                tr.showlegend = tr.name not in seen
                seen.add(tr.name)
                tr.legendgroup = tr.name  # keeps toggling synced across all cells
                fig.add_trace(tr, row=r, col=c)

        # applies to every polar subplot at once
        fig.update_polars(angularaxis=dict(direction="clockwise", rotation=90))

        # hide leftover empty cells (5 stations in a 3x2 = one blank)
        for j in range(len(stations) + 1, rows * cols + 1):
            key = "polar" if j == 1 else f"polar{j}"
            fig.update_layout({key: dict(radialaxis=dict(visible=False),
                                         angularaxis=dict(visible=False))})

        fig.update_layout(
            title = dict(
                text=fname,
                x = 0.5,
                xanchor="center",
                y= 0.98,
                yanchor="top",
            ),
            margin = dict(t=120),
            legend_title_text = "Wind Speed (m/s)",
            template = "plotly_white",
            width = 900, height = 1200,
        )

        for ann in fig.layout.annotations:
            ann.update(y=ann.y + 0.03, yanchor="bottom", font=dict(size=14))
        return fig

    def save(self, fig, fname):
        output_dir = r"C:\Users\ncbof\hypoxia\windroseproj\dataOutput"
        os.makedirs(output_dir, exist_ok=True)
        fig.write_html(os.path.join(output_dir, f"{fname}.html"))
        fig.write_image(os.path.join(output_dir, f"{fname}.png"), scale=2)
        fig.write_image(os.path.join(output_dir, f"{fname}.svg"), scale=2)
        fig.show()