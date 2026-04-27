#!/bin/bash
env=$1
if [[ "$env" != "dev" && "$env" != "prod" ]]; then
  echo "env must be dev or prod"
  exit 1
fi

auto=$2
if [[ "$auto" != "auto-yes" && "$auto" != "auto-no" ]]; then
  echo "auto must be set"
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
# TODO add tag delete
build_tag_push()
{
    src=$1
    docker_repo=$2
    tag="${docker_repo}:${commit}"
    echo "Building $tag from $src" >&2
    docker build -t $tag $src >&2
    #aws ecr batch-delete-image --repository-name $docker_repo --image-ids imageTag=$commit
    image_uri="$registry_url/$tag"
    docker tag $tag $image_uri >&2
    docker push $registry_url/$tag >&2
    echo "$image_uri"
}

get_response_image_uri=$(build_tag_push "lambda_src/get_response/" "get_response_$env")
response_image_uri=$(build_tag_push "lambda_src/response/" "response_$env")
speechtotext_image_uri=$(build_tag_push "lambda_src/speech_to_text/" "speech_to_text_$env") 

cd infrastructure
terraform init -reconfigure \
    -backend-config="bucket=$BUCKET" \
    -backend-config="key=$KEY" \
    -backend-config="region=$REGION" \
    -backend-config="encrypt=$ENCRYPT"

if [ "$auto" = "auto-yes" ]; then
    terraform apply -auto-approve \
        -var="environment=$env" \
        -var="get_response_image_uri=$get_response_image_uri" \
        -var="response_image_uri=$response_image_uri" \
        -var="speech_to_text_image_uri=$speechtotext_image_uri" \
        -var="aws_region=$region"
else
    terraform apply \
        -var="environment=$env" \
        -var="get_response_image_uri=$get_response_image_uri" \
        -var="response_image_uri=$response_image_uri" \
        -var="speech_to_text_image_uri=$speechtotext_image_uri" \
        -var="aws_region=$region"
fi
cd ..