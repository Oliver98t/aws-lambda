FROM python:3.12-slim

COPY . app/

WORKDIR /app

RUN useradd -ms /bin/bash oli98

# Install the specified packages
RUN pip install -r LambdaSrc/DevEnvRequirements.txt

# set up git for version control
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*
RUN git config --global user.name "Oliver98t"
RUN git config --global user.email "oli1998t@gmail.com"

# set up terraform
RUN apt-get update && apt-get install -y wget unzip
RUN wget https://releases.hashicorp.com/terraform/1.7.5/terraform_1.7.5_linux_amd64.zip 
RUN unzip terraform_1.7.5_linux_amd64.zip -d /usr/local/bin
RUN rm terraform_1.7.5_linux_amd64.zip

USER oli98
# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "sleep", "infinity" ]