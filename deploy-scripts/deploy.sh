#!/bin/bash
# Use this script to deploy a sole API release

name="api"
image="mainapi"
port=8082

curl http://localhost:${port}/log/
docker stop ${name}
docker rm ${name}
docker run -d -e port=${port} -p ${port}:${port}/tcp --name=${name} ${image}

# Clean up images from a possible canary release
mainPort=5000
canaryPort=5001
curl http://localhost:${mainPort}/log/
docker stop "main"
docker rm "main"
curl http://localhost:${canaryPort}/log/
docker stop "canary"
docker rm "canary"