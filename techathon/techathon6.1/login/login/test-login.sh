#!/bin/sh
# Simple curl test for the login endpoint
curl -s -X POST -H "Content-Type: application/json" -d '{"username":"admin","password":"vuiuiuiuiuiuiuiuiuiui bguuuuuuuuuuuuuutgys ry"}' http://localhost:3000/login | jq
