# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A small SmartMet data ingestion module distributed as a `noarch` RPM —
sibling of `smartmet-data-gts-synop` but for upper-air sounding bulletins
(WMO TEMP, FM-35). The conversion script is **PHP, not shell** (unusual
for this family of packages), and there is no build step — the RPM
just installs `dosounding.php` and a cron file.

## Layout

- `dosounding.php` — driven by cron every 20 min. Globs every file in the incoming dir, extracts `TTAA` and `TTBB` reports with regex (multi-line, ungreedy, terminated by `=`), deduplicates by (location, date, type), writes a sorted text concatenation, then runs `temp2qd` to produce a `.sqd` and copies it to both the data tree and the editor inbox.
- `smartmet-data-gts-sounding.spec` — RPM packaging. Creates the `/smartmet/...` tree, the cron entry (every 20 min), and the hourly cleaner (`%{smartmetroot}/cnf/cron/cron.hourly/clean_data_gts_sounding`).

## Runtime pipeline

1. Cron triggers `dosounding.php` every 20 minutes. Cron redirects all stdout/stderr to `/smartmet/logs/data/sounding-gts.log` — unlike the synop scripts the PHP itself does not handle log redirection.
2. Read every file in `/smartmet/data/incoming/gts/sounding/`.
3. Regex-extract `TTAA` and `TTBB` blocks (one per report), trimming whitespace.
4. Group by `messages[location][date][type]` and emit them sorted by location → date → type, joined with CRLF, into `tmp/data/sounding/<timestamp>_gts_world_sounding.sqd.txt`.
5. If the text file is non-empty: `temp2qd -t … > …sqd` in tmp.
6. If the `.sqd` is non-empty: `rename` it into `/smartmet/data/gts/sounding/world/querydata/`, `cp` to `/smartmet/editor/in/`, `rm` the text file.

The hourly cleaner keeps only the 2 most-recent `.sqd` files in the output and editor dirs and deletes incoming files older than 7 days.

## Editing rules specific to this repo

- **Version bump = touch `Version:` and add a `%changelog` entry.** Date-based `YY.MM.DD` (e.g. `26.5.21`). The version field currently sits at `17.10.4` but the changelog only carries the `17.10.3` initial entry — there is an inherited mismatch here.
- **Hardcoded `/smartmet` paths.** Unlike the synop scripts, `dosounding.php` does not fall back to `$HOME` when `/smartmet` is missing. Running it locally for ad-hoc testing requires `mkdir -p /smartmet/...` (with sudo) or editing the constants.
- **PHP `system()` and `exec()` are unescaped.** Treat changes that introduce variable-derived shell arguments very carefully — at the moment the only externally-influenced value is the glob path, but watch the existing `system("temp2qd -t $TMPDIR/$OUTFILE.txt > …")` pattern when adding logic.
- **Don't `git push` straight to master.** PR-based flow is the FMI convention even though earlier commits on this repo were direct-to-master.

## Building the RPM (FMI infrastructure)

Same shape as the sibling `smartmet-data-gts-synop`: the `%install` section expects sources under `%_topdir/SOURCES/smartmet-data-gts-sounding/`. Production builds happen in FMI's CI. Locally:

```sh
rpmbuild -ba smartmet-data-gts-sounding.spec
```

after staging `dosounding.php` into `~/rpmbuild/SOURCES/smartmet-data-gts-sounding/`. End users install via `yum install smartmet-data-gts-sounding`.

## macOS note

This package is RHEL-only (RPM, `/smartmet` paths, cron). It is **not** part of the macOS port described in the parent workspace's `CLAUDE.md`. Don't add `Makefile.mac` or `#ifdef __APPLE__` patches here.
