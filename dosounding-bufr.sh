#!/bin/bash
#
# Finnish Meteorological Institute / Mikko Rauhala (2018-)
#
# SmartMet Data Ingestion Module for GTS BUFR Sounding Observations
#

set -uo pipefail

export BUFR_TABLES=/usr/share/libecbufr
if [ -d /smartmet ]; then
    BASE=/smartmet
else
    BASE=$HOME
fi

IN=$BASE/data/incoming/gts/sounding-bufr
OUT=$BASE/data/gts
EDITOR=$BASE/editor/in
TMP=$BASE/tmp/data/sounding
TIMESTAMP=$(date +%Y%m%d%H%M)
LOGFILE=$BASE/logs/data/sounding-bufr-gts.log

OUTFILE=$TMP/${TIMESTAMP}_gts_world_sounding_bufr.sqd

mkdir -p "$TMP"
mkdir -p "$OUT/sounding-bufr/world/querydata"
trap 'rm -f "$TMP"/*.sqd*' EXIT

# Use log file if not run interactively
if [ "${TERM:-}" = "dumb" ]; then
    exec &> "$LOGFILE"
fi

echo "IN:  $IN"
echo "OUT: $OUT"
echo "TMP: $TMP"
echo "Sounding File: $OUTFILE"

# Do sounding data
bufrtoqd -C sounding -p 1005,Sounding --subsets "$IN/" "$OUTFILE"

if [ -s "$OUTFILE" ]; then
    pbzip2 -k "$OUTFILE"
    mv -f "$OUTFILE" "$OUT/sounding-bufr/world/querydata/"
    mv -f "${OUTFILE}.bz2" "$EDITOR"
fi
