#!/bin/bash

set -e
set -v
set -x

# docker build
make image

echo $DOCKER_PW | base64 --decode -i > ${HOME}/password.txt
cat ~/password.txt | docker login --username ${DOCKER_USERNAME} --password-stdin

echo $GCLOUD_SERVICE_KEY | base64 --decode -i > ${HOME}/gcloud-service-key.json
gcloud auth activate-service-account --key-file ${HOME}/gcloud-service-key.json

echo "y" | gcloud auth configure-docker
docker push gcr.io/ou-reviews/stev-api:latest

gcloud --quiet config set project $PROJECT_NAME
gcloud --quiet config set run/platform managed
gcloud --quiet config set run/region us-central1 
# gcloud --quiet config set compute/zone ${CLOUDSDK_COMPUTE_ZONE}

gcloud beta run deploy stev-api --image gcr.io/ou-reviews/stev-api
# update
#gcloud compute instances update-container api-server \
#        --container-image docker.io/samjett/ou-reviews-api:latest
