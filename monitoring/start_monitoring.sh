#!/bin/bash

echo "Killing old docker items ..."

docker container kill online-evaluation &>/dev/null
docker container kill node-exporter &>/dev/null
docker container kill prometheus &>/dev/null

docker container rm online-evaluation &>/dev/null
docker container rm node-exporter &>/dev/null
docker container rm prometheus &>/dev/null

docker image rm  kill node-exporter &>/dev/null
docker image rm  kill prometheus &>/dev/null
docker image rm online-evaluation &>/dev/null

sleep 1

echo "Running node-exporter ..."
docker run --name node-exporter -d -p 9100:9100 --user $(id -u):$(id -g) prom/node-exporter
sleep 1

echo "Running alertmanager ..."
docker run --name alertmanager -d -p 9093:9093 --user $(id -u):$(id -g)  -v "/home/team-3/Team3/monitoring/alertmanager:/config" prom/alertmanager
sleep 1

echo "Running prometheus ..."
docker run --name prometheus -d -p 9090:9090 --user root:root -v "/home/team-3/Team3/monitoring/prometheus:/etc/prometheus" prom/prometheus
sleep 1

echo "Building online evaluation ..."
docker build -f /home/team-3/Team3/monitoring/Dockerfile /home/team-3/Team3/monitoring -t online-evaluation &>/dev/null
sleep 1

echo "Running online evaluation ..."
docker run --name online-evaluation -d online-evaluation

docker network connect recommenderNet online-evaluation
docker network connect recommenderNet prometheus
docker network connect recommenderNet node-exporter
docker network connect recommenderNet alertmanager
