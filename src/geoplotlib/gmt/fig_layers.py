from typing import List

import pandas as pd


def fig_topo(fig, topo, frame=["a"], projection=None, gra=False):
    projection = projection or _hscale(topo["region"])
    fig.basemap(region=topo["region"], projection=projection, frame=frame)
    if gra:
        fig.grdimage(grid=topo["grid"], cmap=topo["cmap"], shading=gra)


def fig_tomos(fig, tomos: List, region: List, gra):
    for tomo in tomos:
        fig.grdimage(
            grid=tomo["grid"],
            cmap=tomo["cmap"],
            region=region,
            nan_transparent=True,
            shading=gra,
        )


def fig_stations(fig, sta_csv, colorful=False):
    df = pd.read_csv(sta_csv)
    if colorful:
        ides = df["ide"].unique()
        symbols = _colorful_symbols(ides)

        for ide in ides:
            idf = df[df["ide"] == ide]
            symbol = symbols[ide]
            fig.plot(
                x=idf["longitude"],
                y=idf["latitude"],
                style=symbol["style"],
                fill=symbol["fill"],
                pen=f"0.5p,{symbol['fill']}",
                label=symbol["label"],
            )
        fig.legend()
    else:
        fig.plot(
            x=df["longitude"],
            y=df["latitude"],
            style="t0.2c",
            fill="seagreen",
            pen="0.3p,black",
        )


def fig_annotation(fig, x, y, text, justify="LT"):
    fig.text(
        x=x, y=y, text=text, justify=justify, offset="0.01j", fill="white", font="9p"
    )


def _hscale(region: List):
    x = (region[0] + region[1]) / 2
    y = (region[2] + region[3]) / 2
    return f"m{x}/{y}/0.3i"


def _colorful_symbols(ides: List):
    symbol_templates = [
        {"style": "t0.2c", "fill": "tomato", "label": "Type1"},
        {"style": "i0.2c", "fill": "darkblue", "label": "Type2"},
        {"style": "t0.2c", "fill": "red", "label": "Type1"},
        {"style": "a0.2c", "fill": "gold", "label": "Type3"},
        {"style": "a0.2c", "fill": "green", "label": "Type5"},
        {"style": "i0.2c", "fill": "brown", "label": "Type6"},
    ]
    symbols = {}
    for i, ide in enumerate(ides):
        template = symbol_templates[i % len(symbol_templates)]
        symbols[ide] = {
            "style": template["style"],
            "fill": template["fill"],
            "label": ide,
        }
    return symbols
