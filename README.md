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
show_phv_avg("data/nz/fmst_phv_20260302.csv", hull)

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
plt.events.event_paths("data/nz/eqlist-snr10sm100.csv", "data/nz/events.csv", sta_csv, region)
# plot tpwt res
sta_csv = None
plt.phase.phvs(tpwt_phv, region, "tpwt", sta_csv=sta_csv, hull=hull)
plt.phase.stddevs(tpwt_phv, region, "tpwt", hull)
plt.phase.checkboards(tpwt_phv, region, dcheck=1, outflag="tpwt", hull=hull)
# comparation
flag = "fmst"
plt.phase.diff(30, f"./data/nz/{flag}_phv.csv", tpwt_phv, region, hull=hull, method1=flag)
plt.phase.dispersions(tpwt_phv, "data/nz/fmst_phv-spec.csv", region, hull=hull)
```
