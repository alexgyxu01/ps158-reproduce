#!/usr/bin/env python3
"""
get_data.py -- acquire V-Dem v16 and extract the variables for this analysis.

Question
--------
Do more democratic countries have less political corruption, and which
countries are the biggest exceptions?

Source
------
V-Dem (Varieties of Democracy) dataset, version 16.

The V-Dem Institute's own download page gates every file behind an email
form, so it is not scriptable. The Institute also publishes the identical
data in its official R package, openly, on GitHub:

    https://github.com/vdeminstitute/vdemdata

This script downloads `data/vdem.RData` from that repository, pinned to the
v16 release commit, so the fetch is reproducible and needs no credentials.
The file ships as .RData rather than CSV, so reading it needs `pyreadr`
(pip install pyreadr). No R installation is required.

Dataset DOI: https://doi.org/10.23696/vdemds26

Usage
-----
    python get_data.py                 # download if needed, then extract
    python get_data.py --year 2023     # pick a different year
    python get_data.py --force         # re-download even if cached
"""

import argparse
import hashlib
import sys
import urllib.request
from pathlib import Path

# --- Pinned source -------------------------------------------------------
# Commit f4dd269 is the "v16 release" commit (2026-03-17) of vdeminstitute/vdemdata.
# Pinning to the SHA rather than a branch means this script keeps returning the
# same data even after the Institute pushes v17.
COMMIT = "f4dd26922e658442524dfd954bf14f7ebe622d5d"
DATA_URL = (
    f"https://raw.githubusercontent.com/vdeminstitute/vdemdata/{COMMIT}/data/vdem.RData"
)
EXPECTED_SHA256 = "39b412d39a061c18f20c98e4ad4d6355b05a0441df31be4ee9aec420dc3d95ea"
EXPECTED_BYTES = 33_878_255

# --- Variables we keep ---------------------------------------------------
# Both headline measures are expert-coded by V-Dem itself, on 0-1 scales.
# NOTE ON DIRECTION: v2x_corr runs 0 = least corrupt, 1 = most corrupt.
# It is an index of corruption, not of cleanliness. Easy to flip by accident.
COLUMNS = {
    "country_name": "Country name",
    "country_text_id": "3-letter country code",
    "year": "Year",
    "v2x_polyarchy": "Electoral democracy index (0-1, higher = more democratic)",
    "v2x_corr": "Political corruption index (0-1, higher = MORE corrupt)",
    "v2x_regime": "Regimes of the World category (0-3)",
    "e_regionpol_6C": "Politico-geographic region (6 categories)",
    # Two corruption measures from OUTSIDE V-Dem, bundled into the Full dataset.
    # They are produced by different organisations with different methods, so
    # they are an independent check on V-Dem's own v2x_corr rather than a
    # restatement of it. Both run in the opposite direction to v2x_corr.
    "e_ti_cpi": "Transparency International CPI (0-100, higher = CLEANER)",
    "e_wbgi_cce": "World Bank control of corruption (~-2.5 to 2.5, higher = CLEANER)",
}

REGIME_LABELS = {
    0: "Closed autocracy",
    1: "Electoral autocracy",
    2: "Electoral democracy",
    3: "Liberal democracy",
}

REGION_LABELS = {
    1: "Eastern Europe & Central Asia",
    2: "Latin America & Caribbean",
    3: "Middle East & North Africa",
    4: "Sub-Saharan Africa",
    5: "Western Europe & North America",
    6: "Asia & Pacific",
}

