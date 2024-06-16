#!/bin/sh

ID=${1:-1}
 curl "http://localhost:8000/vendors/${ID}" ; echo
