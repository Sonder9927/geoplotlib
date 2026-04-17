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


def base_profile_fig(data, region, *, cpt=None, moho=None, ave=False):
    # cpt="Vc_1.8s.cpt"
    # prepare
    cmap = makecpt(series=[4.2, 4.6, 0.07], cpt=cpt)
    if ave:
        cmap = makecpt(series=[-5, 5, 1], cpt=cpt)

    grd = "temp/temp.grd"
    tomo_grid(data, region, grd, blockmean=[0.5, 1], grdsample=[0.01, 1])
    # tomo_grid(data, region, grd, blockmean=[0.5, 1])

    # plot gmt fig
    fig = pygmt.Figure()
    # define figure configuration
    pygmt.config(
        MAP_FRAME_TYPE="plain",
        MAP_TITLE_OFFSET="0.25p",
        MAP_DEGREE_SYMBOL="none",
        FONT_TITLE="18",
    )

    fig.basemap(region=region, projection="X8i/2i", frame=["WSen", "xa", "ya"])
    fig.grdimage(grid=grd, cmap=cmap, nan_transparent=True)

    if ave:
        fig.colorbar(cmap=cmap, position="JBC+w10c/0.5c+o0c/1c+h", frame="xaf+ldVs (%)")
    if moho is not None:
        moho.columns = ["x", "y"]
        cmap_crust = _fig_crust(fig, grd, region, moho, cpt, ave=ave)
        if not ave:
            fig.colorbar(
                cmap=cmap_crust,
                position="JBC+w10c/0.5c+o-5.5c/1c+h",
                frame="x+lCrust Vs (km/s)",
            )
            fig.colorbar(
                cmap=cmap,
                position="JBC+w10c/0.5c+o5.5c/1c+h",
                frame="x+lMantle Vs (km/s)",
            )
    else:
        if not ave:
            fig.colorbar(cmap=cmap, position="JBC+w3i/0.10i/-0.5i+h", frame="xa")

    return fig


def _fig_crust(fig, grd, region, moho, cpt, ave=False):
    import pandas as pd
    import xarray as xr

    # prepare
    cmap = makecpt(series=[3.2, 4, 0.15], cpt=cpt)
    if ave:
        cmap = makecpt(series=[-5, 5, 1], cpt=cpt)
    regionc = region
    regionc[-2] = float(moho["y"].min())

    hull_df = pd.concat(
        [
            pd.DataFrame([[moho["x"].iloc[0], 0]], columns=["x", "y"]),
            moho[["x", "y"]],
            pd.DataFrame([[moho["x"].iloc[-1], 0]], columns=["x", "y"]),
        ],
        ignore_index=True,
    )
    hull_df.to_csv("hull.csv", index=False)
    ds = xr.Dataset(
        {"x_values": ("points", hull_df["x"]), "y_values": ("points", hull_df["y"])},
        coords={
            "x_coords": ("points", hull_df["x"]),
            "y_coords": ("points", hull_df["y"]),
        },
    )
    hull = "temp/hull.nc"
    ds.to_netcdf(hull)
    grd = hull_clip_grd(grd, hull, regionc, spacing=[0.01, 1])

    # plot crust vs
    fig.grdimage(grid=grd, cmap=cmap, nan_transparent=True)
    fig.plot(data=moho, pen="1.5p,black,-")
    return cmap
