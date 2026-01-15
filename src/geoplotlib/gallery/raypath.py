import pygmt

from geoplotlib.gmt import fig_annotation


def plot_rays(period, eqdf, region, outfile):
    fig = pygmt.Figure()
    # define figure configuration
    pygmt.config(
        MAP_FRAME_TYPE="plain",
        MAP_TITLE_OFFSET="0.25p",
        MAP_DEGREE_SYMBOL="none",
        FONT_TITLE="18",
    )

    fig.basemap(region=region, projection="M15c", frame=True)
    fig.coast(land="lightgray", water="lightblue")

    # plot lines
    for _, row in eqdf.iterrows():
        # raise
        fig.plot(
            x=[row["sta_lon"], row["evt_lon"]],
            y=[row["sta_lat"], row["evt_lat"]],
            pen="0.1p,black",
            transparency=30,
        )

    fig.coast(shorelines="1/0.5p,red")
    # fig stations
    fig.plot(
        x=eqdf["sta_lon"],
        y=eqdf["sta_lat"],
        style="t0.2c",
        fill="seagreen",
        pen="0.3p,black",
    )
    fig_annotation(fig, x=region[0], y=region[-1], text=f"{period}s")

    fig.savefig(outfile)
