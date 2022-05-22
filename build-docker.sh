#!/usr/bin/env bash

version=$(<version.txt)

docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v7 \
  -t rogryza/linkding-postgres:latest \
  -t rogryza/linkding-postgres:$version \
  --push .
