from typing import List

import pandas as pd
import xarray as xr
from scipy.spatial import ConvexHull


def mk_hull(sta_csv: str, region: List, outfile: str):
    df = pd.read_csv(sta_csv)
    lon_min, lon_max, lat_min, lat_max = region
    mask = (
        (df["longitude"] >= lon_min)
        & (df["longitude"] <= lon_max)
        & (df["latitude"] >= lat_min)
        & (df["latitude"] <= lat_max)
    )
    df_flt = df[mask]
    if len(df_flt) < 3:
        raise ValueError("Stations in the region less than 3.")

    points = df_flt[["longitude", "latitude"]].values
    hull = ConvexHull(points)
    hull_points = points[hull.vertices]
    df_hull = pd.DataFrame(hull_points, columns=["x", "y"])
    ds = xr.Dataset(
        {"x_values": ("points", df_hull["x"]), "y_values": ("points", df_hull["y"])},
        coords={
            "x_coords": ("points", df_hull["x"]),
            "y_coords": ("points", df_hull["y"]),
        },
    )
    ds.to_netcdf(outfile)