HERE = Path(__file__).resolve().parent
RAW_DIR = HERE / "data" / "raw"
OUT_DIR = HERE / "data"
RAW_PATH = RAW_DIR / "vdem_v16.RData"
OUT_PATH = OUT_DIR / "democracy_corruption.csv"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download(force: bool = False) -> Path:
    """Download the pinned V-Dem .RData, unless a valid copy is already cached."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    if RAW_PATH.exists() and not force:
        digest = sha256(RAW_PATH)
        if digest == EXPECTED_SHA256:
            print(f"[cache]    {RAW_PATH.name} already present and verified")
            return RAW_PATH
        print(f"[cache]    checksum mismatch on cached file, re-downloading")

    print(f"[download] {DATA_URL}")
    print(f"[download] ~{EXPECTED_BYTES / 1e6:.1f} MB, this takes a moment...")
    urllib.request.urlretrieve(DATA_URL, RAW_PATH)

    size = RAW_PATH.stat().st_size
    digest = sha256(RAW_PATH)
    print(f"[download] got {size:,} bytes")

    if size != EXPECTED_BYTES:
        print(
            f"[WARN]     expected {EXPECTED_BYTES:,} bytes. The pinned commit may "
            f"have been changed upstream."
        )
    if digest != EXPECTED_SHA256:
        print(f"[WARN]     sha256 {digest}")
        print(f"[WARN]     expected {EXPECTED_SHA256}")
        print("[WARN]     Contents differ from what this script was written against.")
    else:
        print("[verify]   sha256 matches the pinned v16 release")

    return RAW_PATH


def extract(raw_path: Path, year: int):
    try:
        import pyreadr
    except ImportError:
        sys.exit("Missing dependency. Run: pip install pyreadr pandas matplotlib")

    print(f"[read]     parsing .RData (large file, ~10s)...")
    result = pyreadr.read_r(str(raw_path))
    df = result["vdem"]
    print(f"[read]     full dataset: {df.shape[0]:,} rows x {df.shape[1]:,} columns")
    print(f"[read]     years {int(df['year'].min())}-{int(df['year'].max())}, "
          f"{df['country_name'].nunique()} countries")

    missing = [c for c in COLUMNS if c not in df.columns]
    if missing:
        sys.exit(f"Expected columns absent from the source data: {missing}")

    sub = df[list(COLUMNS)].copy()
    sub = sub[sub["year"] == year].copy()
    if sub.empty:
        sys.exit(f"No rows for year {year}.")

    print(f"\n[extract]  year {year}: {len(sub)} country rows before cleaning")
    for col in ("v2x_polyarchy", "v2x_corr", "e_ti_cpi", "e_wbgi_cce"):
        n_missing = int(sub[col].isna().sum())
        note = "  (headline, rows dropped)" if col in ("v2x_polyarchy", "v2x_corr") \
            else "  (cross-check only, rows kept)"
        print(f"[extract]    {col:16s} missing: {n_missing:3d}{note}")

    before = len(sub)
    sub = sub.dropna(subset=["v2x_polyarchy", "v2x_corr"])
    if before != len(sub):
        print(f"[extract]  dropped {before - len(sub)} rows missing a headline measure")

    sub["regime_label"] = sub["v2x_regime"].map(REGIME_LABELS)
    sub["region_label"] = sub["e_regionpol_6C"].map(REGION_LABELS)
    sub = sub.sort_values("country_name").reset_index(drop=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    sub.to_csv(OUT_PATH, index=False)

    # --- Report ----------------------------------------------------------
    r = sub["v2x_polyarchy"].corr(sub["v2x_corr"])
    print(f"\n[result]   wrote {OUT_PATH.relative_to(HERE)}  ({len(sub)} countries)")
    print(f"[result]   electoral democracy range: "
          f"{sub['v2x_polyarchy'].min():.3f} to {sub['v2x_polyarchy'].max():.3f}")
    print(f"[result]   political corruption range: "
          f"{sub['v2x_corr'].min():.3f} to {sub['v2x_corr'].max():.3f}")
    print(f"[result]   Pearson r (democracy vs corruption) = {r:.3f}")
    print(f"\n[note]     v2x_corr is higher = MORE corrupt, so a negative r means "
          f"more democratic countries are cleaner.")
    return sub


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--year", type=int, default=2024,
                   help="survey year to extract (default: 2024, the latest with "
                        "complete coverage on both measures)")
    p.add_argument("--force", action="store_true",
                   help="re-download even if a verified cached copy exists")
    args = p.parse_args()

    raw = download(force=args.force)
    extract(raw, args.year)


if __name__ == "__main__":
    main()
