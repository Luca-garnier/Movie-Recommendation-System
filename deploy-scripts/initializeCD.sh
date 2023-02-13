
canaryImage = "canaryapi"
mainImage = "mainapi"
proxyImage = "proxy"


docker build -t ${proxyImage} ../api/proxy
docker build -t ${mainImage} ../