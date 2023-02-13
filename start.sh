#!/bin/bash

app="flask-api"

docker container stop ${app}
docker container rm ${app}
docker build -t ${app} .
docker run -d -p 8082:8082/tcp --name=${app} -v $PWD:/app --user $(id -u):$(id -g) ${app}
docker network connect recommenderNet flask-api