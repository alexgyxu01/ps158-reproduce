# Democracy and political corruption (V-Dem v16)

**The figure.** `figure.png` plots the electoral democracy index against the
political corruption index for all 179 countries V-Dem scored in 2024, with an
OLS fit line. The six countries furthest from the line in each direction are
labelled.

**The data.** [V-Dem (Varieties of Democracy) v16](https://www.v-dem.net/data/the-v-dem-dataset/),
DOI [10.23696/vdemds26](https://doi.org/10.23696/vdemds26). V-Dem's own download
page is behind an email form, so `get_data.py` fetches the identical data from
the Institute's official R package, [`vdeminstitute/vdemdata`](https://github.com/vdeminstitute/vdemdata),
pinned to the v16 release commit `f4dd269` and verified by sha256.

**Running it.**

```bash
pip install pyreadr pandas matplotlib numpy adjustText
python get_data.py    # downloads ~34 MB, writes data/democracy_corruption.csv
python plot.py        # writes figure.png, prints the checks
```

**What it shows.** r = −0.71 across 179 countries. The exceptions are the
interesting part: everything running cleaner than its democracy score predicts
is a Gulf monarchy or Asian city-state, and everything running dirtier is an
electoral democracy or autocracy in Africa, Latin America, or the Balkans.

**Checks** (printed by `plot.py`). Bootstrap 95% CI [−0.79, −0.62]; Spearman
−0.70, so the result isn't driven by a few extremes. Because V-Dem's democracy
and corruption indices share expert panels, I also checked against two measures
built outside V-Dem: `v2x_corr` correlates −0.91 with Transparency
International's CPI and −0.91 with the World Bank's control-of-corruption
estimate, and rebuilding the headline on CPI gives 0.70 against 0.71.

**Caveats.** This is a correlation in a single year, not a cause — democracy
reducing corruption, corruption impeding democratisation, and a common driver
such as oil rents all fit the same scatter. Both headline measures are
expert-coded perceptions rather than counts of corrupt acts.

**Note on direction:** `v2x_corr` runs higher = *more* corrupt, so the expected
relationship is negative.
