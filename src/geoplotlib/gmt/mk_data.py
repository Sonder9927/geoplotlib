import pygmt
import pandas as pd
from pathlib import Path

_cpt_path = Path("data/cpts")


def makecpt(series, cpt=None, output="temp/temp.cpt", reverse=False) -> str:
    cpt = cpt or "Vc_1.8s.cpt"
    tcpt = _cpt_path / cpt
    cmap = str(tcpt) if tcpt.exists() else cpt

    pygmt.makecpt(
        cmap=cmap,
        series=series,
        output=output,
        continuous=True,
        background=True,
        reverse=reverse,
    )

    return output


def make_topo(
    idt,
    region,
    *,
    data="data/tects/ETOPO1.grd",
    normalize="t",
    resolution=None,
    cmap="grayC",
    series=None,
):
    series = series or [-500, 1500]
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)

    ctopo = str(temp_dir / f"topo_{cmap}.cpt")
    grd = temp_dir / f"topo_{idt}.grd"
    gra = temp_dir / f"topo_{idt}.gradient"
    topos = dict(
        zip(
            ["grid", "gra", "cmap", "region"],
            [grd, gra, makecpt(series, cpt=cmap, output=ctopo), region],
        )
    )

    if not gra.exists():
        _mk_topo_grd(data, resolution, normalize, topos)
    return topos


def _mk_topo_grd(data, resolution, normalize, topos):
    TOPO_CUT = "temp/topo_cut.grd"
    TOPO_SAMPLE = "temp/topo_sample.grd"
    TOPO_GRA = "temp/topo.gradient"
    if resolution:
        data = pygmt.datasets.load_earth_relief(
            resolution=resolution, region=topos["region"], registration="gridline"
        )
    # grdcut
    pygmt.grdcut(grid=data, region=topos["region"], outgrid=TOPO_CUT)
    # grdsample
    pygmt.grdsample(
        grid=TOPO_CUT,
        outgrid=TOPO_SAMPLE,
        region=topos["region"],
        spacing=0.01,
        # translate=True,
    )
    # grdgradient
    pygmt.grdgradient(
        grid=TOPO_SAMPLE, outgrid=TOPO_GRA, azimuth=45, normalize=normalize, verbose="w"
    )
    Path(TOPO_SAMPLE).rename(topos["grd"])
    Path(TOPO_GRA).rename(topos["gra"])


##############################################################################


def tomo_grid(data, region, outfile=None, **spacings):
    if spacings is None:
        spacings = {}
    # blockmean
    xyz = pygmt.blockmean(
        data=data, region=region, spacing=spacings.get("blockmean") or 0.5
    )
    # surface
    grd = pygmt.surface(data=xyz, region=region, spacing=spacings.get("surface") or 0.5)

    # grdsample
    if outfile:
        pygmt.grdsample(
            grid=grd, spacing=spacings.get("grdsample") or 0.01, outgrid=outfile
        )

    return pygmt.grd2xyz(grd)


def auto_series(df, df_csv=None, *, method=0, hull=None, dseries=None):
    if df_csv:
        df = pd.read_csv(df_csv)
    df.columns = ["x", "y", "z"]
    if hull:
        df = pygmt.select(df, polygon=hull)

    avg_val = df["z"].mean()
    min_val = df["z"].min()
    max_val = df["z"].max()

    dev_min = min([avg_val - min_val, max_val - avg_val])
    dev_max = max([avg_val - min_val, max_val - avg_val])

    res = [
        [min_val, max_val, 0.01],
        [avg_val - dev_min + 0.01, avg_val + dev_min - 0.01, 0.01],
        [avg_val - dev_max - 0.01, avg_val + dev_max + 0.01, 0.01],
    ]
    series = res[method]

    if dseries:
        series[-1] = (series[1] - series[0]) / dseries

    return series


def data_avg(data, hull=None, col="z"):
    avg = data[col].mean()
    if hull:
        clip_data = pygmt.select(data, polygon=hull)
        avg = clip_data[col].mean()
    data[col] = (data[col] - avg) / avg * 100
    return data
