#!/bin/bash

docker build -t py_proxy -f Dockerfile .

docker tag py_proxy localhost:32000/py-proxy:k8s
docker push localhost:32000/py-proxy

