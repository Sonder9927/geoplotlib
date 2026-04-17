import json
from pathlib import Path
from typing import List

from geoplotlib.gmt.mk_data import data_avg, tomo_grid
import pandas as pd
import pygmt
from tqdm import tqdm

from geoplotlib.gallery.profile import plot_profile, plot_profile_distribution
from geoplotlib.gallery.vel2d import plot_vs2d
from geoplotlib.gallery.measurement import plot_misfit


class Profile:
    def __init__(self, data, depth, id):
        self.id = id
        self.line = data["line"]
        self.pid = data["pid"]
        self.y1, self.y2 = depth

    @property
    def idx(self):
        return "xy"[self.id]

    @property
    def lregion(self):
        x1, x2 = self.line[0][self.id], self.line[1][self.id]
        return [min(x1, x2), max(x1, x2), self.y1, self.y2]

    @property
    def track_points(self):
        return pygmt.project(center=self.line[0], endpoint=self.line[1], generate=0.1)

    def outpath(self, outdir, ave=False) -> Path:
        dest = Path(outdir) / f"profile_{self.pid}{self.pid}_{self.idx}.png"
        if ave:
            dest = dest.with_suffix(".ave.png")
        return dest

    def track(self, grid):
        df = pygmt.grdtrack(grid=grid, points=self.track_points, newcolname="track")
        df = df.iloc[:, [0, 1, 3]]
        df.columns = ["x", "y", "v"]
        return df[[self.idx, "v"]]

    def track_dvs(self, dvs_path: Path, ave=False) -> pd.DataFrame:
        suffix = "ave" if ave else "vel"
        dfs = []
        for dvsf in dvs_path.glob(f"dvs-*-{suffix}.gmt"):
            dep = dvsf.name.split("-")[1]
            idf = self.track(dvsf)
            idf["z"] = -abs(float(dep))
            dfs.append(idf)
        return pd.concat(dfs)[[self.idx, "z", "v"]]


def mk_dvs_path(dvs_dir, vs_csv, region, ave, hull) -> Path:
    dvs_path = Path(dvs_dir)
    dvs_path.mkdir(parents=True, exist_ok=True)
    if not vs_csv:
        return dvs_path

    # remake dvs
    print("remaking dvs")
    df = pd.read_csv(vs_csv)
    suffix = "ave" if ave else "vel"
    for depth, idf in tqdm(df.groupby("z")):
        idf = idf[["x", "y", "vs"]]
        if ave:
            idf = data_avg(idf, hull, col="vs")
        outfile = dvs_path / f"dvs-{abs(depth)}-{suffix}.gmt"
        tomo_grid(idf, region, outfile=str(outfile))
    print(f"remake dvs in dir {dvs_path}")

    return dvs_path


def _load_ml(ml_csv, region):
    temp_path = Path("temp")
    temp_path.mkdir(exist_ok=True)
    df = pd.read_csv(ml_csv) if ml_csv else pd.DataFrame(columns=["x", "y"])
    moho_grd, lab_grd = None, None
    if "moho" in df.columns:
        moho_grd = str(temp_path / "moho.grd")
        tomo_grid(df[["x", "y", "moho"]], region, moho_grd, surface=0.25)
    if "lab" in df.columns:
        lab_grd = str(temp_path / "lab.grd")
        tomo_grid(df[["x", "y", "lab"]], region, lab_grd, surface=0.25)
    return moho_grd, lab_grd


def profiles(
    profiles_json,
    outflag="vs",
    *,
    vs_csv=None,
    region=None,
    mml_csv=None,
    dvs_dir="temp",
    ave=False,
    hull=None,
    ids=[0, 1],
):
    dvs_path = mk_dvs_path(dvs_dir, vs_csv, region, ave, hull)
    outdir = Path(f"images/{outflag}")
    outdir.mkdir(parents=True, exist_ok=True)

    profiles = load_profiles(profiles_json, ids)
    moho_grd, lab_grd = _load_ml(ml_csv=mml_csv, region=region)

    for profile in tqdm(profiles):
        moho_df = profile.track(moho_grd) if moho_grd else None
        moho_df["v"] = -abs(moho_df["v"])
        lab_df = profile.track(lab_grd) if lab_grd else None
        plot_profile(profile, dvs_path, outdir, moho=moho_df, lab=lab_df, ave=ave)


def profile_distribution(
    profiles_json, mml_csv, region, flag="lab", ave=False, hull=None
):
    df = pd.read_csv(mml_csv)[["x", "y", flag]]
    profiles = load_profiles(profiles_json)
    outpath = "images/profile_distribution.png"
    plot_profile_distribution(df, profiles, region, outpath=outpath, ave=ave, hull=hull)


def load_profiles(profiles_json: str, ids=None) -> List[Profile]:
    if ids is None:
        ids = [0]
    with open(profiles_json) as f:
        data = json.load(f)
    depth = data["depth"]
    return [Profile(pdata, depth, id) for pdata in data["profiles"] for id in ids]


def depths(vs_csv, region, outflag="vs", hull=None, dz=20, ave=False):
    df = pd.read_csv(vs_csv)
    outdir = Path(f"images/{outflag}")
    outdir.mkdir(parents=True, exist_ok=True)
    df = df[df["z"] % dz == 0]
    for depth, idf in tqdm(df.groupby("z")):
        outpath = outdir / f"depth_{abs(depth)}km.png"
        idata = idf[["x", "y", "vs"]]
        plot_vs2d(depth, idata, region, outpath, hull=hull, ave=ave)


def misfit(misfit_csv, region, outflag="vs", hull=None):
    df = pd.read_csv(misfit_csv)[["x", "y", "misfit"]]
    # df["misfit"] *= 0.8
    outdir = Path(f"images/{outflag}")
    outdir.mkdir(exist_ok=True)
    outpath = outdir / f"misfit_{outflag}.png"
    plot_misfit(df, region, str(outpath), hull=hull)
