from pathlib import Path

import pandas as pd
from tqdm import tqdm
import pygmt

from geoplotlib.gallery.stddev import plot_stddev
from geoplotlib.gallery.vel2d import plot_diff, plot_phv2d
from geoplotlib.gallery.dispersion import plot_dispersion

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
        data1[["longitude", "latitude", "phv"]].astype("float"),
        data2[["longitude", "latitude", "phv"]].astype("float"),
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


def stddevs(phv_csv, region, outflag="tpwt", hull=None):
    df = pd.read_csv(phv_csv)
    outdir = Path(f"images/{outflag}")
    outdir.mkdir(exist_ok=True)
    for period, idf in tqdm(df.groupby("period")):
        outpath = outdir / f"std_{outflag}_{period}s.png"
        idata = idf[["longitude", "latitude", "std"]]
        idata["std"] *= 0.8
        plot_stddev(period, idata, region, str(outpath), hull=hull)
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


def dispersions(tpwt_phv_csv, ant_phv_csv, region, hull=None, interp=True):
    outdir = Path("images/dispersions")
    outdir.mkdir(parents=True, exist_ok=True)

    tpwt_phv = pd.read_csv(tpwt_phv_csv)
    ant_phv = pd.read_csv(ant_phv_csv)
    # ant_phv = _interp(ant_phv, tpwt_points)
    ant_phv = _gmt_surface(ant_phv, region)
    # ant_phv.to_csv("fmst_phv-d5.csv", index=False)
    # raise

    tpwt_points = (
        tpwt_phv[["longitude", "latitude"]].drop_duplicates().reset_index(drop=True)
    )
    tpwt_points.columns = ["x", "y"]
    # clip hull
    if hull:
        tpwt_points = pygmt.select(tpwt_points, region=region, polygon=hull)

    for lon, lat in zip(tpwt_points["x"], tpwt_points["y"]):
        tpwt_point_df = tpwt_phv[
            (tpwt_phv["latitude"] == lat) & (tpwt_phv["longitude"] == lon)
        ]
        ant_point_df = ant_phv[
            (ant_phv["latitude"] == lat) & (ant_phv["longitude"] == lon)
        ]
        file_path = outdir / f"dispersion_{lat:.2f}_{lon:.2f}.png"
        plot_dispersion(lat, lon, tpwt_point_df, ant_point_df, file_path)


def _gmt_surface(df, region):
    data_lst = []
    for per, idf in df.groupby("period"):
        grd = pygmt.surface(
            idf[["longitude", "latitude", "phv"]], region=region, spacing=0.5
        )
        idata = pygmt.grd2xyz(grd, region=region)
        idata["period"] = per
        data_lst.append(idata)
    data_df = pd.concat(data_lst, ignore_index=True)
    data_df.columns = ["longitude", "latitude", "phv", "period"]
    return data_df


def _interp(df, target_points):
    import numpy as np
    from scipy.interpolate import griddata

    periods = df["period"].unique()
    interp_list = []

    for period in periods:
        df_per = df[df["period"] == period]
        df_points = df_per[["longitude", "latitude"]].values
        values = df_per["phv"].values

        xi = target_points[["longitude", "latitude"]].values
        phv_interp = griddata(df_points, values, xi, method="linear", fill_value=np.nan)

        for i, row in target_points.iterrows():
            interp_list.append({
                "latitude": row["latitude"],
                "longitude": row["longitude"],
                "period": period,
                "phv": phv_interp[i],
            })
    dest_df = pd.DataFrame(interp_list).dropna(subset=["phv"])
    return dest_df
