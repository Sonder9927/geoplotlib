# Geoplotlib

Plot geophysical maps.

## Examples

```python
import geoplotlib as plt
from geoplotlib import mk_hull, show_phv_avg

# params
region = [172.0, 179.5, -42.5, -34.0]
sta_csv = "data/nz/stations.csv"
hull = "data/nz/sta_hull.nc"
mk_hull(sta_csv, hull)

# print info
# hull=None
show_phv_avg("data/nz/tpwt_phv.csv", hull)
show_phv_avg("data/nz/fmst_phv.csv", hull)

tpwt_phv = "./data/nz/tpwt_phv.csv"

# plot stas evts
plt.regions.station_location(region, sta_csv, "images/station_location.png")
plt.events.event_location(
    region, "data/nz/events.csv", "data/nz/eqlist.csv", "images/event_location.png"
)
plt.events.event_counts(
    "data/nz/eqlist.csv",
    tpwt_phv,
    "images/event_counts.png",
    ant_csv="data/nz/fmst_phv.csv",
    iter_csv="data/nz/tpwt_iter.csv",
)
plt.events.event_paths("data/nz/eqlist.csv", "data/nz/events.csv", sta_csv, region)
# plot tpwt res
sta_csv = None
plt.phase.phvs(tpwt_phv, region, "tpwt", sta_csv=sta_csv, hull=hull)
plt.phase.stddevs(tpwt_phv, region, "tpwt", hull)
plt.phase.checkboards(tpwt_phv, region, dcheck=1, outflag="tpwt", hull=hull)
# comparation
flag = "fmst"
plt.phase.diff(30, f"./data/nz/{flag}_phv.csv", tpwt_phv, region, hull=hull, method1=flag)
plt.phase.dispersions(tpwt_phv, "data/nz/fmst_phv-spec.csv", region, hull=hull)


# interfaces
mml_csv = "data/nz/mcmc-res/misfit_moho_lab.csv"
plt.interface(mml_csv, "moho", region, hull=None)
plt.interface(mml_csv, "lab", region, hull=None)

# vs
profiles_json = "data/nz/mcmc-res/profiles.json"
plt.vs.depths("./data/nz/mcmc-res/vs.csv", region, "mcmc", hull=hull, dz=10, ave=True)
plt.vs.misfit(mml_csv, region, "mcmc", hull=hull)
# profiles
plt.vs.profile_distribution(profiles_json, mml_csv, region, flag="lab", hull=hull)
plt.vs.profiles(
    profiles_json,
    "mcmc",
    vs_csv="data/nz/mcmc-res/vs.csv",
    mml_csv=mml_csv,
    region=region,
    # ave=True,
    hull=hull,
)
```
