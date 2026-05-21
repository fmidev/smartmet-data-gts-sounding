# SmartMet GTS sounding ingestion module

Reads incoming GTS WMO TEMP (FM-35/36/37 text) and BUFR sounding
bulletins and converts them to SmartMet querydata (`.sqd`) for the
data server and the editor.

## Install

```sh
yum install smartmet-data-gts-sounding
```

The package installs `dosounding.php` and `dosounding-bufr.sh` under
`/smartmet/run/data/sounding_gts/bin/` and registers both in cron every
20 minutes. An hourly cleaner keeps the two most recent outputs for
each format and prunes incoming files older than 7 days.

## Configure the message switch

Route incoming GTS bulletins to the directories below based on WMO heading:

| Format                                   | WMO headings                                              | Drop files in                                |
|------------------------------------------|-----------------------------------------------------------|----------------------------------------------|
| TAC TEMP (FM-35/36/37), parts A & B      | `US///` `UK///` `UF///` `UG///` `UA///` `UB///`           | `/smartmet/data/incoming/gts/sounding`       |
| BUFR upper-air                           | `IU///`                                                   | `/smartmet/data/incoming/gts/sounding-bufr`  |

`dosounding.php` only extracts `TTAA` (part A) and `TTBB` (part B)
blocks; `temp2qd` (via `NFmiTEMPCode`) recognises three station types
in the body's `MiMiMjMj` identifier:

- **FM-35** fixed land — default. Headers `US///` (A), `UK///` (B).
- **FM-36** TEMP SHIP — body starts with `UU??`. Headers `UF///`, `UG///`.
- **FM-37** TEMP MOBIL — body starts with `II??`. Headers `UA///`, `UB///`.

**Not supported:** FM-38 (TEMP DROP, headers `UR///` `UT///`) has no
dedicated handling in `NFmiTEMPCode` — without `II`/`UU` in the body
it would be parsed as fixed-station TEMP, which mis-handles the
dropsonde altitude scheme. Parts C and D (headers
`UE`/`UM`/`UH`/`UI`/`UC`/`UD`/`UW`/`UX`) are not extracted either.

## Output

- **Text TEMP:** `dosounding.php` extracts `TTAA` and `TTBB` blocks from each incoming file, deduplicates by (location, date, type), runs `temp2qd` to produce `<timestamp>_gts_world_sounding.sqd`, then `pbzip2 -k`-compresses it. The uncompressed `.sqd` lands in `/smartmet/data/gts/sounding/world/querydata/` and the `.bz2` in `/smartmet/editor/in/`. Cron output goes to `/smartmet/logs/data/sounding-gts.log`.
- **BUFR:** `dosounding-bufr.sh` runs `bufrtoqd -C sounding --subsets` over the incoming directory, `pbzip2 -k`-compresses the result, and distributes the `.sqd` to `/smartmet/data/gts/sounding-bufr/world/querydata/` and the `.bz2` to `/smartmet/editor/in/`. Logs to `/smartmet/logs/data/sounding-bufr-gts.log`.

## Requires

`smartmet-qdtools` (provides `temp2qd`, `bufrtoqd`), `pbzip2`, `php`.
