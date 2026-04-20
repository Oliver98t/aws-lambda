#!/bin/bash
env=$1
if [[ "$env" != "dev" && "$env" != "prod" ]]; then
  echo "env must be dev or prod"
  exit 1
fi

account_id=$(aws sts get-caller-identity --query "Account" --output text)
region="eu-west-2"
registry_url="$account_id.dkr.ecr.$region.amazonaws.com"
commit=$(git rev-parse --short HEAD)

aws ecr get-login-password --region eu-west-2 | docker login --username AWS \
--password-stdin $registry_url

# build/tag/push Response
response_tag="response-$env:$commit"
docker build -t $response_tag LambdaSrc/Response/
response_image_uri="$registry_url/$response_tag"
docker tag $response_tag $response_image_uri
docker push $registry_url/$response_tag

# build/tag/push Response
speechtotext_tag="speechtotext-$env:$commit"
docker build -t $speechtotext_tag LambdaSrc/SpeechToText/
speechtotext_image_uri=$registry_url/$speechtotext_tag
docker tag $speechtotext_tag $speechtotext_image_uri
docker push $registry_url/$speechtotext_tag

cd infrastructure
terraform init -reconfigure -backend-config=backend_$env.config
terraform apply -auto-approve \
    -var="environment=$env" \
    -var="Response_image_uri=$response_image_uri" \
    -var="SpeechToText_image_uri=$speechtotext_image_uri" \
    -var="aws_region=$region"
cd ..