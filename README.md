# Geoplotlib

Plot geophysical maps.

## Examples

```python
# params
region = [172.0, 179.5, -42.5, -34.0]
sta_csv = "data/nz/stations.csv"
hull = "data/nz/sta_hull.nc"
mk_hull(sta_csv, region, hull)

# plot stas evts
plt.regions.station_location(region, sta_csv, "images/station_location.png")
plt.events.event_location(
    region, "data/nz/events.csv", "data/nz/eqlist.csv", "images/event_location.png"
)
plt.events.event_counts("data/nz/eqlist.csv", "st", "images/event_counts.png")
plt.events.event_paths("data/nz/eqlist.csv", "data/nz/events.csv", sta_csv, region)

# plot tpwt res
sta_csv = None
tpwt_phv = "data/nz/tpwt_phv.csv"
plt.phase.phvs(tpwt_phv, region, "tpwt", sta_csv=sta_csv, hull=hull)
plt.phase.misfits(tpwt_phv, region, "tpwt")
plt.phase.checkboards(tpwt_phv, region, dcheck=1.5, outflag="tpwt", hull=hull)

# comparation
flag = "fmst"
plt.phase.diff(30, f"data/nz/{flag}_phv.csv", tpwt_phv, region, hull=hull, method1=flag)
```
