#!/usr/bin/env python3
"""
plot.py -- visualise the democracy / corruption correlation from V-Dem v16.

Reads data/democracy_corruption.csv (produced by get_data.py) and writes
figures/democracy_corruption.png.

The chart is a scatter of all countries with an OLS fit line. The countries
furthest from that line in each direction are highlighted and labelled --
they are the substantive point of the figure, not decoration.

Usage
-----
    python get_data.py && python plot.py
    python plot.py --n-labels 8
    python plot.py --input data/democracy_corruption.csv --output figures/x.png
"""

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from adjustText import adjust_text

HERE = Path(__file__).resolve().parent

# --- Palette -------------------------------------------------------------
# Validated for all-pairs colourblind separation on the light surface
# (worst CVD dE 9.2, worst normal-vision dE 24.0). The aqua slot sits below
# 3:1 against the surface, which is why every highlighted point is directly
# labelled rather than identified by colour alone.
SURFACE      = "#fcfcfb"
INK_PRIMARY  = "#0b0b0b"
INK_SECOND   = "#52514e"
INK_MUTED    = "#898781"
GRIDLINE     = "#e1e0d9"
AXISLINE     = "#c3c2b7"

C_MAIN       = "#2a78d6"   # slot 1, blue   -- all other countries
C_CORRUPT    = "#eb6834"   # slot 2, orange -- more corrupt than predicted
C_CLEAN      = "#1baf7a"   # slot 3, aqua   -- cleaner than predicted


