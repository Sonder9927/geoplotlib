from pathlib import Path
from typing import List

import pygmt

from geoplotlib.gmt import fig_stations


def station_location(region: List, sta_csv: str, outfile: str):
    grid = pygmt.datasets.load_earth_relief(resolution="15s", region=region)

    fig = pygmt.Figure()
    fig.basemap(projection="M12c", region=region, frame=["a1f"])
    fig.grdimage(grid=grid, cmap="geo", frame="g0.5")

    fig_stations(fig, sta_csv, colorful=True)

    Path(outfile).parent.mkdir(exist_ok=True)
    fig.savefig(outfile)
