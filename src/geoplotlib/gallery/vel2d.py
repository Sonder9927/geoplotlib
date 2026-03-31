from geoplotlib.gmt.hull import hull_clip_grd
import pandas as pd
import pygmt

from geoplotlib.gallery.base_fig import base2d_fig
from geoplotlib.gmt import fig_annotation, fig_stations, data_avg

VCPT = "C-redBlue.cpt"
DCPT = "vs_dif.cpt"


def _diff_prepare(data1, data2, region, hull=None):
    from geoplotlib.gmt import make_topo, makecpt, tomo_grid

    topo = make_topo("ETOPO1", region)
    grds = {
        "grd1": "temp/grd1.grd",
        "grd2": "temp/grd2.grd",
        "diff": "temp/diff.grd",
    }

    # mk z diff grid
    df1 = tomo_grid(data1, region)
    df2 = tomo_grid(data2, region)
    df_diff = pd.merge(df1, df2, on=["x", "y"], how="left")
    df_diff["z"] = (df_diff["z_x"] - df_diff["z_y"]) * 1000
    tomo_grid(df_diff[["x", "y", "z"]], region, grds["diff"])

    # z diff for statics
    zdiff = df_diff["z"]

    # tomo avg grid
    data1_avg = data_avg(data1, hull, col="phv")
    tomo_grid(data1_avg, region, grds["grd1"])
    data2_avg = data_avg(data2, hull, col="phv")
    tomo_grid(data2_avg, region, grds["grd2"])

    if hull:
        # clip tomo grid
        grds["grd1"] = hull_clip_grd(grds["grd1"], hull, region)
        grds["grd2"] = hull_clip_grd(grds["grd2"], hull, region)
        grds["diff"] = hull_clip_grd(grds["diff"], hull, region)
        # clip z diff for statics
        clip_data_diff = pygmt.select(df_diff, polygon=hull)
        zdiff = clip_data_diff["z"]

    vcmap = makecpt(series=[-3, 3, 0.85], cpt=VCPT, output="temp/vcmap.cpt")
    dcmap = makecpt(series=[-150, 150], cpt=DCPT, output="temp/dcmap.cpt")

    return topo, grds, zdiff, vcmap, dcmap


def _diff_plot(period, topo, grds, zdiff, vcmap, dcmap, method1: str, outfile):
    from geoplotlib.gmt import fig_topo, fig_tomos

    region = topo["region"]

    # plot gmt fig
    fig = pygmt.Figure()
    # define figure configuration
    pygmt.config(
        MAP_FRAME_TYPE="plain",
        MAP_TITLE_OFFSET="0.25p",
        MAP_DEGREE_SYMBOL="none",
        FONT_TITLE="18",
    )

    with fig.subplot(
        nrows=2,
        ncols=2,
        figsize=("15c", "14.5c"),
        autolabel=True,
        margins="0.5c/0.3c",
        title=f"{period}s Difference",
    ):
        kws = {"projection": "M?", "frame": ["WSne", "a1f2"]}
        with fig.set_panel(panel=0):
            fig_topo(fig, topo, **kws)
            tomo = {"grid": grds["grd1"], "cmap": vcmap}
            fig_tomos(fig, [tomo], topo["region"], topo["gra"])
            fig.coast(shorelines="0.5p", area_thresh=1000)
            fig.text(
                x=region[1],
                y=region[-1],
                fill="white",
                justify="RT",
                font="15p",
                text=method1.upper(),
                offset="j0.1",
            )
        with fig.set_panel(panel=1):
            fig_topo(fig, topo, **kws)
            tomo = {"grid": grds["grd2"], "cmap": vcmap}
            fig_tomos(fig, [tomo], topo["region"], topo["gra"])
            fig.coast(shorelines="0.5p", area_thresh=1000)

            fig.text(
                x=region[1],
                y=region[-1],
                fill="white",
                justify="RT",
                font="15p",
                text="TPWT",
                offset="j0.1",
            )
            fig.colorbar(cmap=vcmap, position="JMR+o0.5c/0c+w6c/0.4c", frame="xaf")

        # diff
        with fig.set_panel(panel=2):
            fig_topo(fig, topo, **kws)
            tomo = {"grid": grds["diff"], "cmap": dcmap}
            fig_tomos(fig, [tomo], topo["region"], topo["gra"])
            fig.coast(shorelines="0.5p", area_thresh=1000)

        # statistics
        with fig.set_panel(panel=3):
            fig.histogram(
                data=zdiff,
                projection="X?",
                region=[-150, 150, 0, 30],
                series=[-150, 150, 20],
                cmap=dcmap,
                histtype=1,
                pen="1p,black",
            )
            fig.text(
                x=150,
                y=30,
                justify="RT",
                font="12.5p",
                text=f"mean={round(zdiff.mean(), 2)}m/s",
                offset="j0.1",
            )
            fig.text(
                x=150,
                y=28,
                justify="RT",
                font="12p",
                text=f"std = {round(zdiff.std(ddof=0), 2)}m/s",
                offset="j0.1",
            )
            fig.colorbar(
                cmap=dcmap, position="JMR+o0.5c/0c+w6c/0.4c", frame=["xa50f50"]
            )

    fig.savefig(outfile)


def plot_diff(period, data1, data2, method1, region, outfile, hull=None):
    # prepare
    topo, grds, zdiff, vcmap, dcmap = _diff_prepare(data1, data2, region, hull=hull)

    _diff_plot(period, topo, grds, zdiff, vcmap, dcmap, method1, outfile)


def plot_phv2d(period, data, region, outfile, *, series=None, sta_csv=None, hull=None):
    fig = base2d_fig(
        data, region, cptinfo={"cpt": VCPT, "series": series, "dseries": 7}, hull=hull
    )
    # tects
    # station
    if sta_csv:
        fig_stations(fig, sta_csv)
    # volcation
    # period annotation
    fig_annotation(fig, x=region[0], y=region[-1], text=f"{period}s")
    fig.savefig(outfile)
