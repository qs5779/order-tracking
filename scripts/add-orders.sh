#!/bin/sh
# shellcheck shell=dash

# shellcheck source=/dev/null
. /usr/local/etc/foowtforg

usage() {
  if [ -n "$1" ]; then
    echo "$1"
  fi
  abend "usage: $0 directory start [end]"
}

SD="$1"
[ -d "$SD" ] || usage "missing parameter directory"

START="$2"
[ -n "$START" ] || usage "missing parameter start"
END="$3"
[ -z "$END" ] && END="$START"

while [ "$START" -le "$END" ]; do
  SRC="${SD}/${START}.json"
  if [ -f "$SRC" ]; then
    echo "Posting $SRC"
    scripts/order-upsert.sh "$SRC"
    RC=$?
    if [ "$RC" != "0" ]; then
      exit $RC
    fi
  else
    echo "Skipping file not found $SRC"
  fi
  START=$((START+1))
done
