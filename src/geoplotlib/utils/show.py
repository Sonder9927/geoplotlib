import pandas as pd
import pygmt


def show_phv_avg(phv_csv, hull=None):
    df = pd.read_csv(phv_csv)
    df = df[["longitude", "latitude", "phv", "period"]]
    phv_info = f"{phv_csv}: "
    for period, idf in df.groupby("period"):
        avg = idf["phv"].mean()
        if hull:
            idf_clip = pygmt.select(idf, polygon=hull)
            avg = idf_clip["phv"].mean()
        phv_info += f"{period}s({avg:.3f}), "
    print(phv_info)
    return phv_info
