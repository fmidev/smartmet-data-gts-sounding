# SmartMet GTS sounding ingestion module

Reads incoming GTS WMO TEMP (FM-35) sounding bulletins and converts
them to SmartMet querydata (`.sqd`) for the data server and the editor.

## Install

```sh
yum install smartmet-data-gts-sounding
```

The package installs `dosounding.php` under
`/smartmet/run/data/sounding_gts/bin/` and registers it in cron every
20 minutes. An hourly cleaner keeps the two most recent outputs and
prunes incoming files older than 7 days.

## Configure the message switch

Route incoming GTS bulletins to the directory below based on WMO heading:

| Bulletin              | WMO heading | Drop files in                           |
|-----------------------|-------------|-----------------------------------------|
| GTS WMO TEMP (FM-35)  | `IU///`     | `/smartmet/data/incoming/gts/sounding`  |

## Output

The PHP script extracts `TTAA` and `TTBB` blocks from each incoming
file, deduplicates by (location, date, type), and runs `temp2qd` to
produce `/smartmet/data/gts/sounding/world/querydata/<timestamp>_gts_world_sounding.sqd`.
A copy of the same `.sqd` is dropped into `/smartmet/editor/in/` for
the editor. Cron output goes to `/smartmet/logs/data/sounding-gts.log`.

## Requires

`smartmet-qdtools` (provides `temp2qd`), `bzip2`, `php`.
