#!/bin/sh

 curl -d '{"name":"usps"}' -H "Content-Type: application/json" -X POST http://localhost:8000/shippers ; echo
 curl -d '{"name":"ups"}' -H "Content-Type: application/json" -X POST http://localhost:8000/shippers ; echo
 curl -d '{"name":"fedex"}' -H "Content-Type: application/json" -X POST http://localhost:8000/shippers ; echo
 curl -d '{"name":"DHL"}' -H "Content-Type: application/json" -X POST http://localhost:8000/shippers ; echo
