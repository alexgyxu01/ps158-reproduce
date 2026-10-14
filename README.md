# Democracy and political corruption (V-Dem v16)

**The figure.** `figure.png` is a scatter of all 179 countries V-Dem scored for
2024, plotting the **electoral democracy index** against the **political
corruption index**, with an OLS fit line. The six countries furthest from that
line in each direction are highlighted and labelled.

**The question.** Do more democratic countries have less political corruption,
and which countries are the biggest exceptions?

## Where the data come from

[V-Dem (Varieties of Democracy) dataset, version 16](https://www.v-dem.net/data/the-v-dem-dataset/)
— DOI [10.23696/vdemds26](https://doi.org/10.23696/vdemds26).

V-Dem's own download page puts every file behind an email form, so it cannot be
fetched by script. The V-Dem Institute publishes the identical data openly in
its official R package, [`vdeminstitute/vdemdata`](https://github.com/vdeminstitute/vdemdata),
and that is what `get_data.py` downloads — pinned to commit `f4dd269`, the v16
release, and verified against a known sha256 so a silent upstream change can't
pass unnoticed. Nothing is typed in by hand or read off a picture.

The file ships as `.RData`, so reading it needs `pyreadr`. No R installation is
required.

## Running it

```bash
pip install pyreadr pandas matplotlib numpy adjustText
python get_data.py     # downloads ~34 MB, writes data/democracy_corruption.csv
python plot.py         # writes figure.png and prints the checks below
```

`get_data.py --year 2023` picks a different year. The raw download is cached and
checksummed, so a second run doesn't re-fetch it.

## Variables

| Column | Meaning |
|---|---|
| `v2x_polyarchy` | Electoral democracy index, 0–1, higher = more democratic |
| `v2x_corr` | Political corruption index, 0–1, **higher = MORE corrupt** |
| `e_ti_cpi` | Transparency International CPI, 0–100, higher = cleaner |
| `e_wbgi_cce` | World Bank control of corruption, higher = cleaner |

The direction of `v2x_corr` is the one thing most likely to trip someone up: it
measures corruption, not cleanliness, so the expected relationship is negative.

## What it shows

**r = −0.71** across 179 countries; democracy accounts for about 51% of the
variance in corruption scores.

The more interesting result is that the residuals aren't random. Every one of
the six countries running **cleaner** than its democracy score predicts is a
Gulf monarchy or an Asian city-state — UAE, Hong Kong, Saudi Arabia, Singapore,
Qatar, Oman. Every one of the six running **dirtier** is an electoral democracy
or electoral autocracy in Africa, Latin America, or the Balkans — Liberia,
Nigeria, Paraguay, Madagascar, North Macedonia, Honduras.

## Checks

`plot.py` prints these on every run:

| Check | Result |
|---|---|
| 95% bootstrap CI for r (10,000 resamples) | [−0.792, −0.619] |
| Spearman rank correlation | −0.702, close to Pearson, so not driven by a few extremes |
| `v2x_corr` vs Transparency International CPI | −0.907 (n=172) |
| `v2x_corr` vs World Bank control of corruption | −0.908 (n=171) |
| Headline rebuilt using CPI instead of `v2x_corr` | +0.699 (n=172), sign flipped by CPI's scale |

The cross-source checks matter because V-Dem's democracy and corruption indices
are coded by overlapping expert panels, so some of the −0.71 could have been
shared method variance rather than two independent things agreeing. Two outside
measures, built by different organisations with different methods, correlate
with V-Dem's corruption index at about 0.91, and swapping one of them in for
`v2x_corr` moves the headline from 0.71 to 0.70. That doesn't eliminate the
concern, but it bounds it.

## Caveats

- **This is a correlation, not a cause.** The figure cannot distinguish
  democracy reducing corruption from corruption impeding democratisation, from
  both being driven by something else — oil rents and state capacity are obvious
  candidates, and the Gulf cluster is exactly where you'd expect that to bite.
- **Both headline measures are expert-coded perceptions**, not audited counts of
  corrupt acts. "Political corruption" here is what country experts judge, which
  can be shaped by how freely a country's press reports on corruption — plausibly
  correlated with democracy itself.
- **One year only.** 2024 is the latest with complete coverage on both measures;
  this is a cross-section, not a trend.

## What I'd do next

Use the panel rather than the cross-section — V-Dem runs 1789–2025, so the same
two variables can be tracked within countries over time, which would at least
remove fixed country characteristics from the comparison. The obvious second
step is testing whether the Gulf cluster survives controlling for resource
rents.
