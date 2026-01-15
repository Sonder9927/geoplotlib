from pathlib import Path

import pandas as pd
from tqdm import tqdm

from geoplotlib.gallery.misfit import plot_misfit
from geoplotlib.gallery.vel2d import plot_diff, plot_phv2d

man_series = [
    [3.35, 3.7],
    [3.45, 3.71],
    [3.45, 3.72],
    [3.53, 3.75],
    [3.59, 3.81],
    [3.65, 3.86],
    [3.68, 3.91],
    [3.75, 3.92],
    [3.8, 4.05],
    [3.85, 4.1],
]


def diff(period, csv1, csv2, region, hull=None, method1="method1"):
    df1 = pd.read_csv(csv1)
    df2 = pd.read_csv(csv2)

    outdir = Path("images")
    outdir.mkdir(exist_ok=True)
    outpath = outdir / f"diff_{method1}_{period}s.png"
    data1 = df1[df1["period"] == period]
    data2 = df2[df2["period"] == period]
    plot_diff(
        period,
        data1[["longitude", "latitude", "phv"]],
        data2[["longitude", "latitude", "phv"]],
        method1,
        region,
        str(outpath),
        hull=hull,
    )


def phvs(phv_csv, region, outflag="tpwt", sta_csv=None, hull=None, auto_series=True):
    df = pd.read_csv(phv_csv)
    outdir = Path(f"images/{outflag}")
    outdir.mkdir(exist_ok=True, parents=True)
    ii = 0
    for period, idf in tqdm(df.groupby("period")):
        outpath = outdir / f"phv_{outflag}_{period}s.png"
        idata = idf[["longitude", "latitude", "phv"]]
        series = None if auto_series else man_series[ii]
        plot_phv2d(
            period,
            idata,
            region,
            str(outpath),
            sta_csv=sta_csv,
            series=series,
            hull=hull,
        )
        ii += 1
        # return


def phvs_3x3(phv_csv, outflag): ...


def misfits(phv_csv, region, outflag="tpwt", hull=None):
    df = pd.read_csv(phv_csv)
    outdir = Path(f"images/{outflag}")
    outdir.mkdir(exist_ok=True)
    for period, idf in tqdm(df.groupby("period")):
        outpath = outdir / f"std_{outflag}_{period}s.png"
        idata = idf[["longitude", "latitude", "std"]]
        plot_misfit(period, idata, region, str(outpath), hull=hull)
        # return


def checkboards(phv_csv, region, dcheck, outflag="tpwt", hull=None):
    df = pd.read_csv(phv_csv)
    outdir = Path(f"images/{outflag}")
    outdir.mkdir(exist_ok=True)
    for period, idf in tqdm(df.groupby("period")):
        outpath = outdir / f"cb{dcheck}_{outflag}_{period}s.png"
        idata = idf[["longitude", "latitude", f"cb{dcheck}"]]
        plot_phv2d(period, idata, region, str(outpath), hull=hull)
        # return
