#!/bin/sh
# shellcheck shell=dash

if [ -n "$1" ]; then
  if [ -f "$1" ]; then
    curl -d "@$1" \
    -H "Content-Type: application/json" \
    -X POST http://localhost:8000/orders/upsert
    RC=$?
    echo
  else
    echo "File not found: $1"
    RC=2
  fi
else
  echo "Usage: $0 json_file"
  RC=1
fi

echo "exitting with exit code: $RC"
exit "$RC"
