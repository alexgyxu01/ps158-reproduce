---
name: reproducible-figure
description: Build a reproducible data figure from a public source — find and verify the data, download it with a pinned script, check the headline number, and render a labelled chart. Use when asked to chart, plot, or visualise a relationship from a named public dataset (V-Dem, SCF, World Bank, Eurostat, census or survey microdata), or to reproduce a published figure from its underlying data.
---

# Reproducible figure from a public dataset

Produces two scripts and a figure that someone else can rerun from an empty
checkout. The order matters: **find and report before building anything.**

## 1. Find the data, and report before building

Do not write a line of analysis code until the source is pinned down.

- Identify the publisher's **own** distribution. Prefer the organisation that
  produces the data over any mirror or aggregator.
- **Check whether it can be fetched by script at all.** Many official downloads
  sit behind an email form or a click-through licence. Never script around one.
  Look instead for a legitimate alternative the same organisation publishes — an
  official package repository, an API, a DOI'd archive deposit.
- Download one copy and **actually open it**. Report, before building:
  - rows, columns, year range, unit of observation
  - the exact variable names the question needs, confirmed present
  - coverage of those variables in the target year — a variable that exists but
    is empty for recent years is a trap
  - anything that contradicts the request

If the request can't be answered with the data in hand, **say so and stop**. The
most common failure is building a beautiful chart on variables that don't
measure what was asked for.

## 2. get_data.py

One script, rerunnable, no manual steps.

- **Pin to an immutable reference** — a commit SHA, a versioned release URL, a
  DOI — never a branch or a "latest" link.
- **Verify a checksum** and print whether it matched. Warn loudly on mismatch
  rather than failing silently.
- **Cache**, and re-verify the cache rather than trusting it. Offer `--force`.
- Subset to the needed columns, **write a small derived CSV**, and gitignore the
  raw download if it's large.
- Print a report: shape, year range, missingness per variable, and the headline
  statistic. Distinguish rows dropped for missing headline variables from rows
  kept despite missing optional ones.
- **Record every variable's direction in a comment.** Indices that run "higher =
  worse" sitting beside ones that run "higher = better" are the single most
  reliable way to invert a finding without noticing.

## 3. Check the number before drawing it

A point estimate alone is not a result. Produce:

- an **interval** — bootstrap percentile CI is fine and assumption-light
- a **robustness check** that drops a distributional assumption — Spearman
  against Pearson, median against mean. Divergence means extremes are driving it
- a **cross-source check** — at least one measure of the same concept from a
  different producer. Two variables from the same expert survey agreeing is much
  weaker evidence than it appears. Many datasets bundle external indicators for
  exactly this purpose; look before reaching outside.

Print these every run, so they can't drift away from the figure.

## 4. plot.py

- Read the derived CSV. **Never recompute the download here.**
- Load design guidance before writing chart code. For scatter plots, colour must
  validate on **all pairs**, which caps distinct series at about three — plan the
  encoding around that rather than discovering it late.
- **Highlight and directly label the interesting points**, not every point.
  Outliers and residuals are usually the substance; the trend is the setup.
- Keep the legend **out of the region where the highlighted points live.**
- Put **source, variable names, and n** on the figure itself.
- **Render it and open it.** Label collisions, legend overlap and clipped text
  are invisible in code and obvious in the PNG. Use a label-repulsion pass
  (`adjustText`) rather than hand-tuned offsets, which break on new data.

## 5. README.md

Which figure, where the data come from, how to rerun, what it shows, the checks
with their numbers, and the caveats. State plainly that a correlation is a
correlation. Name the most likely confounders rather than gesturing at them.

## Failure modes seen in practice

- Variables that exist in the codebook but are empty for the year wanted.
- An index whose direction is the reverse of the obvious reading.
- A legend placed exactly on top of the labelled outliers.
- Treating the dataset's own bundled external indicators as if they were part of
  the same expert survey, and so missing a free cross-source check.
- Committing a 30 MB raw download that the script could re-fetch.
