from geoplotlib.gallery.base_fig import base2d_fig
from geoplotlib.gmt import fig_annotation


def plot_misfit(period, data, region, outfile, hull=None):
    series = [0, 121, 1] if period < 100 else [0, 141, 1]
    cptinfo = {"cpt": "hot", "series": series, "reverse": True}
    # mk data
    fig = base2d_fig(data, region, cptinfo=cptinfo, hull=hull)

    # plot fig
    fig_annotation(fig, x=region[0], y=region[-1], text=f"{period}s")
    fig.savefig(outfile)