def load(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise SystemExit(f"{path} not found. Run `python get_data.py` first.")
    return pd.read_csv(path)


def build(df: pd.DataFrame, n_labels: int):
    """Fit the line and tag the largest residual in each direction."""
    x = df["v2x_polyarchy"].to_numpy()
    y = df["v2x_corr"].to_numpy()

    slope, intercept = np.polyfit(x, y, 1)
    df = df.copy()
    df["fitted"] = intercept + slope * x
    df["resid"] = y - df["fitted"]

    r = float(np.corrcoef(x, y)[0, 1])

    clean = df.nsmallest(n_labels, "resid")       # below the line = cleaner
    corrupt = df.nlargest(n_labels, "resid")      # above the line = more corrupt
    flagged = set(clean.index) | set(corrupt.index)
    rest = df[~df.index.isin(flagged)]

    return df, rest, clean, corrupt, slope, intercept, r


def label_points(ax, subsets):
    """Direct-label the highlighted countries, repelling labels off each other.

    Highlighted points are identified by label, not by colour alone -- the aqua
    slot is below 3:1 against the surface, so the labels are load-bearing for
    accessibility, not ornament.
    """
    texts = []
    for subset in subsets:
        for row in subset.to_dict("records"):
            texts.append(ax.text(
                row["v2x_polyarchy"], row["v2x_corr"], row["country_name"],
                fontsize=8.4, color=INK_SECOND, zorder=7,
            ))

    adjust_text(
        texts,
        ax=ax,
        expand=(1.25, 1.6),
        force_text=(0.5, 0.9),
        force_static=(0.2, 0.4),
        arrowprops=dict(arrowstyle="-", color=AXISLINE, linewidth=0.8,
                        shrinkA=2, shrinkB=3),
    )


def render(df, rest, clean, corrupt, slope, intercept, r, year, out_path):
    fig, ax = plt.subplots(figsize=(11.5, 7.8), dpi=200)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)

    # Grid sits behind everything and stays recessive.
    ax.set_axisbelow(True)
    ax.grid(True, color=GRIDLINE, linewidth=0.8)

    # --- Fit line --------------------------------------------------------
    xs = np.linspace(0, 1, 100)
    ax.plot(xs, intercept + slope * xs, color=INK_MUTED, linewidth=2,
            zorder=2, label="Line of best fit")

    # --- Marks -----------------------------------------------------------
    # A 2px surface ring keeps overlapping points readable.
    common = dict(s=52, linewidth=1.4, edgecolor=SURFACE, zorder=3)
    ax.scatter(rest["v2x_polyarchy"], rest["v2x_corr"],
               color=C_MAIN, alpha=0.65, label="All other countries", **common)
    ax.scatter(corrupt["v2x_polyarchy"], corrupt["v2x_corr"],
               color=C_CORRUPT, zorder=5,
               label="More corrupt than the fit predicts",
               **{k: v for k, v in common.items() if k != "zorder"})
    ax.scatter(clean["v2x_polyarchy"], clean["v2x_corr"],
               color=C_CLEAN, zorder=5,
               label="Cleaner than the fit predicts",
               **{k: v for k, v in common.items() if k != "zorder"})

    label_points(ax, [corrupt, clean])

    # --- Axes ------------------------------------------------------------
    ax.set_xlim(-0.03, 1.0)
    ax.set_ylim(-0.06, 1.06)
    ax.set_xlabel("Electoral democracy index  (0 = least democratic, 1 = most)",
                  fontsize=10.5, color=INK_SECOND, labelpad=10)
    ax.set_ylabel("Political corruption index  (0 = least corrupt, 1 = most)",
                  fontsize=10.5, color=INK_SECOND, labelpad=10)
    ax.tick_params(colors=INK_MUTED, labelsize=9.5, length=0)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(AXISLINE)

    # --- Correlation callout --------------------------------------------
    ax.text(
        0.975, 0.955,
        f"r = {r:.2f}",
        transform=ax.transAxes, ha="right", va="top",
        fontsize=19, color=INK_PRIMARY, fontweight="bold",
    )
    ax.text(
        0.975, 0.905,
        f"{len(df)} countries, {year}",
        transform=ax.transAxes, ha="right", va="top",
        fontsize=9.5, color=INK_MUTED,
    )

    # --- Titles ----------------------------------------------------------
    fig.suptitle(
        "More democratic countries are less corrupt — but the exceptions cluster",
        x=0.062, y=0.965, ha="left",
        fontsize=16.5, color=INK_PRIMARY, fontweight="bold",
    )
    fig.text(
        0.062, 0.905,
        "Gulf monarchies and city-states run far cleaner than their democracy scores predict; "
        "the countries that run dirtier\nare mostly electoral democracies in Africa, "
        "Latin America and the Balkans.",
        ha="left", va="top", fontsize=10.5, color=INK_SECOND, linespacing=1.5,
    )

    # Legend sits below the plot: the lower-left corner of the panel is where
    # the cleaner-than-predicted outliers live, so an in-panel legend collides
    # with exactly the points the figure is about.
    leg = ax.legend(
        loc="upper left", bbox_to_anchor=(0.0, -0.105), ncol=4,
        frameon=False, fontsize=9.5, labelcolor=INK_SECOND,
        handletextpad=0.6, columnspacing=1.8, borderpad=0.0,
    )
    for handle in leg.legend_handles:
        handle.set_alpha(1.0)

    fig.text(
        0.062, 0.022,
        "Source: V-Dem (Varieties of Democracy) dataset v16, variables v2x_polyarchy and v2x_corr. "
        "doi.org/10.23696/vdemds26",
        ha="left", fontsize=8.5, color=INK_MUTED,
    )

    fig.subplots_adjust(left=0.075, right=0.975, top=0.845, bottom=0.145)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, facecolor=SURFACE)
    print(f"[plot]     wrote {out_path}")


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--input", type=Path, default=HERE / "data" / "democracy_corruption.csv")
    p.add_argument("--output", type=Path, default=HERE / "figures" / "democracy_corruption.png")
    p.add_argument("--n-labels", type=int, default=6,
                   help="how many outliers to label in each direction (default: 6)")
    args = p.parse_args()

    df = load(args.input)
    year = int(df["year"].iloc[0])
    df, rest, clean, corrupt, slope, intercept, r = build(df, args.n_labels)

    print(f"[plot]     {len(df)} countries, year {year}")
    print(f"[plot]     slope {slope:.3f}, intercept {intercept:.3f}, Pearson r {r:.3f}")
    print(f"[plot]     r^2 = {r**2:.3f} -- democracy accounts for "
          f"{r**2*100:.0f}% of the variance in corruption scores")
    print(f"\n[plot]     Cleaner than predicted: "
          f"{', '.join(clean.sort_values('resid')['country_name'])}")
    print(f"[plot]     More corrupt than predicted: "
          f"{', '.join(corrupt.sort_values('resid', ascending=False)['country_name'])}")

    render(df, rest, clean, corrupt, slope, intercept, r, year, args.output)


if __name__ == "__main__":
    main()
