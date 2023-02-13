#!/bin/bash
# Use this script to deploy a canary release - with a proxy, main and canary API

proxyImage="proxy"
proxyPort=8082

mainImage="mainapi"
mainPort=5000

canaryImage="canaryapi"
canaryPort=5001

# Using the current codebase build the canary api
docker build -t canaryapi ./

# Remove old images and deploy new ones
curl http://localhost:${proxyPort}/log/
docker stop "api"
docker rm "api"
docker run -d -e port=${proxyPort} -p ${proxyPort}:${proxyPort}/tcp --name="api" ${proxyImage}

curl http://localhost:${mainPort}/log/
docker stop "main"
docker rm "main"
docker run -d -e port=${mainPort} -p ${mainPort}:${mainPort}/tcp --name="main" ${mainImage}

curl http://localhost:${canaryPort}/log/
docker stop "canary"
docker rm "canary"
docker run -d -e port=${canaryPort} -p ${canaryPort}:${canaryPort}/tcp --name="canary" ${canaryImage}