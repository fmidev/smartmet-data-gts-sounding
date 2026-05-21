# SmartMet GTS sounding ingestion module

Reads incoming GTS WMO TEMP (FM-35, text) and BUFR sounding bulletins
and converts them to SmartMet querydata (`.sqd`) for the data server
and the editor.

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

| Bulletin                       | WMO heading | Drop files in                                |
|--------------------------------|-------------|----------------------------------------------|
| GTS WMO TEMP (FM-35, text)     | `IU///`     | `/smartmet/data/incoming/gts/sounding`       |
| GTS WMO upper-air BUFR         | `IU///`     | `/smartmet/data/incoming/gts/sounding-bufr`  |

Both formats share the WMO designator `IU///`; routing to the two
incoming directories is up to the local message-switch configuration.

## Output

- **Text TEMP:** `dosounding.php` extracts `TTAA` and `TTBB` blocks from each incoming file, deduplicates by (location, date, type), and runs `temp2qd` to produce `/smartmet/data/gts/sounding/world/querydata/<timestamp>_gts_world_sounding.sqd`. A copy is dropped into `/smartmet/editor/in/`. Cron output goes to `/smartmet/logs/data/sounding-gts.log`.
- **BUFR:** `dosounding-bufr.sh` runs `bufrtoqd -C sounding --subsets` over the incoming directory, writing `<timestamp>_gts_world_sounding_bufr.sqd` to `/smartmet/data/gts/sounding-bufr/world/querydata/`, plus a `pbzip2`-compressed copy in `/smartmet/editor/in/`. Logs to `/smartmet/logs/data/sounding-bufr-gts.log`.

## Requires

`smartmet-qdtools` (provides `temp2qd`, `bufrtoqd`), `bzip2`, `pbzip2`, `php`.
