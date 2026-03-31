import matplotlib.pyplot as plt


def plot_dispersion(lat, lon, df1, df2, outfile):
    df1 = df1.sort_values("period")
    df2 = df2.sort_values("period")

    plt.figure(figsize=(12, 5))
    # plt.plot(df1["period"], df1["phv"], "o-", label="TPWT", color="red")
    plt.errorbar(
        df1["period"],
        df1["phv"],
        yerr=df1["std"] / 1000,
        fmt="o-",
        label="TPWT",
        color="red",
        capsize=3,
        ecolor="gray",
        elinewidth=1,
    )
    plt.plot(df2["period"], df2["phv"], "s-", label="ANT", color="blue")

    plt.xlabel("Period (s)")
    plt.ylabel("Phase Velocity (km/s)")
    plt.title(f"({lat:.2f}, {lon:.2f})")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.6)

    plt.savefig(outfile, dpi=150, bbox_inches="tight")
    plt.close()
