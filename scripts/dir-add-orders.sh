#!/bin/sh
# shellcheck shell=dash

# shellcheck source=/dev/null
. /usr/local/etc/foowtforg

usage() {
  if [ -n "$1" ]; then
    echo "$1"
  fi
  abend "usage: $0 directory"
}

SD="$1"
[ -d "$SD" ] || usage "missing parameter directory"


# for ff in $(find ${SD} -name \*.json 2>/dev/null); do
#     echo "$ff"
# done
# shopt -s globstar nullglob
for file in "$SD"/*.json
do
  count=$(( count+=1 ))
  echo "Processing file: $file"
  scripts/order-upsert.sh "$file"
done
echo "Processed $count files"
