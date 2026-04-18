#!/bin/bash

env="dev"
account_id=$(aws sts get-caller-identity --query "Account" --output text)
region="eu-west-2"
registry_url="$account_id.dkr.ecr.$region.amazonaws.com"
commit=$(git rev-parse --short HEAD)

aws ecr get-login-password --region eu-west-2 | docker login --username AWS \
--password-stdin $registry_url

# remove old docker images locally
docker rmi $(docker images | grep -E "response|speechtotext" | awk '{print $2}') --force

# build/tag/push Response
response_tag="response-$env:$commit"
docker build -t $response_tag LambdaSrc/Response/
docker tag $response_tag $registry_url/$response_tag
docker push $registry_url/$response_tag

# build/tag/push Response
speechtotext_tag="speechtotext-$env:$commit"
docker build -t $speechtotext_tag LambdaSrc/SpeechToText/
docker tag $speechtotext_tag $registry_url/$speechtotext_tag
docker push $registry_url/$speechtotext_tag
