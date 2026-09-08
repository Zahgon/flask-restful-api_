#!/usr/bin/env bash
set -e

docker build -t fastapi-api-test .
docker run --rm -p 56733:5000 fastapi-api-test
