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


def event_counts(eqlist_csv, phv_csv, outfile, *, ant_csv=None, iter_csv=None):
    df = pd.read_csv(eqlist_csv)
    event_counts = df.groupby("period")["event"].size()
    vdf = pd.read_csv(phv_csv)
    tpwt_n2 = vdf.groupby("period")["phv"].mean()

    fig = mplt.figure(figsize=(10, 6))
    ax1 = fig.add_subplot(111)
    ax1.bar(event_counts.index, event_counts.values)
    ax1.set_xlabel("period")
    ax1.set_ylabel("event counts")
    for i, v in enumerate(event_counts.values):
        ax1.text(event_counts.index[i], v + 0.1, str(v), ha="center")
    # ax1.tight_layout()

    ax2 = ax1.twinx()
    ax2.plot(tpwt_n2.index, tpwt_n2.values, "r", label="TPWT Phv")

    if iter_csv:
        vdf = pd.read_csv(iter_csv)
        ax2.plot(vdf["period"], vdf["n0"], "b", label="TPWT N0")
        ax2.plot(vdf["period"], vdf["n1"], "g", label="TPWT N1")
    if ant_csv:
        vdf = pd.read_csv(ant_csv)
        ant_mean = vdf.groupby("period")["phv"].mean()
        ax2.plot(ant_mean.index, ant_mean.values, "y", label="ANT Phv")

    ax2.set_ylabel("Velocity")
    ax2.legend(loc="upper right")

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
