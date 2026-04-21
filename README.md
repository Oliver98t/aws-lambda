# AInterview Backend

This repository contains the backend infrastructure and Lambda source code for the AInterview project. It is designed to run on AWS using Docker containers and Terraform for infrastructure as code.

## Project Structure

- **deploy.sh**: Bash script to build, tag, and push Lambda container images to AWS ECR and deploy infrastructure using Terraform.
- **Dockerfile**: Builds a development environment with Python, Terraform, and required dependencies.
- **docker-compose.yml**: Defines a development container for local use.
- **setup_venv.sh**: Script to set up a Python virtual environment and install development dependencies.
- **lambda_src/**: Source code for Lambda functions.
  - **dev_env_requirements.txt**: Shared Python requirements for development.
  - **response/**: Lambda function for generating AI responses.
    - `index.py`: Main handler and logic for processing SQS messages and generating responses using Bedrock.
    - `requirements.txt`: Function-specific dependencies.
    - `test/`: Unit tests for the Response Lambda.
  - **speech_to_text/**: Lambda function for transcribing audio.
    - `index.py`: Main handler and logic for transcribing audio and sending results to SQS.
    - `requirements.txt`: Function-specific dependencies.
    - `test/`: Unit tests for the SpeechToText Lambda.
- **infrastructure/**: Terraform code for AWS infrastructure.
  - `main.tf`, `variables.tf`, `outputs.tf`, `terraform.tf`, `terraform.tfvars`, `backend.config`: Core Terraform configuration and state management.
  - **modules/**: Reusable Terraform modules for Lambda, SQS, etc.

## Main Components

### Lambda Functions
- **speech_to_text**: Receives API requests, transcribes audio from S3, and sends transcription to SQS.
- **response**: Consumes SQS messages, generates AI responses using Bedrock, and stores results in DynamoDB or logs them.

### Infrastructure
- **Terraform**: Provisions AWS Lambda (container image), SQS queue, and supporting resources. State is managed in S3.
- **Docker**: Used for local development and building Lambda container images.

## Setup & Deployment

1. **Clone the repository**
2. **Set up AWS credentials** (ensure you have access to ECR, Lambda, SQS, S3, DynamoDB)
3. **Build and deploy**:
   ```bash
  ./deploy.sh
   ```
   This will:
   - Build and push Lambda images to ECR
   - Deploy infrastructure with Terraform

4. **Local Development**:
   - Use `docker-compose up` to start a dev container
  - Use `setup_venv.sh` to set up a local Python environment

## Testing
- Each Lambda function has unit tests in its `test/` directory.
- Run tests with `pytest` inside the appropriate directory or container.

## Requirements
- Python 3.12+
- Docker
- AWS CLI
- Terraform >= 1.2

## Notes
- Update `terraform.tfvars` and `backend.config` with your environment details as needed.
- Ensure AWS credentials are configured for CLI and Docker to access ECR and deploy resources.

---

For more details, see the code in each subdirectory and the Terraform module documentation.