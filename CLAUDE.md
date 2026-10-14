# Working rules for this repository

Rules followed while building this analysis. They are here so a later session
(or a later me) doesn't quietly drop them.

## Data provenance

- **Download data with a script, never by hand.** No typing numbers in, no
  reading values off a published chart. If a source can't be fetched by script,
  say so and find a scriptable mirror published by the same organisation.
- **Never script around an access gate.** V-Dem's download form exists on
  purpose. The official R package repo is the legitimate alternative, not a
  workaround for the form.
- **Pin the version.** Pin to a commit SHA, not a branch, and verify a checksum.
  A pinned source that silently changes upstream is worse than no pin, because
  the numbers move without the code changing.
- **Cache, don't re-fetch.** Verify the cached copy rather than trusting it.

## Analysis

- **Check the direction of every index before using it.** `v2x_corr` is higher
  = more corrupt, which is the opposite of most corruption measures. Getting
  this backwards silently inverts a finding. Write the direction in a comment
  next to the variable.
- **Report missingness explicitly**, and distinguish rows dropped for a missing
  headline variable from rows kept despite a missing cross-check variable.
- **Give every headline number an interval.** A point estimate with no bootstrap
  CI is not a finding.
- **Check robustness to the distribution.** Pearson alongside Spearman, mean
  alongside median — if they diverge, the extremes are the story.
- **Cross-check against sources outside the dataset** whenever the dataset
  provides them. Two variables from one expert survey agreeing is weaker
  evidence than it looks.
- **Say "correlation" and mean it.** Never let a figure caption imply a cause
  the design can't support.

## Figures

- **Look at the rendered figure before calling it done.** The first version had
  the legend sitting on top of the labelled outliers; nothing but opening the
  PNG catches that.
- **Validate the palette rather than eyeballing it.** Scatter plots need
  all-pairs colourblind separation, which caps distinct series at three.
- **Identify highlighted points by label, not colour alone.**
- **Put the source and the variable names on the figure itself.** A figure
  travels away from its README.

## Repository

- **Don't commit large raw downloads.** The 34 MB `.RData` is gitignored; the
  script re-fetches and re-verifies it.
- **Commit the derived CSV.** It's small, and it lets someone read the numbers
  without running anything.
- **Both scripts must run clean from an empty checkout**, in order, with nothing
  but the documented pip install.
