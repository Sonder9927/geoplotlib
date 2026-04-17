from geoplotlib.gallery.base_fig import base2d_fig
from geoplotlib.gmt import fig_annotation


def plot_misfit(data, region, outfile, hull=None):
    # vs misfit
    series = [0, 81, 1]
    cptinfo = {"cpt": "hot", "series": series, "reverse": True}
    # mk data
    fig = base2d_fig(data, region, cptinfo=cptinfo, hull=hull)

    fig.savefig(outfile)


def plot_stddev(period, data, region, outfile, hull=None):
    series = [0, 81, 1] if period < 100 else [0, 101, 1]
    cptinfo = {"cpt": "hot", "series": series, "reverse": True}
    # mk data
    fig = base2d_fig(data, region, cptinfo=cptinfo, hull=hull)

    # plot fig
    fig_annotation(fig, x=region[0], y=region[-1], text=f"{period}s")
    fig.savefig(outfile)
