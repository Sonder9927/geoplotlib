from pathlib import Path

from geoplotlib.gallery.base_fig import base2d_fig, base_profile_fig
from geoplotlib.gmt import data_avg


def plot_profile_distribution(data, profiles, region, *, outpath, ave, hull):
    cptinfo = {"cpt": "jet", "dseries": 7}
    if ave:
        cptinfo["series"] = [-5, 5, 1]
        data = data_avg(data, hull, col="phv")
        outpath = outpath.with_suffix(".ave.png")
    fig = base2d_fig(data, region, cptinfo=cptinfo, hull=hull)
    # tects
    # volcation
    # lines
    for profile in profiles:
        line = profile.line
        fig.plot(line, pen="2p,gray")
        fig.text(
            x=line[0][0],
            y=line[0][1],
            text=profile.pid,
            justify="LT",
            offset="0.01j",
            font="9p",
        )

    fig.savefig(str(outpath))


def plot_profile(profile, dvs_path: Path, outdir: Path, *, moho=None, lab=None, ave=False):
    data = profile.track_dvs(dvs_path, ave=ave)

    cpt = "C-redBlue.cpt"
    fig = base_profile_fig(data, profile.lregion, moho=moho, cpt=cpt, ave=ave)

    # fig lab
    if lab is not None:
        fig.plot(data=lab, pen="1.5p,black,-")

    outpath = profile.outpath(outdir=outdir, ave=ave)
    fig.savefig(str(outpath))
