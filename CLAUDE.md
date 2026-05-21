# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A small SmartMet data ingestion module distributed as a `noarch` RPM —
sibling of `smartmet-data-gts-synop` but for upper-air sounding bulletins.
There is no build step; the RPM installs the two ingestion scripts and a
cron file.

## Layout

- `dosounding.php` — text-TEMP path (FM-35). PHP because the conversion needs regex extraction of `TTAA`/`TTBB` blocks before `temp2qd` can parse them.
- `dosounding-bufr.sh` — BUFR path. Plain bash; runs `bufrtoqd -C sounding --subsets` over the incoming dir.
- `smartmet-data-gts-sounding.spec` — RPM packaging. Creates the `/smartmet/...` tree, the cron entry (both scripts every 20 min), and the hourly cleaner (`%{smartmetroot}/cnf/cron/cron.hourly/clean_data_gts_sounding`).

## Runtime pipelines

**Text TEMP (`dosounding.php`):**

1. Cron triggers `dosounding.php` every 20 min. Cron redirects all stdout/stderr to `/smartmet/logs/data/sounding-gts.log` — unlike the BUFR script, the PHP does not handle log redirection.
2. Read every file in `/smartmet/data/incoming/gts/sounding/`.
3. Regex-extract `TTAA` and `TTBB` blocks (one per report), trimming whitespace.
4. Group by `messages[location][date][type]`, sort by location → date → type, join with CRLF into `tmp/data/sounding/<timestamp>_gts_world_sounding.sqd.txt`.
5. Run `temp2qd -t …txt > …sqd` (arguments are `escapeshellarg`'d, exit code captured).
6. If the `.sqd` is non-empty: `pbzip2 -k` it (creates `.sqd.bz2` alongside), `rename` the `.sqd` into `/smartmet/data/gts/sounding/world/querydata/`, `rename` the `.bz2` into `/smartmet/editor/in/`.
7. Clean any leftovers matching `$OUTFILE*` from tmp.

**BUFR (`dosounding-bufr.sh`):**

1. Cron triggers `dosounding-bufr.sh` every 20 min. The script redirects stdout/stderr to `/smartmet/logs/data/sounding-bufr-gts.log` itself (via `exec &>` when `TERM=dumb`).
2. `bufrtoqd -C sounding -p 1005,Sounding --subsets "$IN/" "$OUTFILE"` reads everything in `/smartmet/data/incoming/gts/sounding-bufr/` and writes a `.sqd` to tmp. `--subsets` matters for messages carrying multiple soundings.
3. If the `.sqd` is non-empty: `pbzip2 -k` the file, `mv` the original to `/smartmet/data/gts/sounding-bufr/world/querydata/`, `mv` the `.bz2` to `/smartmet/editor/in/`.
4. An `EXIT` trap clears `$TMP/*.sqd*` so partial-failure runs don't leave stale tmp files.

The hourly cleaner keeps only the 2 most-recent `.sqd` and `_sounding_bufr.sqd` files in the output and editor dirs and deletes incoming files (both `sounding/` and `sounding-bufr/`) older than 7 days.

## Editing rules specific to this repo

- **Version bump = touch `Version:` and add a `%changelog` entry.** Date-based `YY.MM.DD` (e.g. `26.5.21`).
- **Hardcoded `/smartmet` paths in `dosounding.php`.** Unlike the bash scripts, the PHP does not fall back to `$HOME` when `/smartmet` is missing. Running locally for ad-hoc testing requires `mkdir -p /smartmet/...` (with sudo) or editing the constants. The BUFR script *does* have the `$HOME` fallback.
- **Both paths compress with `pbzip2`** (parallel bzip2). The uncompressed `.sqd` goes to the data tree; the `.bz2` goes to the editor inbox. The cleaner's `_sounding.sqd` and `_sounding_bufr.sqd` patterns match `.sqd.bz2` via substring, so a single rule covers both.
- **PHP `system()` is now `escapeshellarg`-guarded** but the wrapper itself still uses the shell (because of `>` redirection). Don't loosen the escaping if you add arguments derived from input data.
- **Don't `git push` straight to master.** PR-based flow is the FMI convention even though some earlier commits were direct-to-master.

## Building the RPM (FMI infrastructure)

Same shape as the sibling `smartmet-data-gts-synop`: the `%install` section expects sources under `%_topdir/SOURCES/smartmet-data-gts-sounding/`. Production builds happen in FMI's CI. Locally:

```sh
rpmbuild -ba smartmet-data-gts-sounding.spec
```

after staging both scripts into `~/rpmbuild/SOURCES/smartmet-data-gts-sounding/`. End users install via `yum install smartmet-data-gts-sounding`.

## macOS note

This package is RHEL-only (RPM, `/smartmet` paths, cron). It is **not** part of the macOS port described in the parent workspace's `CLAUDE.md`. Don't add `Makefile.mac` or `#ifdef __APPLE__` patches here.
