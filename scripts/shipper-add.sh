#!/bin/sh

if [ -n "$1" ]; then
  curl -d "{\"name\":\"$1\"}" \
  -H "Content-Type: application/json" \
  -X POST http://localhost:8000/shippers/add
  echo
else
  echo "Usage: $0 shipper"
fi
