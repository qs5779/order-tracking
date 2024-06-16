#!/bin/sh

if [ -n "$1" ]; then
  curl -d "{\"name\":\"$1\"}" \
  -H "Content-Type: application/json" \
  -X POST http://localhost:8000/vendors/add
  echo
else
  echo "Usage: $0 vendor"
fi
