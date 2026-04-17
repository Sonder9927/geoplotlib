from pathlib import Path

from geoplotlib.gallery.base_fig import base2d_fig
from geoplotlib.gmt import data_avg

VCPT = "C-redBlue.cpt"


def plot_interface(data, region, outpath: Path, hull=None, ave=False):
    cptinfo = {"cpt": "jet", "dseries": 7}
    if ave:
        cptinfo["series"] = [-5, 5, 1]
        data = data_avg(data, hull, col="phv")
        outpath = outpath.with_suffix(".ave.png")
    fig = base2d_fig(data, region, cptinfo=cptinfo, hull=hull)
    # tects
    # volcation
    # period annotation
    fig.savefig(str(outpath))
