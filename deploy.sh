#!/bin/bash
env=$1
if [[ "$env" != "dev" && "$env" != "prod" ]]; then
  echo "env must be dev or prod"
  exit 1
fi

# backend config
BUCKET=ainterview-state-files   
KEY=state/terraform_$env.tfstate      
REGION=eu-west-2                     
ENCRYPT=true

account_id=$(aws sts get-caller-identity --query "Account" --output text)
region="eu-west-2"
registry_url="$account_id.dkr.ecr.$region.amazonaws.com"
commit=$(git rev-parse --short HEAD)

aws ecr get-login-password --region eu-west-2 | docker login --username AWS \
--password-stdin $registry_url

# build/tag/push Response
response_tag="response-$env:$commit"
docker build -t $response_tag lambda_src/response/
response_image_uri="$registry_url/$response_tag"
docker tag $response_tag $response_image_uri
docker push $registry_url/$response_tag

# build/tag/push SpeechToText
speechtotext_tag="speech_to_text-$env:$commit"
docker build -t $speechtotext_tag lambda_src/speech_to_text/
speechtotext_image_uri=$registry_url/$speechtotext_tag
docker tag $speechtotext_tag $speechtotext_image_uri
docker push $registry_url/$speechtotext_tag

cd infrastructure
terraform init -reconfigure \
    -backend-config="bucket=$BUCKET" \
    -backend-config="key=$KEY" \
    -backend-config="region=$REGION" \
    -backend-config="encrypt=$ENCRYPT"

terraform apply $test \
    -var="environment=$env" \
    -var="response_image_uri=$response_image_uri" \
    -var="speech_to_text_image_uri=$speechtotext_image_uri" \
    -var="aws_region=$region"
cd ..