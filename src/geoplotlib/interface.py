import pandas as pd
from pathlib import Path

from geoplotlib.gallery.interface import plot_interface


def interface(mml_file, flag, region, outdir="images", hull=None):
    df = pd.read_csv(mml_file)[["x", "y", flag]]
    df[flag] = -abs(df[flag])
    outdir = Path(outdir)
    outdir.mkdir(exist_ok=True, parents=True)
    outfile = outdir / f"{flag}.png"
    plot_interface(df, region, outfile, hull)
