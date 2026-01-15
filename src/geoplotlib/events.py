from pathlib import Path

import matplotlib.pyplot as mplt
import numpy as np
import pandas as pd
import pygmt
from tqdm import tqdm

from geoplotlib.gallery.raypath import plot_rays
from geoplotlib.gmt import makecpt


def _merge_eqdf(eq_csv, evt_csv, sta_csv):
    df = pd.read_csv(eq_csv, dtype={"event": str})
    evtdf = pd.read_csv(evt_csv, parse_dates=["time"])
    evtdf["event"] = evtdf["time"].dt.strftime("%Y%m%d%H%M")
    stadf = pd.read_csv(sta_csv)

    eqdf = df.merge(evtdf[["event", "longitude", "latitude"]], on="event", how="left")
    eqdf = eqdf.rename(columns={"longitude": "evt_lon", "latitude": "evt_lat"})

    eqdf = eqdf.merge(
        stadf[["station", "longitude", "latitude"]], on="station", how="left"
    )
    eqdf = eqdf.rename(columns={"longitude": "sta_lon", "latitude": "sta_lat"})

    return eqdf


def event_paths(eqlist_csv, evt_csv, sta_csv, region, outflag="tpwt"):
    eqdf = _merge_eqdf(eqlist_csv, evt_csv, sta_csv)
    for period, ieqdf in tqdm(eqdf.groupby("period")):
        outdir = Path(f"images/{outflag}")
        outdir.mkdir(exist_ok=True)
        outpath = outdir / f"path_{outflag}_{period}s.png"
        plot_rays(period, ieqdf, region, str(outpath))
        # return


def event_counts(eqlist_csv, iter_dispersions, outfile):
    df = pd.read_csv(eqlist_csv)
    period_counts = df.groupby("period")["event"].size()

    fig = mplt.figure(figsize=(10, 6))
    ax1 = fig.add_subplot(111)
    ax1.bar(period_counts.index, period_counts.values)
    ax1.set_xlabel("period")
    ax1.set_ylabel("event counts")
    for i, v in enumerate(period_counts.values):
        ax1.text(period_counts.index[i], v + 0.1, str(v), ha="center")
    # ax1.tight_layout()

    fig.savefig(outfile)


def _get_valid_events(evt_csv, eqlist_csv):
    eqdf = pd.read_csv(eqlist_csv, dtype={"event": str})
    valid_evts = eqdf["event"].unique()

    evtdf = pd.read_csv(evt_csv, parse_dates=["time"])
    evtdf["event"] = evtdf["time"].dt.strftime("%Y%m%d%H%M")

    df = evtdf[evtdf["event"].isin(valid_evts)]

    return df


def event_location(region, evt_csv, eqlist_csv, outfile):
    evts = _get_valid_events(evt_csv, eqlist_csv)
    cen = [sum(region[:2]) / 2, sum(region[-2:]) / 2]
    evts["mag"] = evts["mag"] * 0.08
    evts["evt_site"] = evts.apply(lambda r: [r["longitude"], r["latitude"]], axis=1)
    evts["sta_site"] = evts["event"].apply(lambda _: cen)
    # evts["sta_site"] = cen
    lines = evts[["evt_site", "sta_site"]].values.tolist()

    fig = pygmt.Figure()
    pygmt.config(
        FORMAT_GEO_MAP="+D",
    )
    fig.coast(
        projection=f"E{cen[0]}/{cen[1]}/130/8i",
        region="g",
        shorelines="0.25p,black",
        land="yellow",
        water="white",
        area_thresh=10_000,
        frame="a",
    )
    fig.plot("data/tects/PB2002_plates.dig.txt", pen="1.5p,darkred,.")
    cen = np.array(cen)
    for line in lines:
        fig.plot(data=line, pen="thick,black")
    cc = makecpt([0, 200, 0.01], cpt="rainbow.cpt", reverse=True)
    sites = evts[["longitude", "latitude", "depth", "mag"]]
    fig.plot(data=sites, style="c", cmap=cc, pen="white")
    fig.plot(data=[cen], style="t0.6c", fill="red", pen="white")

    for dd in range(60, 300, 60):
        fig.plot(data=[cen], style=f"E{dd}d", pen="0.3p,black")
    for y in [60, 90, 120]:
        fig.text(
            text=y,
            x=cen[0],
            y=cen[1] - y,
            font="15.0p",
            offset="0c/0c",
            fill="white",
        )
    fig.colorbar(
        cmap=cc,
        frame=["xa40f20+lDepth", "y+l(km)"],
        position="jBC+w20c/0.5c+o0c/-2c+m+h",
        shading=True,
    )

    fig.savefig(outfile)
