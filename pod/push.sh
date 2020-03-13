#!/bin/bash

docker build -t init-networking -f Dockerfile .

docker tag init-networking localhost:32000/init-networking:k8s
docker push localhost:32000/init-networking

