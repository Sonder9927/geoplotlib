import pygmt

from geoplotlib.gmt import (
    auto_series,
    fig_tomos,
    fig_topo,
    make_topo,
    makecpt,
    tomo_grid,
    hull_clip_grd,
)


def base2d_fig(data, region, *, cptinfo={}, hull=None):
    # prepare
    topo = make_topo("ETOPO1", region)
    grd = "temp/temp.grd"
    tomo_grid(data, region, grd)
    if hull:
        grd = hull_clip_grd(grd, hull, region)
        # data = pygmt.select(data, polygon=hull)

    series = cptinfo.get("series") or auto_series(
        data, method=0, dseries=cptinfo.get("dseries"), hull=hull
    )
    cmap = makecpt(series=series, cpt=cptinfo["cpt"], reverse=cptinfo.get("reverse"))

    tomo = {"grid": grd, "cmap": cmap}

    # plot gmt fig
    fig = pygmt.Figure()
    # define figure configuration
    pygmt.config(
        MAP_FRAME_TYPE="plain",
        MAP_TITLE_OFFSET="0.25p",
        MAP_DEGREE_SYMBOL="none",
        FONT_TITLE="18",
    )
    fig_topo(fig, topo, frame=["WSne", "a1f2"])
    fig_tomos(fig, [tomo], topo["region"], topo["gra"])

    fig.coast(
        shorelines="0.5p",
        area_thresh=1000,
        # water="lightblue",
    )
    fig.colorbar(cmap=cmap, frame=["a"])
    return fig
