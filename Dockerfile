FROM python:3.12-slim

COPY . app/

WORKDIR /app

# Install the specified packages
RUN pip install -r LambdaSrc/DevEnvRequirements.txt
 
# Install git for version control
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# set up terraform
RUN apt-get update && apt-get install -y wget unzip \
  && wget https://releases.hashicorp.com/terraform/1.7.5/terraform_1.7.5_linux_amd64.zip \
  && unzip terraform_1.7.5_linux_amd64.zip -d /usr/local/bin \
  && rm terraform_1.7.5_linux_amd64.zip

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "sleep", "infinity" ]